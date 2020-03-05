import unittest
import os
import sbol
from sbol import *

import rdflib

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
TEST_LOCATION = os.path.join(MODULE_LOCATION, 'resources',
                             'crispr_example.xml')


class TestProperty(unittest.TestCase):
    def test_listProperty(self):
        plasmid = ComponentDefinition('pBB1', BIOPAX_DNA, '1.0.0')
        plasmid.roles = [SO_PLASMID, SO_CIRCULAR]
        self.assertEqual(len(plasmid.roles), 2)

    def test_noListProperty(self):
        plasmid = ComponentDefinition('pBB1', BIOPAX_DNA, '1.0.0')
        with self.assertRaises(TypeError):
            plasmid.version = ['1', '2']

    def test_addPropertyToList(self):
        plasmid = ComponentDefinition('pBB1', BIOPAX_DNA, '1.0.0')
        plasmid.roles = [SO_PLASMID]
        plasmid.addRole(SO_CIRCULAR)
        self.assertEqual(len(plasmid.roles), 2)

    def test_removePropertyFromList(self):
        plasmid = ComponentDefinition('pBB1', BIOPAX_DNA, '1.0.0')
        plasmid.roles = [SO_PLASMID, SO_CIRCULAR]
        plasmid.removeRole()
        self.assertEqual(len(plasmid.roles), 1)

    def test_lenOwnedObject(self):
        d = Document()
        d.read(TEST_LOCATION)
        self.assertEqual(25, len(d.componentDefinitions))
        self.assertEqual(2, len(d.moduleDefinitions))
        self.assertEqual(4, len(d.sequences))

    def test_getitem(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example/')
        d = sbol.Document()
        d.read(TEST_LOCATION)
        s1 = d.sequences['CRa_U6_seq']
        expected = 'http://sbols.org/CRISPR_Example/CRa_U6_seq/1.0.0'
        self.assertEqual(expected, str(s1))

    def test_readProperties(self):
        d = Document()
        d.read(TEST_LOCATION)
        cd2 = d.componentDefinitions['http://sbols.org/CRISPR_Example/EYFP_gene/1.0.0']
        self.assertEqual(2, len(cd2.components))
        self.assertEqual(1, len(cd2.roles))
        md = d.moduleDefinitions['http://sbols.org/CRISPR_Example/CRISPR_Template/1.0.0']
        self.assertEqual(5, len(md.functionalComponents))
        self.assertEqual(3, len(md.interactions))
        self.assertEqual(0, len(md.roles))

    def test_text_property_constructor(self):
        # Test None as parent object
        with self.assertRaises(AttributeError):
            sbol.TextProperty(None, sbol.SBOL_NAME, '0', '*', [], 'foo')
        # Test string as parent object
        with self.assertRaises(AttributeError):
            sbol.TextProperty('foo', sbol.SBOL_NAME, '0', '*', [], 'foo')
        # Test with object whose properties attribute is not a dict
        with self.assertRaises(TypeError):
            md = sbol.ModuleDefinition()
            md.properties = []
            sbol.TextProperty(md, sbol.SBOL_NAME, '0', '*', [], 'foo')

    def test_literal_property_properties(self):
        md = sbol.ModuleDefinition()
        self.assertNotIn(sbol.UNDEFINED, md.properties)
        sbol.property.LiteralProperty(md, sbol.UNDEFINED, '0', '*', [], 'foo')
        # Creating the property should also create the entry in the
        # parent properties dict
        self.assertIn(sbol.UNDEFINED, md.properties)

    def test_text_property_setting_single(self):
        md = sbol.ModuleDefinition()
        testing_uri = URIRef(SBOL_URI + "#Testing")
        tp = sbol.TextProperty(md, testing_uri, '0', '1', [])
        # Test setting to string
        expected = 'foo'
        tp.value = expected
        self.assertEqual(tp.value, rdflib.Literal(expected))
        # Test setting to None
        tp.value = None
        self.assertIsNone(tp.value)
        # Test integer
        with self.assertRaises(TypeError):
            tp.value = 3
        # Test setting to list
        with self.assertRaises(TypeError):
            tp.value = ['foo', 'bar']

    def test_text_property_setting_list(self):
        md = sbol.ModuleDefinition()
        testing_uri = URIRef(SBOL_URI + "#Testing")
        tp = sbol.TextProperty(md, testing_uri, '0', '*', [])
        # Test setting to string
        expected = 'foo'
        tp.value = expected
        self.assertEqual(tp.value, [rdflib.Literal(expected)])
        # Test setting to None
        with self.assertRaises(TypeError):
            tp.value = None
        # Test setting to list
        expected = ['foo', 'bar']
        tp.value = expected
        self.assertEqual(tp.value, [rdflib.Literal(x) for x in expected])
        # Test setting to list of integers
        with self.assertRaises(TypeError):
            tp.value = [1, 2, 3]
        # Test setting to empty list
        expected = []
        tp.value = expected
        self.assertEqual(tp.value, [])


if __name__ == '__main__':
    unittest.main()
