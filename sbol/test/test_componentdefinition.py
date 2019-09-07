import unittest
from sbol.document import *
from sbol.componentdefinition import *
import os
import sys


MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))


class TestComponentDefinitions(unittest.TestCase):

    def setUp(self):
        pass

    def test_typesSet(self):
        # Constructs a protein component
        cas9 = ComponentDefinition('Cas9', BIOPAX_PROTEIN)
        self.assertEqual([BIOPAX_PROTEIN.n3()[1:-1]], cas9.types)

    def test_typesNotSet(self):
        target_promoter = ComponentDefinition('target_promoter')
        self.assertEqual([BIOPAX_DNA.n3()[1:-1]], target_promoter.types)

    def testAddComponentDefinition(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', True)
        Config.setOption('sbol_typed_uris', False)
        test_CD = ComponentDefinition("BB0001")
        doc = Document()
        doc.addComponentDefinition(test_CD)
        self.assertIsNotNone(doc.componentDefinitions.get("BB0001"))
        displayId = doc.componentDefinitions.get("BB0001").displayId
        self.assertEqual(displayId, "BB0001")

    def testRemoveComponentDefinition(self):
        test_CD = ComponentDefinition("BB0001")
        doc = Document()
        doc.addComponentDefinition(test_CD)
        doc.componentDefinitions.remove(0)
        # NOTE: changed the test to expect the 'sbol error type'
        # as opposed to a RuntimeError.
        self.assertRaises(SBOLError, lambda: doc.componentDefinitions.get("BB0001"))

    def testCDDisplayId(self):
        list_cd_read = []
        doc = Document()
        doc.read(os.path.join(MODULE_LOCATION, 'crispr_example.xml'))

        # List of displayIds
        list_cd = ['CRP_b', 'CRa_U6', 'EYFP', 'EYFP_cds', 'EYFP_gene',
                   'Gal4VP16', 'Gal4VP16_cds', 'Gal4VP16_gene',
                   'cas9_gRNA_complex', 'cas9_generic',
                   'cas9m_BFP', 'cas9m_BFP_cds',
                   'cas9m_BFP_gRNA_b', 'cas9m_BFP_gene',
                   'gRNA_b', 'gRNA_b_gene', 'gRNA_b_nc', 'gRNA_b_terminator',
                   'gRNA_generic', 'mKate', 'mKate_cds', 'mKate_gene',
                   'pConst', 'target', 'target_gene']

        for CD in doc.componentDefinitions:
            list_cd_read.append(CD.displayId)

        self.assertSequenceEqual(list_cd_read, list_cd)
        # Python 3 compatability
        if sys.version_info[0] < 3:
            self.assertItemsEqual(list_cd_read, list_cd)
        else:
            self.assertCountEqual(list_cd_read, list_cd)

    def testPrimaryStructureIteration(self):
        list_cd = []
        list_cd_true = ["R0010", "E0040", "B0032", "B0012"]
        doc = Document()
        gene = ComponentDefinition("BB0001")
        promoter = ComponentDefinition("R0010")
        rbs = ComponentDefinition("B0032")
        cds = ComponentDefinition("E0040")
        terminator = ComponentDefinition("B0012")

        doc.addComponentDefinition([gene, promoter, rbs, cds, terminator])

        gene.assemblePrimaryStructure([promoter, rbs, cds, terminator])
        primary_sequence = gene.getPrimaryStructure()
        for component in primary_sequence:
            list_cd.append(component.displayId)

        # Python 3 compatability
        if sys.version_info[0] < 3:
            self.assertItemsEqual(list_cd, list_cd_true)
        else:
            self.assertCountEqual(list_cd, list_cd_true)


if __name__ == '__main__':
    unittest.main()
