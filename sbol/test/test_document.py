import locale
import logging
import os
import unittest
import sbol
from rdflib import URIRef
from rdflib.namespace import NamespaceManager

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
TEST_LOCATION = os.path.join(MODULE_LOCATION, 'resources', 'crispr_example.xml')


class TestDocument(unittest.TestCase):

    def test_empty_len0(self):
        doc = sbol.Document()
        # print(doc)
        self.assertEqual(0, len(doc), "Length of document should be 0")

    def test_addGetTopLevel_uri(self):
        doc = sbol.Document()
        # Tutorial doesn't drop final forward slash, but this isn't right.
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', True)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        cas9 = sbol.ComponentDefinition('Cas9', sbol.BIOPAX_PROTEIN)
        doc.addModuleDefinition(crispr_template)
        doc.addComponentDefinition(cas9)

        # Note: tutorial has 1.0.0 instead of 1 but this doesn't work
        crispr_template_uri = 'http://sbols.org/CRISPR_Example/CRISPR_Template/1'
        crispr_template_2 = doc.getModuleDefinition(crispr_template_uri)
        cas9_2 = doc.getComponentDefinition('http://sbols.org/CRISPR_Example/Cas9/1')
        self.assertEqual(crispr_template, crispr_template_2)
        self.assertEqual(cas9, cas9_2)

    def test_addGetTopLevel_displayId(self):
        doc = sbol.Document()
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', True)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        cas9 = sbol.ComponentDefinition('Cas9', sbol.BIOPAX_PROTEIN)
        doc.addModuleDefinition(crispr_template)
        doc.addComponentDefinition(cas9)

        crispr_template_2 = doc.moduleDefinitions['CRISPR_Template']
        cas9_2 = doc.componentDefinitions['Cas9']
        self.assertEqual(crispr_template, crispr_template_2)
        self.assertEqual(cas9, cas9_2)

    def test_addGetTopLevel_indexing(self):
        doc = sbol.Document()
        # Tutorial doesn't drop final forward slash, but this isn't right.
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', True)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        cas9 = sbol.ComponentDefinition('Cas9', sbol.BIOPAX_PROTEIN)
        doc.addModuleDefinition(crispr_template)
        doc.addComponentDefinition(cas9)

        crispr_template_2 = doc.moduleDefinitions[0]
        cas9_2 = doc.componentDefinitions[0]
        self.assertEqual(crispr_template, crispr_template_2)
        self.assertEqual(cas9, cas9_2)

    def test_iteration(self):
        doc = sbol.Document()
        doc.read(TEST_LOCATION)
        i = 0
        for obj in doc:
            i += 1
            # print(obj)
        self.assertEqual(len(doc), 31)
        # print(doc)

    def test_identity(self):
        # The sbol:identity relation should not be written out when
        # serializing SBOL.
        doc = sbol.Document()
        doc.read(TEST_LOCATION)
        result = doc.writeString()
        self.assertNotIn('sbol:identity', result)

    def test_utf8_append(self):
        utf8_path = os.path.join(MODULE_LOCATION, 'SBOLTestSuite', 'SBOL2',
                                 'pICSL50014.xml')
        doc = sbol.Document()
        doc.append(utf8_path)

    def test_utf8_append_no_locale(self):
        # Test loading a utf-8 SBOL file without LANG set. This was a
        # bug at one time, and only shows itself when LANG is unset.
        # Here we simulate that by temporarily setting the locale to
        # the generic 'C' locale.
        utf8_path = os.path.join(MODULE_LOCATION, 'SBOLTestSuite', 'SBOL2',
                                 'pICSL50014.xml')
        loc = locale.getlocale()
        try:
            locale.setlocale(locale.LC_ALL, 'C')
            doc = sbol.Document()
            doc.append(utf8_path)
        finally:
            locale.setlocale(locale.LC_ALL, loc)

    def test_utf8_read(self):
        utf8_path = os.path.join(MODULE_LOCATION, 'SBOLTestSuite', 'SBOL2',
                                 'pICSL50014.xml')
        doc = sbol.Document()
        doc.read(utf8_path)

    def test_utf8_read_no_locale(self):
        # Test loading a utf-8 SBOL file without LANG set. This was a
        # bug at one time, and only shows itself when LANG is unset.
        # Here we simulate that by temporarily setting the locale to
        # the generic 'C' locale.
        utf8_path = os.path.join(MODULE_LOCATION, 'SBOLTestSuite', 'SBOL2',
                                 'pICSL50014.xml')
        loc = locale.getlocale()
        try:
            locale.setlocale(locale.LC_ALL, 'C')
            doc = sbol.Document()
            doc.read(utf8_path)
        finally:
            locale.setlocale(locale.LC_ALL, loc)

    def test_constructor(self):
        doc = sbol.Document(TEST_LOCATION)
        self.assertEqual(len(doc), 31)
        self.assertEqual(len(doc.componentDefinitions), 25)

    def test_find(self):
        doc = sbol.Document(TEST_LOCATION)
        found = doc.find('http://sbols.org/CRISPR_Example/CRISPR_Template')
        # At one point Document.find was returning -1 because it was calling str.find
        self.assertNotEqual(found, -1)
        self.assertIsNone(found)
        found = doc.find('http://sbols.org/CRISPR_Example/CRISPR_Template/1.0.0')
        self.assertNotEqual(found, -1)
        self.assertIsNotNone(found)

    def test_lookup(self):
        # Test simple key lookup via the __getitem__() method
        doc = sbol.Document()
        md = doc.moduleDefinitions.create('foo')
        md2 = doc.moduleDefinitions[md.displayId]
        self.assertEqual(md.identity, md2.identity)

    def test_find_property_value(self):
        # find_property_value wasn't comparing against the passed
        # `value` parameter, so it was returning all identities in the
        # document.
        sbol.setHomespace('http://examples.org')
        sbol.Config.setOption('sbol_compliant_uris', True)
        sbol.Config.setOption('sbol_typed_uris', True)
        doc = sbol.Document()
        md = doc.moduleDefinitions.create('foo')
        test_uri = 'http://examples.org/does/not/exist/1'
        matches = doc.find_property_value(sbol.SBOL_IDENTITY, test_uri)
        self.assertEqual(len(matches), 0)

    def test_add_namespace(self):
        doc = sbol.Document()
        cd = doc.componentDefinitions.create('cd')
        cd.foo = sbol.property.LiteralProperty(cd, 'http://examples.org#foo',
                                               '0', '1', None, 'bar')
        doc.readString(doc.writeString())
        namespaces = [n[1] for n in doc.graph.namespace_manager.namespaces()]
        self.assertFalse('http://examples.org#' in namespaces)
        doc.addNamespace('http://examples.org#', 'examples')
        cd.foo = sbol.property.LiteralProperty(cd, 'http://examples.org#foo',
                                               '0', '1', None, 'bar')
        namespaces = [n for n in doc.graph.namespace_manager.namespaces()]
        doc.readString(doc.writeString())
        namespaces = [n for n in doc.graph.namespace_manager.namespaces()]
        self.assertTrue(('examples', URIRef('http://examples.org#')) in namespaces)

    def test_namespace_fail(self):
        doc = sbol.Document()
        with self.assertRaises(ValueError):
            doc.addNamespace('http://examples.org', 'foo')

    def test_doc(self):
        doc = sbol.Document()
        # This was actually broken, so don't laugh at it
        self.assertEqual(doc.doc, doc)
        md = doc.moduleDefinitions.create('foo')
        self.assertEqual(doc, md.doc)
        m = md.modules.create('bar')
        self.assertEqual(doc, m.doc)


if __name__ == '__main__':
    unittest.main()
