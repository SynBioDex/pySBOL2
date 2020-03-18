import os
import sys
import unittest

import rdflib

import sbol
from sbol import *

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
CRISPR_EXAMPLE = os.path.join(MODULE_LOCATION, 'resources', 'crispr_example.xml')


class TestComponentDefinitions(unittest.TestCase):

    def setUp(self):
        pass

    def test_typesSet(self):
        # Constructs a protein component
        cas9 = ComponentDefinition('Cas9', BIOPAX_PROTEIN)
        self.assertEqual([BIOPAX_PROTEIN], cas9.types)

    def test_typesNotSet(self):
        target_promoter = ComponentDefinition('target_promoter')
        self.assertEqual([BIOPAX_DNA], target_promoter.types)

    def testAddComponentDefinition(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', True)
        Config.setOption('sbol_typed_uris', False)
        expected = 'BB0001'
        test_CD = ComponentDefinition(expected)
        doc = Document()
        doc.addComponentDefinition(test_CD)
        self.assertIsNotNone(doc.componentDefinitions.get(expected))
        displayId = doc.componentDefinitions.get(expected).displayId
        self.assertEqual(str(displayId), expected)
        self.assertEqual(displayId, rdflib.Literal(expected))

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
        doc.read(CRISPR_EXAMPLE)

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
        # Sort the list. Does doc.componentDefintions make any
        # guarantees about order?
        list_cd_read.sort()
        # Convert expected display ids to rdflib.Literals and compare
        self.assertSequenceEqual(list_cd_read,
                                 [rdflib.Literal(x) for x in list_cd])
        # Convert CD display ids to strings and compare
        self.assertSequenceEqual([str(x) for x in list_cd_read],
                                 list_cd)
        # Python 3 compatability
        if sys.version_info[0] < 3:
            self.assertItemsEqual(list_cd_read, list_cd)
        else:
            expected = [rdflib.Literal(x) for x in list_cd]
            self.assertCountEqual(list_cd_read, expected)

    # See Issue #64, CD.assemblePrimaryStructure is not implemented
    @unittest.expectedFailure  # See issue 64
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

    @unittest.expectedFailure
    def testInsertDownstream(self):
        doc = Document()
        gene = ComponentDefinition("BB0001")
        promoter = ComponentDefinition("R0010")
        rbs = ComponentDefinition("B0032")
        cds = ComponentDefinition("E0040")
        terminator = ComponentDefinition("B0012")

        doc.addComponentDefinition([gene, promoter, rbs, cds, terminator])
        gene.assemblePrimaryStructure([promoter, rbs, cds])
        primary_structure_components = gene.getPrimaryStructureComponents()
        c_promoter = primary_structure_components[0]
        c_rbs = primary_structure_components[1]
        c_cds = primary_structure_components[2]
        gene.insertDownstreamComponent(c_cds, terminator)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [promoter.identity, rbs.identity,
                                   cds.identity, terminator.identity]
        self.assertListEqual(primary_structure, valid_primary_structure)

    @unittest.expectedFailure
    def testInsertUpstream(self):
        doc = Document()
        gene = ComponentDefinition("BB0001")
        promoter = ComponentDefinition("R0010")
        rbs = ComponentDefinition("B0032")
        cds = ComponentDefinition("E0040")
        terminator = ComponentDefinition("B0012")

        doc.addComponentDefinition([gene, promoter, rbs, cds, terminator])
        gene.assemblePrimaryStructure([rbs, cds, terminator])
        primary_structure_components = gene.getPrimaryStructureComponents()
        c_rbs = primary_structure_components[0]
        c_cds = primary_structure_components[1]
        c_terminator = primary_structure_components[2]
        gene.insertUpstreamComponent(c_rbs, promoter)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [promoter.identity, rbs.identity,
                                   cds.identity, terminator.identity]
        self.assertListEqual(primary_structure, valid_primary_structure)

    @unittest.expectedFailure
    def testHasUpstreamComponent(self):
        uri = 'http://sbols.org/CRISPR_Example/gRNA_b_gene/1.0.0'
        doc = sbol.Document()
        doc.read(CRISPR_EXAMPLE)
        cd = doc.componentDefinitions.get(uri)
        self.assertIsNotNone(cd)
        comps = {
            'http://sbols.org/CRISPR_Example/gRNA_b_gene/CRa_U6/1.0.0': True,
            'http://sbols.org/CRISPR_Example/gRNA_b_gene/CRa_U6/1.0.0': True,
            'http://sbols.org/CRISPR_Example/gRNA_b_gene/CRa_U6/1.0.0': False
        }
        uri = 'http://sbols.org/CRISPR_Example/gRNA_b_gene/CRa_U6/1.0.0'
        c = cd.components.get(uri)
        self.assertTrue(cd.hasUpstreamComponent(c))
