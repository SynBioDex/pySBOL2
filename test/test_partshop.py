import os
import unittest
import json
import requests

import sbol2 as sbol
import sbol2

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
CRISPR_LOCATION = os.path.join(MODULE_LOCATION, 'resources', 'crispr_example.xml')

TEST_RESOURCE = 'https://synbiohub.utah.edu'
TEST_RESOURCE_MAIN = 'https://synbiohub.org'

if 'SBH_USER' in os.environ:
    username = os.environ['SBH_USER']
else:
    username = None
if 'SBH_PASSWORD' in os.environ:
    password = os.environ['SBH_PASSWORD']
else:
    password = None


class TestPartShop(unittest.TestCase):
    def test_pull_00(self):
        # Based on tutorial: https://pysbol2.readthedocs.io/en/latest/repositories.html
        doc = sbol.Document()
        igem = sbol.PartShop(TEST_RESOURCE_MAIN)
        igem.pull('https://synbiohub.org/public/igem/BBa_R0010/1', doc)
        # print(doc)
        # for obj in doc:
        #     print(obj)
        self.assertEqual(3, len(doc))

    def test_pull_01(self):
        # Based on tutorial: https://pysbol2.readthedocs.io/en/latest/repositories.html
        doc = sbol.Document()
        igem = sbol.PartShop('https://synbiohub.org/public/igem')
        igem.pull('BBa_B0032', doc)
        igem.pull('BBa_E0040', doc)
        igem.pull('BBa_B0012', doc)
        # print(doc)
        # for obj in doc:
        #     print(obj)
        self.assertEqual(7, len(doc))

    def test_pull_02(self):
        # I don't know what this adds over test_pull_01
        # This is a replacement for a previous test whose part was no
        # longer available at SynBioHub
        doc = sbol.Document()
        ps = sbol.PartShop('https://synbiohub.org/public/bsu')
        ps.pull('SyBiOntKB2sbol', doc)
        # print(doc)
        # for obj in doc:
        #     print(obj)
        self.assertEqual(1, len(doc))

    def test_login(self):
        # NOTE: Add /login because login pages may be different
        # depending on what site you're accessing
        igem = sbol.PartShop(TEST_RESOURCE_MAIN)
        response = igem.login('johndoe@example.org', 'test')
        self.assertEqual(response.status_code, 200)

    def test_login_bad(self):
        igem = sbol.PartShop(TEST_RESOURCE_MAIN)
        try:
            igem.login('johndoe@example.org', 'test1')
            self.fail('SBOLError not raised')
        except sbol.SBOLError as sbol_error:
            self.assertEqual(sbol_error.error_code(),
                             sbol.SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST)

    @unittest.skipIf(password is None, "No password supplied")
    def test_submit_00(self):
        RESOURCE = 'https://synbiohub.utah.edu'
        doc = sbol.Document()
        doc.displayId = 'test_collection'
        doc.name = 'test collection'
        doc.description = 'a test collection automatically generated ' \
                          'by the SBOL client library'
        ps = sbol.PartShop(RESOURCE)
        ps.login(username, password)
        response = ps.submit(doc, overwrite=1)
        self.assertEqual(response.status_code, 200)

    def test_sparqlQuery_00(self):
        ps = sbol.PartShop(TEST_RESOURCE_MAIN)
        response = ps.login('johndoe', 'test')
        self.assertEqual(response.status_code, 200)
        query = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX sbh: <http://wiki.synbiohub.org/wiki/Terms/synbiohub#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX sbol: <http://sbols.org/v2#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX purl: <http://purl.obolibrary.org/obo/>
SELECT ?p ?o
WHERE {
  <https://synbiohub.org/public/igem/BBa_K318030/1> ?p ?o
}
'''
        response = ps.sparqlQuery(query)
        # print(response.text)
        self.assertEqual(response.status_code, 200)

    def test_getURL(self):
        expected_url = 'https://example.org'
        partShop = sbol.PartShop(expected_url)
        self.assertEqual(partShop.getURL(), expected_url)

    def test_getUser(self):
        url = 'https://example.org'
        partShop = sbol.PartShop(url)
        self.assertTrue(hasattr(partShop, 'getUser'))
        self.assertEqual(partShop.getUser(), '')
        user = 'scott'
        password = 'tiger'
        # Depending on DNS we might get one of two errors. Detect both
        # and handle them gracefully. If neither of the expected
        # errors is raised, then fail the test.
        try:
            partShop.login(user, password)
        except requests.exceptions.ConnectionError:
            pass
        except sbol.sbolerror.SBOLError as err:
            self.assertEqual(err.error_code(),
                             sbol.SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST)
        self.assertEqual(partShop.getUser(), user)

    def test_getSpoofedURL(self):
        url = 'https://example.org'
        spoofed_url = 'https://synbiohub.org'
        partShop = sbol.PartShop(url, spoofed_url=spoofed_url)
        self.assertTrue(hasattr(partShop, 'getSpoofedURL'))
        self.assertEqual(partShop.getSpoofedURL(), spoofed_url)

    def test_spoof(self):
        url = 'https://example.org'
        part_shop = sbol.PartShop(url)
        self.assertEqual(part_shop.getSpoofedURL(), '')
        spoofed_url = 'https://synbiohub.org'
        part_shop.spoof(spoofed_url)
        self.assertEqual(part_shop.getSpoofedURL(), spoofed_url)

    @unittest.skipIf(password is None, "No password supplied")
    def test_submit(self):
        # This test is derived from an etl-to-synbiohub_pipeline test
        # case that was failing.
        RESOURCE = 'https://tang.ece.utah.edu'
        SPOOFED_RESOURCE = 'https://synbiohub.utah.edu'
        doc = sbol.Document()
        doc.version = '1'
        doc.displayId = 'sbol_test'
        doc.name = "SBOL Test Collection"
        doc.description = "A scratch collection for automated testing of the sbol."
        sbh = sbol.PartShop(RESOURCE, SPOOFED_RESOURCE)
        try:
            sbh.login(username, password)
        except sbol2.SBOLError as sbol_error:
            if sbol_error.error_code() == sbol2.SBOLErrorCode.SBOL_ERROR_BAD_HTTP_REQUEST:
                if '503' in sbol_error.what():
                    return
            raise
        try:
            sbh.submit(doc)
        except Exception:
            # What exception type should we really be expecting? The
            # original test had a bare except.
            uri_template = '{0}/user/{1}/{2}/{2}_collection/1'
            target_collection = uri_template.format(RESOURCE, username, doc.displayId)
            sbh.submit(doc, target_collection, 1)

    def test_uri2url(self):
        # This tests an internal method that underlies `remove` and
        # `pull`. No spoofing in these tests.
        part_shop = sbol.PartShop(TEST_RESOURCE_MAIN)
        uri = 'https://synbiohub.org/design/CAT_C0378/1'
        url = part_shop._uri2url(uri)
        self.assertEqual(url, uri)
        uri = 'https://example.org/design/CAT_C0378/1'
        try:
            url = part_shop._uri2url(uri)
        except sbol.SBOLError as err:
            self.assertEqual(err.error_code(),
                             sbol.SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT)
        else:
            self.fail('Expected SBOLError')

    def test_uri2url_spoofed(self):
        # Test with a spoofed url
        #
        # Spoofed URLs had been an issue in `pull` before extracting
        # the `_uri2url` method
        part_shop = sbol.PartShop(TEST_RESOURCE_MAIN,
                                  spoofed_url='https://example.org')
        uri = 'https://synbiohub.org/design/CAT_C0378/1'
        url = part_shop._uri2url(uri)
        self.assertEqual(url, uri)
        # _uri2url should change the spoofed URI to the resource URL
        uri = 'https://example.org/design/CAT_C0378/1'
        expected = 'https://synbiohub.org/design/CAT_C0378/1'
        url = part_shop._uri2url(uri)
        self.assertEqual(url, expected)
        # URI is not in spoofed or resource domains
        uri = 'https://example.com/design/CAT_C0378/1'
        try:
            url = part_shop._uri2url(uri)
        except sbol.SBOLError as err:
            self.assertEqual(err.error_code(),
                             sbol.SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT)
        else:
            self.fail('Expected SBOLError')

    @unittest.skipIf(password is None, "No password supplied")
    def test_attach_file(self):
        sbol2.Config.setOption('sbol_typed_uris', False)
        doc = sbol2.Document()
        doc.displayId = 'test_attachment'
        doc.name = 'test attachment'
        desc = 'a test collection created by the sbol2 unit tests'
        doc.description = desc
        md = doc.moduleDefinitions.create('attachmd')
        sbh = sbol2.PartShop(TEST_RESOURCE)
        sbh.login(username, password)
        sbh.submit(doc, overwrite=1)
        md_uri = '{}/user/{}/{}/{}/{}'.format(sbh.getURL(), sbh.getUser(), doc.displayId,
                                              md.displayId, md.version)
        sbh.attachFile(md_uri, CRISPR_LOCATION)

        # SBH will autogenerate an Attachment object, so now we query to find out
        # what the URI of that Attachment object is so we can download it
        query = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX sbh: <http://wiki.synbiohub.org/wiki/Terms/synbiohub#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX sbol: <http://sbols.org/v2#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX purl: <http://purl.obolibrary.org/obo/>
SELECT DISTINCT ?attachment_uri
WHERE {{
  <{}> sbol:attachment ?attachment_uri
}}'''.format(md_uri)
        response = sbh.sparqlQuery(query)
        content = json.loads(response.content)
        attachment_uri = content['results']['bindings'][0]['attachment_uri']['value']
        # Save to default filename
        sbh.downloadAttachment(attachment_uri)
        self.assertTrue(os.path.exists('./crispr_example.xml'))
        os.remove('crispr_example.xml')
        # Save to new file name
        sbh.downloadAttachment(attachment_uri, 'foo.xml')
        self.assertTrue(os.path.exists('./foo.xml'))
        os.remove('foo.xml')
        # Confirm error handling
        sbh.remove(attachment_uri)
        with self.assertRaises(sbol2.SBOLError) as cm:
            sbh.downloadAttachment(attachment_uri)
        e = cm.exception
        self.assertEqual(e.error_code(), sbol2.SBOLErrorCode.SBOL_ERROR_NOT_FOUND)

    def test_search_general(self):
        sbh = sbol2.PartShop(TEST_RESOURCE_MAIN)
        # sbh.login(username, password)
        results = sbh.search("NAND")
        # The response is a list
        self.assertIsInstance(results, list)
        # The response items are all of type Identified
        self.assertTrue(all([isinstance(x, sbol2.Identified)
                             for x in results]))

    def test_search_general_offset_limit(self):
        # Test a general search using offset and limit
        # This comes from a documentation example that was failing
        sbh = sbol2.PartShop(TEST_RESOURCE_MAIN)
        offset = 10
        limit = 20
        results = sbh.search('plasmid', sbol2.SBOL_COMPONENT_DEFINITION,
                             offset, limit)
        # The response is a list
        self.assertEqual(list, type(results))
        # There are `limit` items in the list (search returns more,
        # but by default we get the first `limit`)
        self.assertEqual(limit, len(results))
        # The response items are all of type Identified
        self.assertTrue(all([isinstance(x, sbol2.Identified)
                             for x in results]))

    def test_search_exact(self):
        igem = sbol.PartShop(TEST_RESOURCE_MAIN)
        limit = 10
        results = igem.search(sbol2.SO_PROMOTER,
                              sbol2.SBOL_COMPONENT_DEFINITION,
                              sbol2.SBOL_ROLES,
                              0, limit)
        # The response is a list
        self.assertEqual(list, type(results))
        # The response contains _limit_ items
        self.assertEqual(limit, len(results))
        # The response items are all of type Identified
        self.assertTrue(all([isinstance(x, sbol2.Identified)
                             for x in results]))
        doc = sbol2.Document()
        igem.pull([x.identity for x in results], doc, False)
        self.assertEqual(10, len(doc))
        for cd in doc.componentDefinitions:
            self.assertIn(sbol2.SO_PROMOTER, cd.roles)

    def test_pull_doc_version(self):
        # After a pull the document version was erroneously set to None (#281)
        doc = sbol.Document()
        self.assertIsNotNone(doc.version)
        old_version = doc.version
        igem = sbol.PartShop(TEST_RESOURCE_MAIN)
        igem.pull('https://synbiohub.org/public/igem/BBa_R0010/1', doc)
        self.assertEqual(3, len(doc))
        self.assertIsNotNone(doc.version)
        self.assertEqual(old_version, doc.version)

    def test_search_count(self):
        part_shop = sbol2.PartShop('https://synbiohub.org/public/igem')
        # searchCount did not exist, see #322
        self.assertTrue(hasattr(part_shop, 'searchCount'))
        count = part_shop.searchCount('plasmid')
        # Make sure we get an int back, not a string representation of a number
        self.assertIs(type(count), int)
        # Expecting at least 1 plasmid
        self.assertGreater(count, 0)

    def test_validate_url_forwardslash(self):
        # Tests whether the _validate_url() sucessfully filters
        # out urls containing a terminal forward slash
        part_shop = sbol2.PartShop('https://initialise-partshop')
        self.assertRaises(TypeError,
                          part_shop._validate_url,
                          'https://stackoverflow.com/')

    def test_validate_url_missing_netloc(self):
        # Tests whether the _validate_url() sucessfully filters
        # out urls with non existent netlocs
        part_shop = sbol2.PartShop('https://initialise-partshop')
        self.assertRaises(TypeError,
                          part_shop._validate_url,
                          'https://')

    def test_validate_url_invalid_scheme(self):
        # Tests whether the _validate_url() sucessfully filters
        # out urls with schemes not equal to "http" or "https"
        part_shop = sbol2.PartShop('https://initialise-partshop')
        self.assertRaises(TypeError,
                          part_shop._validate_url,
                          'file://google.com')

    def test_validate_url_hidden_list(self):
        # Tests whether the _validate_url() sucessfully filters
        # out urls as a string of a list
        part_shop = sbol2.PartShop('https://initialise-partshop')
        self.assertRaises(TypeError,
                          part_shop._validate_url,
                          '[1,2,3]')

    def test_validate_url_type_check(self):
        # Tests whether the _validate_url() sucessfully filters
        # out urls of type which is not equal to string
        part_shop = sbol2.PartShop('https://initialise-partshop')
        self.assertRaises(TypeError,
                          part_shop._validate_url,
                          [1, 2, 3])


if __name__ == '__main__':
    unittest.main()
