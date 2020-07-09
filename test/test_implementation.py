import unittest

import sbol2 as sbol
import sbol2


class TestImplementation(unittest.TestCase):

    def __init__(self, *args):
        super().__init__(*args)
        self.homespace = 'http://example.org'

    def make_identity(self, homespace, name, version, tipe='Implementation'):
        uri = '{}/{}/{}/{}'
        return uri.format(homespace, tipe, name, version)

    def setUp(self):
        # Always reset homespace
        sbol.setHomespace(self.homespace)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)

    def test_implementation_exported(self):
        self.assertIn('Implementation', dir(sbol))

    def testEmptyConstructor(self):
        # This is the default name in the implementation constructor
        name = 'example'
        c = sbol.Implementation()
        expected_identity = self.make_identity(self.homespace, name,
                                               sbol.VERSION_STRING)
        self.assertEqual(c.identity, expected_identity)
        self.assertEqual(c.displayId, name)
        self.assertEqual(c.version, sbol.VERSION_STRING)
        self.assertEqual(c.rdf_type, sbol.SBOL_IMPLEMENTATION)
        doc = sbol.Document()
        doc.addImplementation(c)
        self.assertEqual(len(doc.implementations), 1)

    def test1ArgConstructor(self):
        name = 'foo'
        c = sbol.Implementation(name)
        expected_identity = self.make_identity(self.homespace, name,
                                               sbol.VERSION_STRING)
        self.assertEqual(c.identity, expected_identity)
        self.assertEqual(c.displayId, name)
        self.assertEqual(c.version, sbol.VERSION_STRING)
        self.assertEqual(c.rdf_type, sbol.SBOL_IMPLEMENTATION)
        doc = sbol.Document()
        doc.addImplementation(c)
        self.assertEqual(len(doc.implementations), 1)

    def test2ArgConstructor(self):
        name = 'foo'
        version = '3'
        c = sbol.Implementation(name, version)
        expected_identity = self.make_identity(self.homespace, name,
                                               version)
        self.assertEqual(c.identity, expected_identity)
        self.assertEqual(c.displayId, name)
        self.assertEqual(c.version, version)
        self.assertEqual(c.rdf_type, sbol.SBOL_IMPLEMENTATION)
        doc = sbol.Document()
        doc.addImplementation(c)
        self.assertEqual(len(doc.implementations), 1)

    def test3ArgConstructor(self):
        name = 'foo'
        version = '3'
        rdf_type = sbol.SBOL_IMPLEMENTATION + '2'
        c = sbol.Implementation(name, version, type_uri=rdf_type)
        expected_identity = self.make_identity(self.homespace, name,
                                               version, 'Implementation2')
        self.assertEqual(c.identity, expected_identity)
        self.assertEqual(c.displayId, name)
        self.assertEqual(c.version, version)
        self.assertEqual(c.rdf_type, rdf_type)
        # Verify that when added to a document, this implementation is
        # not in the list of implementations. That's because the rdf_type
        # is not SBOL_IMPLEMENTATION.
        doc = sbol.Document()
        doc.addImplementation(c)
        self.assertEqual(len(doc.implementations), 0)
