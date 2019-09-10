import unittest
from sbol.componentdefinition import ComponentDefinition
from sbol.document import Document
from sbol.constants import *
from sbol.config import *
import os

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
        setHomespace('http://sbols.org/CRISPR_Example/')
        d = Document()
        d.read(TEST_LOCATION)
        s1 = d.sequences['CRa_U6_seq']
        self.assertEqual('http://sbols.org/CRISPR_Example/CRa_U6_seq/1.0.0',
                         str(s1))

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


if __name__ == '__main__':
    unittest.main()
