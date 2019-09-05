import requests
import os
import logging
from logging.config import fileConfig
from sbol.sbolerror import *
from sbol.constants import *
from sbol.config import Config, ConfigOptions, parseURLDomain
import getpass

LOGGING_CONFIG = 'logging_config.ini'


class PartShop:
    """A class which provides an API front-end for online bioparts repositories"""

    def __init__(self, url, spoofed_url=''):
        """

        :param url: The URL of the online repository (as a str)
        :param spoofed_url:
        """
        self.logger = logging.getLogger(__name__)
        # set up logger
        if os.path.exists(LOGGING_CONFIG):
            fileConfig(LOGGING_CONFIG)
        else:
            self.logger.setLevel(logging.INFO)
        # initialize member variables
        self.resource = url
        self.key = ''
        self.spoofed_resource = spoofed_url
        if len(url) > 0 and url[-1] == '/':
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT,
                            'PartShop initialization failed. The resource URL should not contain a terminal backlash')
        if len(spoofed_url) > 0 and spoofed_url[-1] == '/':
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT,
                            'PartShop initialization failed. The spoofed URL should not contain a terminal backslash')

    def count(self):
        """Return the count of objects contained in a PartShop"""
        raise NotImplementedError('Not yet implemented')

    def sparqlQuery(self, query):
        """Issue a SPARQL query"""
        raise NotImplementedError('Not yet implemented')

    def pull(self, uris, doc, recursive=True):
        """Retrieve an object from an online resource
        :param uris: A list of SBOL objects you want to retrieve, or a single SBOL object URI
        :param doc: A document to add the data to
        :param recursive: Whether the GET request should be recursive
        :return:
        """
        # IMPLEMENTATION NOTE: rdflib.Graph.parse() actually lets you pass a URL as an argument.
        # I decided to not use this method, because I couldn't find an easy way to get the response
        # code, set HTTP headers, etc. In addition, I would need to use requests for submitting
        # new SBOL data anyway.
        endpoints = []
        if type(uris) is str:
            endpoints.append(uris)
        elif type(uris) is list:
            endpoints = uris
        else:
            raise TypeError('URIs must be str or list. Found: ' + str(type(uris)))
        for uri in endpoints:
            if self.resource in uri:  # user has specified full URI
                query = uri
            elif len(self.spoofed_resource) > 0 and self.resource in uri:
                query = uri.replace(self.resource, self.spoofed_resource)
            else:
                query = self.resource + '/' + uri  # Assume user has only specified displayId
            query += '/sbol'
            if not recursive:
                query += 'nr'
            if Config.getOption(ConfigOptions.VERBOSE.value):
                self.logger.debug('Issuing GET request ' + query)
            # Issue GET request
            response = requests.get(query,
                                    headers={'X-authorization': self.key, 'Accept': 'text/plain'})
            if response.status_code == 404:
                raise SBOLError(SBOLErrorCode.SBOL_ERROR_NOT_FOUND, 'Part not found. Unable to pull: ' + query)
            elif response.status_code == 401:
                raise SBOLError(SBOLErrorCode.SBOL_ERROR_HTTP_UNAUTHORIZED, 'Please log in with valid credentials')
            elif not response:
                raise SBOLError(SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST, response)
            # Add content to document
            serialization_format = Config.getOption('serialization_format')
            Config.setOption('serialization_format', serialization_format)
            doc.readString(response.content)
            doc.resource_namespaces.add(self.resource)

    def submit(self, doc, collection='', overwrite=0):
        """Submit a SBOL Document to SynBioHub
        :param doc: The Document to submit
        :param collection: The URI of a SBOL Collection to which the Document contents will be uploaded
        :param overwrite: An integer code: 0 (default) - do not overwrite, 1 - overwrite, 2 - merge
        :return:
        """
        if collection == '':
            # If a Document is submitted as a new collection, then Document metadata must be specified
            if len(doc.displayId) == 0 or len(doc.name) == 0 or len(doc.description) == 0:
                raise SBOLError(SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT,
                                'Cannot submit Document. The Document must be assigned a displayId, name, and ' +
                                'description for upload.')
        else:
            if len(self.spoofed_resource) > 0 and self.resource in collection:
                # Correct collection URI in case a spoofed resource is being used
                collection = collection.replace(self.resource, self.spoofed_resource)
            if Config.getOption(ConfigOptions.VERBOSE.value) is True:
                self.logger.info('Submitting Document to an existing collection: ' + collection)
        # if Config.getOption(ConfigOptions.SERIALIZATION_FORMAT.value) == 'rdfxml':
        #     self.addSynBioHubAnnotations(doc)
        files = {}
        if len(doc.displayId) > 0:
            files['id'] = (None, doc.displayId)
        if len(doc.version) > 0:
            files['version'] = (None, doc.version)
        if len(doc.name) > 0:
            files['name'] = (None, doc.name)
        if len(doc.description) > 0:
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
        files['file'] = (None, doc.writeString(), 'text/xml')
        if collection != '':
            files['rootCollections'] = (None, collection)
        # Send POST request
        print(files)
        response = requests.post(self.resource + '/submit',
                                 files=files,
                                 headers={'Accept': 'text/plain', 'X-authorization': self.key})
        print(response.text)
        if response:
            return response
        elif response.status_code == 401:
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST,
                            'You must login with valid credentials before submitting')
        else:
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST,
                            'HTTP post request failed with: ' + str(response.status_code) +
                            ' - ' + str(response.content))

    def login(self, user_id, password=''):
        """In order to submit to a PartShop, you must login first.
        Register on [SynBioHub](http://synbiohub.org) to obtain account credentials.
        :param user_id: User ID
        :param password: User password
        :return:
        """
        if password is None or password == '':
            password = getpass.getpass()
        response = requests.post(
            parseURLDomain(self.resource) + '/remoteLogin',
            data={'email': user_id, 'password': password},
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        if not response:
            raise SBOLError(SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST,
                            'Login failed due to an HTTP error: ' + str(response))
        self.key = response.content.decode('utf-8')
        return response

    # def addSynBioHubAnnotations(self, doc):
    #     doc.addNamespace("http://wiki.synbiohub.org/wiki/Terms/synbiohub#", "sbh")
    #     for id, toplevel_obj in doc.SBOLObjects:
    #         toplevel_obj.apply(None, None)  # TODO

