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

    def test_literal_property_constructor(self):
        with self.assertRaises(AttributeError):
            sbol.property.LiteralProperty(None, sbol.SBOL_NAME, '0', '*', [], 'foo')
        with self.assertRaises(AttributeError):
            sbol.property.LiteralProperty('foo', sbol.SBOL_NAME, '0', '*', [], 'foo')
        with self.assertRaises(TypeError):
            md = sbol.ModuleDefinition()
            md.properties = []
            sbol.property.LiteralProperty(md, sbol.SBOL_NAME, '0', '*', [], 'foo')

    def test_literal_property_properties(self):
        md = sbol.ModuleDefinition()
        self.assertNotIn(sbol.UNDEFINED, md.properties)
        sbol.property.LiteralProperty(md, sbol.UNDEFINED, '0', '*', [], 'foo')
        # Creating the property should also create the entry in the
        # parent properties dict
        self.assertIn(sbol.UNDEFINED, md.properties)


if __name__ == '__main__':
    unittest.main()
