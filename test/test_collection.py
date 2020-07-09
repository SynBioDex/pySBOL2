import unittest

import rdflib

import sbol2


class TestCollection(unittest.TestCase):

    def __init__(self, *args):
        super().__init__(*args)
        self.homespace = 'http://example.org'

    def make_identity(self, homespace, name, version, tipe='Collection'):
        uri = '{}/{}/{}/{}'
        return uri.format(homespace, tipe, name, version)

    def setUp(self):
        # Always reset homespace
        sbol2.setHomespace(self.homespace)
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)

    def testEmptyConstructor(self):
        # This is the default name in the collection constructor
        name = 'example'
        c = sbol2.Collection()
        expected_identity = self.make_identity(self.homespace, name,
                                               sbol2.VERSION_STRING)
        self.assertEqual(c.identity, expected_identity)
        self.assertEqual(c.displayId, name)
        self.assertEqual(c.version, sbol2.VERSION_STRING)
        self.assertEqual(c.rdf_type, sbol2.SBOL_COLLECTION)
        doc = sbol2.Document()
        doc.addCollection(c)
        self.assertEqual(len(doc.collections), 1)

    def test1ArgConstructor(self):
        name = 'foo'
        c = sbol2.Collection(name)
        expected_identity = self.make_identity(self.homespace, name,
                                               sbol2.VERSION_STRING)
        self.assertEqual(c.identity, expected_identity)
        self.assertEqual(c.displayId, name)
        self.assertEqual(c.version, sbol2.VERSION_STRING)
        self.assertEqual(c.rdf_type, sbol2.SBOL_COLLECTION)
        doc = sbol2.Document()
        doc.addCollection(c)
        self.assertEqual(len(doc.collections), 1)

    def test2ArgConstructor(self):
        name = 'foo'
        version = '3'
        c = sbol2.Collection(name, version)
        expected_identity = self.make_identity(self.homespace, name,
                                               version)
        self.assertEqual(c.identity, expected_identity)
        self.assertEqual(c.displayId, name)
        self.assertEqual(c.version, version)
        self.assertEqual(c.rdf_type, sbol2.SBOL_COLLECTION)
        doc = sbol2.Document()
        doc.addCollection(c)
        self.assertEqual(len(doc.collections), 1)

    def test3ArgConstructor(self):
        name = 'foo'
        version = '3'
        rdf_type = sbol2.SBOL_COLLECTION + '2'
        c = sbol2.Collection(name, version, type_uri=rdf_type)
        expected_identity = self.make_identity(self.homespace, name,
                                               version, 'Collection2')
        self.assertEqual(c.identity, expected_identity)
        self.assertEqual(c.displayId, name)
        self.assertEqual(c.version, version)
        self.assertEqual(c.rdf_type, rdf_type)
        # Verify that when added to a document, this collection is not
        # in the list of collections. That's because the rdf_type is
        # not SBOL_COLLECTION.
        doc = sbol2.Document()
        doc.addCollection(c)
        self.assertEqual(len(doc.collections), 0)
