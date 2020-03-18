import unittest

import rdflib

import sbol


class TestCollection(unittest.TestCase):

    def __init__(self, *args):
        super().__init__(*args)
        self.homespace = 'http://example.org'

    def make_identity(self, homespace, name, version, tipe='Collection'):
        uri = '{}/{}/{}/{}'
        return uri.format(homespace, tipe, name, version)

    def setUp(self):
        # Always reset homespace
        sbol.setHomespace(self.homespace)
        sbol.Config.setOption('sbol_typed_uris', True)
        sbol.Config.setOption('sbol_compliant_uris', True)

    def testEmptyConstructor(self):
        # This is the default name in the collection constructor
        name = 'example'
        c = sbol.Collection()
        expected_identity = self.make_identity(self.homespace, name,
                                               sbol.VERSION_STRING)
        self.assertEqual(c.identity, rdflib.URIRef(expected_identity))
        self.assertEqual(c.displayId, rdflib.Literal(name))
        self.assertEqual(c.version, rdflib.Literal(sbol.VERSION_STRING))
        self.assertEqual(c.rdf_type, sbol.SBOL_COLLECTION)
        doc = sbol.Document()
        doc.addCollection(c)
        self.assertEqual(len(doc.collections), 1)

    def test1ArgConstructor(self):
        name = 'foo'
        c = sbol.Collection(name)
        expected_identity = self.make_identity(self.homespace, name,
                                               sbol.VERSION_STRING)
        self.assertEqual(c.identity, rdflib.URIRef(expected_identity))
        self.assertEqual(c.displayId, rdflib.Literal(name))
        self.assertEqual(c.version, rdflib.Literal(sbol.VERSION_STRING))
        self.assertEqual(c.rdf_type, sbol.SBOL_COLLECTION)
        doc = sbol.Document()
        doc.addCollection(c)
        self.assertEqual(len(doc.collections), 1)

    def test2ArgConstructor(self):
        name = 'foo'
        version = '3'
        c = sbol.Collection(name, version)
        expected_identity = self.make_identity(self.homespace, name,
                                               version)
        self.assertEqual(c.identity, rdflib.URIRef(expected_identity))
        self.assertEqual(c.displayId, rdflib.Literal(name))
        self.assertEqual(c.version, rdflib.Literal(version))
        self.assertEqual(c.rdf_type, sbol.SBOL_COLLECTION)
        doc = sbol.Document()
        doc.addCollection(c)
        self.assertEqual(len(doc.collections), 1)

    def test3ArgConstructor(self):
        name = 'foo'
        version = '3'
        rdf_type = sbol.SBOL_COLLECTION + '2'
        c = sbol.Collection(name, version, type_uri=rdf_type)
        expected_identity = self.make_identity(self.homespace, name,
                                               version, 'Collection2')
        self.assertEqual(c.identity, rdflib.URIRef(expected_identity))
        self.assertEqual(c.displayId, rdflib.Literal(name))
        self.assertEqual(c.version, rdflib.Literal(version))
        self.assertEqual(c.rdf_type, rdf_type)
        # Verify that when added to a document, this collection is not
        # in the list of collections. That's because the rdf_type is
        # not SBOL_COLLECTION.
        doc = sbol.Document()
        doc.addCollection(c)
        self.assertEqual(len(doc.collections), 0)
