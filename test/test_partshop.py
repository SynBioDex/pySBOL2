import os
import unittest

import requests

import sbol2 as sbol
import sbol2

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
CRISPR_LOCATION = os.path.join(MODULE_LOCATION, 'resources', 'crispr_example.xml')

TEST_RESOURCE = 'https://synbiohub.utah.edu'

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
        igem = sbol.PartShop('https://synbiohub.org')
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

    # The part has gone missing in SynBioHub
    @unittest.expectedFailure
    def test_pull_02(self):
        doc = sbol.Document()
        ps = sbol.PartShop('https://synbiohub.utah.edu/public/RepressionModel')
        ps.pull('CRPb_characterization_Circuit', doc)
        # print(doc)
        # for obj in doc:
        #     print(obj)
        self.assertEqual(31, len(doc))

    def test_login(self):
        # NOTE: Add /login because login pages may be different
        # depending on what site you're accessing
        igem = sbol.PartShop('https://synbiohub.org')
        response = igem.login('johndoe@example.org', 'test')
        self.assertEqual(response.status_code, 200)

    def test_login_bad(self):
        igem = sbol.PartShop('https://synbiohub.org')
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
        ps = sbol.PartShop('https://synbiohub.org')
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
        sbh.login(username, password)
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
        part_shop = sbol.PartShop('https://synbiohub.org')
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
        part_shop = sbol.PartShop('https://synbiohub.org',
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
        doc = sbol2.Document()
        doc.displayId = 'test_attachment'
        doc.name = 'test attachment'
        desc = 'a test collection created by the sbol2 unit tests'
        doc.description = desc
        md = doc.moduleDefinitions.create('attachmd')
        sbh = sbol2.PartShop(TEST_RESOURCE)
        sbh.login(username, password)
        sbh.submit(doc, overwrite=1)
        md_uri = '{}/user/{}/{}/{}/{}'.format(sbh.getURL(), sbh.getUser(),
                                              doc.displayId, md.displayId,
                                              md.version)
        sbh.attachFile(md_uri, CRISPR_LOCATION)
