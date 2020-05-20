import getpass
import http
import logging
import os
import posixpath
from typing import List, Optional
import urllib.parse

import requests
# For backward compatible HTTPError
import urllib3.exceptions

from .config import Config, parseClassName
from .config import ConfigOptions
from .config import parseURLDomain
from .constants import *
from .sbolerror import SBOLError
from .sbolerror import SBOLErrorCode
from .identified import Identified


class PartShop:
    """A class which provides an API front-end for
    online bioparts repositories"""

    def __init__(self, url, spoofed_url=''):
        """

        :param url: The URL of the online repository (as a str)
        :param spoofed_url:
        """
        # initialize member variables
        self.resource = self._validate_url(url, 'resource')
        self.user = ''
        self.key = ''
        self.spoofed_resource = self._validate_url(spoofed_url, 'spoofed')

    def _validate_url(self, url, url_name):
        # This feels like a weak validation
        # Should we verify that it is a string?
        #   [1, 2, 3] will pass this test, and surely break something else later.
        # Should we use urllib.parse.urlparse?
        #   It doesn't do a whole lot, but catches some things this code doesn't
        if len(url) > 0 and url[-1] == '/':
            msg = ('PartShop initialization failed. The {} URL '
                   + 'should not contain a terminal backlash')
            msg = msg.format(url_name)
            raise SBOLError(msg, SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT)
        return url

    @property
    def logger(self):
        logger = logging.getLogger('sbol2')
        if not logger.hasHandlers():
            # If there are no handlers, nobody has initialized
            # logging.  Configure logging here so we have a chance of
            # seeing the messages.
            logging.basicConfig()
        return logger

    def count(self):
        """Return the count of objects contained in a PartShop"""
        raise NotImplementedError('Not yet implemented')

    def spoof(self, spoofed_url):
        self.spoofed_resource = self._validate_url(spoofed_url, 'spoofed')

    def sparqlQuery(self, query):
        """
        Issue a SPARQL query
        :param query: the SPARQL query
        :return: the HTTP response object
        """
        endpoint = parseURLDomain(self.resource) + '/sparql'
        if self.spoofed_resource == '':
            resource = self.resource
        else:
            resource = self.spoofed_resource
        p = query.find('WHERE')
        if p != -1:
            from_clause = ' FROM <' + parseURLDomain(resource) + \
                          '/user/' + self.user + '> '
            query = query[:p].rstrip() + from_clause + query[p:].lstrip()
        headers = {'X-authorization': self.key, 'Accept': 'application/json'}
        params = {'query': query}  # should handle encoding the query
        if Config.getOption(ConfigOptions.VERBOSE.value) is True:
            self.logger.debug('Issuing SPARQL: ' + query)
        response = requests.get(endpoint, headers=headers, params=params)
        if not response:
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST,
                            response)
        return response

    def pull(self, uris, doc, recursive=True):
        """Retrieve an object from an online resource
        :param uris: A list of SBOL objects you want to retrieve,
        or a single SBOL object URI
        :param doc: A document to add the data to
        :param recursive: Whether the GET request should be recursive
        :return: nothing (doc parameter is updated, or an exception is thrown)
        """
        # IMPLEMENTATION NOTE: rdflib.Graph.parse() actually lets you
        # pass a URL as an argument. I decided to not use this method,
        # because I couldn't find an easy way to get the response
        # code, set HTTP headers, etc. In addition, I would need
        # to use requests for submitting new SBOL data anyway.
        endpoints = []
        if type(uris) is str:
            endpoints.append(uris)
        elif type(uris) is list:
            endpoints = uris
        else:
            raise TypeError('URIs must be str or list. Found: ' + str(type(uris)))
        for uri in endpoints:
            try:
                query = self._uri2url(uri)
            except SBOLError as err:
                if err.error_code() == SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT:
                    # Assume user has only specified displayId
                    query = self.resource + '/' + uri
                else:
                    raise
            query += '/sbol'
            if not recursive:
                query += 'nr'
            if Config.getOption(ConfigOptions.VERBOSE.value):
                self.logger.debug('Issuing GET request ' + query)
            # Issue GET request
            response = requests.get(query,
                                    headers={'X-authorization': self.key,
                                             'Accept': 'text/plain'})
            if response.status_code == 404:
                raise SBOLError('Part not found. Unable to pull: ' + query,
                                SBOLErrorCode.SBOL_ERROR_NOT_FOUND,)
            elif response.status_code == 401:
                raise SBOLError('Please log in with valid credentials',
                                SBOLErrorCode.SBOL_ERROR_HTTP_UNAUTHORIZED,)
            elif not response:
                raise SBOLError(response, SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST)
            # Add content to document
            serialization_format = Config.getOption('serialization_format')
            Config.setOption('serialization_format', serialization_format)
            doc.readString(response.content)
            doc.resource_namespaces.add(self.resource)

    def submit(self, doc, collection='', overwrite=0):
        """Submit a SBOL Document to SynBioHub
        :param doc: The Document to submit
        :param collection: The URI of a SBOL Collection to which the Document
        contents will be uploaded
        :param overwrite: An integer code: 0 (default) - do not overwrite,
        1 - overwrite, 2 - merge
        :return: the HTTP response object
        """
        if collection == '':
            # If a Document is submitted as a new collection,
            # then Document metadata must be specified
            if len(doc.displayId) == 0 or len(doc.name) == 0 \
                    or len(doc.description) == 0:
                raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT,
                                'Cannot submit Document. The Document must be '
                                'assigned a displayId, name, and ' +
                                'description for upload.')
        else:
            if len(self.spoofed_resource) > 0 and self.resource in collection:
                # Correct collection URI in case a spoofed resource is being used
                collection = collection.replace(self.resource,
                                                self.spoofed_resource)
            if Config.getOption(ConfigOptions.VERBOSE.value) is True:
                self.logger.info('Submitting Document to an existing collection: %s',
                                 collection)
        # if Config.getOption(ConfigOptions.SERIALIZATION_FORMAT.value) == 'rdfxml':
        #     self.addSynBioHubAnnotations(doc)
        files = {}
        if len(doc.displayId) > 0:
            files['id'] = (None, doc.displayId)
        if len(doc.version) > 0:
            files['version'] = (None, doc.version)
        if doc.name and len(doc.name) > 0:
            files['name'] = (None, doc.name)
        if doc.description and len(doc.description) > 0:
            files['description'] = (None, doc.description)
        citations = ''
        for citation in doc.citations:
            citations += citation + ','
        citations = citations[0:-1]  # chop off final comma
        files['citations'] = (None, citations)
        keywords = ''
        for kw in doc.keywords:
            keywords += kw + ','
        keywords = keywords[0:-1]
        files['keywords'] = (None, keywords)
        files['overwrite_merge'] = (None, str(overwrite))
        files['user'] = (None, self.key)
        files['file'] = ('file', doc.writeString(), 'text/xml')
        if collection != '':
            files['rootCollections'] = (None, collection)
        # Send POST request
        # print(files)
        response = requests.post(self.resource + '/submit',
                                 files=files,
                                 headers={'Accept': 'text/plain',
                                          'X-authorization': self.key})
        # print(response.text)
        if response:
            return response
        elif response.status_code == 401:
            # Raise a urllib3 HTTPError exception to be backward compatible with pySBOL
            raise urllib3.exceptions.HTTPError('You must login with valid credentials '
                                               'before submitting')
        else:
            # Raise a urllib3 HTTPError exception to be backward compatible with pySBOL
            raise urllib3.exceptions.HTTPError('HTTP post request failed with: ' +
                                               str(response.status_code) +
                                               ' - ' + str(response.content))

    def _uri2url(self, uri):
        """Converts an SBOL URI to a URL for running queries to a SynBioHub
        endpoint.

        """
        if self.resource in uri:
            return uri
        if parseURLDomain(self.resource) in uri:
            return uri
        if self.spoofed_resource and self.spoofed_resource in uri:
            return uri.replace(self.spoofed_resource, self.resource)
        msg = ('{} does not exist in the resource namespace')
        msg = msg.format(uri)
        raise SBOLError(msg, SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT)

    def remove(self, uri):
        query = self._uri2url(uri)
        url = '{}/remove'.format(query)
        headers = {
            'X-authorization': self.key,
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        if response.ok:
            return True
        if response.status_code == 401:
            # TODO: Is there a symbol we can use instead of 401?
            msg = 'You must login with valid credentials before removing'
            raise SBOLError(msg, SBOLErrorCode.SBOL_ERROR_HTTP_UNAUTHORIZED)
        # Not sure what went wrong
        msg = 'Unknown error: ' + response
        raise SBOLError(msg, SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST)

    def login(self, user_id, password=''):
        """In order to submit to a PartShop, you must login first.
        Register on [SynBioHub](http://synbiohub.org) to
        obtain account credentials.
        :param user_id: User ID
        :param password: User password
        :return: the HTTP response object
        """
        self.user = user_id
        if password is None or password == '':
            password = getpass.getpass()
        response = requests.post(
            parseURLDomain(self.resource) + '/remoteLogin',
            data={'email': user_id, 'password': password},
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        if not response:
            msg = 'Login failed due to an HTTP error: {}'
            msg = msg.format(response)
            raise SBOLError(msg, SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST)
        self.key = response.content.decode('utf-8')
        return response

    def getKey(self):
        return self.key

    def getURL(self):
        return self.resource

    # For backward compatibility with pySBOL
    def getUser(self):
        return self.user

    # For backward compatibility with pySBOL
    def getSpoofedURL(self):
        return self.spoofed_resource

    # def addSynBioHubAnnotations(self, doc):
    #     doc.addNamespace("http://wiki.synbiohub.org/wiki/Terms/synbiohub#", "sbh")
    #     for id, toplevel_obj in doc.SBOLObjects:
    #         toplevel_obj.apply(None, None)  # TODO

    def attachFile(self, top_level_uri, filepath):
        """Attach a file to an object in SynBioHub.

        Returns None if successful.

        Raises SBOLError with code SBOL_ERROR_HTTP_UNAUTHORIZED if it
        there is an HTTP Unauthorized response.

        Raises SBOLError with code SBOL_ERROR_BAD_HTTP_REQUEST on any
        other HTTP error. The actual status code is embedded in the
        string message.

        """
        # Expand User
        filepath = os.path.expanduser(filepath)
        # HTTP request headers
        headers = {
            'Accept': 'text/plain',
            'X-authorization': self.key
        }
        url = posixpath.join(top_level_uri, 'attach')
        with open(filepath, 'rb') as fp:
            files = {'file': fp}
            response = requests.post(url, headers=headers, files=files)

        if response.ok:
            if Config.getOption(ConfigOptions.VERBOSE.value) is True:
                print(response.text)
            return
        if response.status_code == http.HTTPStatus.UNAUTHORIZED:
            # HTTP 401
            msg = 'You must login with valid credentials before attaching a file'
            raise SBOLError(msg, SBOLErrorCode.SBOL_ERROR_HTTP_UNAUTHORIZED)
        # Not sure what went wrong
        msg = 'HTTP Error code {} trying to attach file.'
        msg = msg.format(response.status_code)
        raise SBOLError(msg, SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST)

    def _make_search_item(self, item: dict) -> Identified:
        obj = Identified()
        obj.identity = item['uri']
        obj.displayId = item['displayId']
        obj.name = item['name']
        obj.description = item['description']
        obj.version = item['version']
        return obj

    def _search(self, url: str) -> List[Identified]:
        """Given a URL, perform the search and parse the results.
        The URL is formed by one of the other search methods: search_exact,
        search_general, and search_advanced.
        """
        # Login is optional
        headers = {'Accept': 'text/plain'}
        if self.key:
            headers['X-authorization'] = self.key

        self.logger.info('search query: %s', url)
        response = requests.get(url, headers=headers)
        if not response:
            # Something went wrong
            raise SBOLError(response, SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST)
        # Everything looks good, parse and return the results
        return [self._make_search_item(item) for item in (response.json())]

    def search_general(self, search_text: str,
                       object_type: Optional[str] = SBOL_COMPONENT_DEFINITION,
                       offset: int = 0, limit: int = 25) -> List[Identified]:
        # See https://synbiohub.github.io/api-docs/#search-metadata
        search_url = parseURLDomain(self.resource)
        query = dict(objectType=parseClassName(object_type))
        query = urllib.parse.urlencode(query)
        search_text = urllib.parse.quote(search_text)
        params = dict(offset=offset, limit=limit)
        params = urllib.parse.urlencode(params)
        query_url = f'{search_url}/search/{query}&{search_text}/?{params}'
        return self._search(query_url)

    def search_exact(self, search_text: str,
                     object_type: Optional[str] = SBOL_COMPONENT_DEFINITION,
                     property_uri: Optional[str] = None,
                     offset: int = 0, limit: int = 25) -> List[Identified]:
        # See https://synbiohub.github.io/api-docs/#search-metadata
        search_url = parseURLDomain(self.resource)
        query = dict(objectType=parseClassName(object_type))
        if search_text.startswith('http'):
            search_text = f"<{search_text}>"
        else:
            search_text = f"'{search_text}'"
        query[parseClassName(property_uri)] = search_text
        query = urllib.parse.urlencode(query)
        params = dict(offset=offset, limit=limit)
        params = urllib.parse.urlencode(params)
        query_url = f'{search_url}/search/{query}&/?{params}'
        return self._search(query_url)

    def search(self, search_text: str,
               object_type: Optional[str] = SBOL_COMPONENT_DEFINITION,
               property_uri: Optional[str] = None,
               offset: int = 0, limit: int = 25) -> List[Identified]:
        # if search_text is a SearchQuery, dispatch to search_advanced

        # if property_uri is not specified, do a general search
        if property_uri is None:
            return self.search_general(search_text, object_type, offset,
                                       limit)
        # property_uri is specified, do an exact search
        return self.search_exact(search_text, object_type, property_uri,
                                 offset, limit)
