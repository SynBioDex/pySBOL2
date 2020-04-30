import os
import sys
import unittest

import rdflib

import sbol2

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
CRISPR_EXAMPLE = os.path.join(MODULE_LOCATION, 'resources', 'crispr_example.xml')


class TestComponentDefinitions(unittest.TestCase):

    def setUp(self):
        pass

    def test_typesSet(self):
        # Constructs a protein component
        cas9 = sbol2.ComponentDefinition('Cas9', sbol2.BIOPAX_PROTEIN)
        self.assertEqual([sbol2.BIOPAX_PROTEIN], cas9.types)

    def test_typesNotSet(self):
        target_promoter = sbol2.ComponentDefinition('target_promoter')
        self.assertEqual([sbol2.BIOPAX_DNA], target_promoter.types)

    def testAddComponentDefinition(self):
        sbol2.setHomespace('http://sbols.org/CRISPR_Example')
        sbol2.Config.setOption('sbol_compliant_uris', True)
        sbol2.Config.setOption('sbol_typed_uris', False)
        expected = 'BB0001'
        test_CD = sbol2.ComponentDefinition(expected)
        doc = sbol2.Document()
        doc.addComponentDefinition(test_CD)
        self.assertIsNotNone(doc.componentDefinitions.get(expected))
        displayId = doc.componentDefinitions.get(expected).displayId
        self.assertEqual(str(displayId), expected)
        self.assertEqual(displayId, rdflib.Literal(expected))

    def testRemoveComponentDefinition(self):
        test_CD = sbol2.ComponentDefinition("BB0001")
        doc = sbol2.Document()
        doc.addComponentDefinition(test_CD)
        doc.componentDefinitions.remove(0)
        # NOTE: changed the test to expect the 'sbol error type'
        # as opposed to a RuntimeError.
        with self.assertRaises(sbol2.SBOLError):
            doc.componentDefinitions.get("BB0001")

    def testCDDisplayId(self):
        list_cd_read = []
        doc = sbol2.Document()
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
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        rbs = sbol2.ComponentDefinition("B0032")
        cds = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

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
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        rbs = sbol2.ComponentDefinition("B0032")
        cds = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

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
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        rbs = sbol2.ComponentDefinition("B0032")
        cds = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

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
        doc = sbol2.Document()
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

    def testOwnedLocation(self):
        cd = sbol2.ComponentDefinition('cd')
        sa = cd.sequenceAnnotations.create('sa')
        r = sa.locations.createRange('r')
        self.assertEqual(type(r), sbol2.Range)
        r = sa.locations['r']
        self.assertEqual(type(r), sbol2.Range)
        gl = sa.locations.createGenericLocation('gl')
        self.assertEqual(type(gl), sbol2.GenericLocation)
        gl = sa.locations['gl']
        self.assertEqual(type(gl), sbol2.GenericLocation)
        self.assertEqual(len(sa.locations), 2)

    def testCut(self):
        cd = sbol2.ComponentDefinition('cd')
        sa = cd.sequenceAnnotations.create('sa')
        c = sa.locations.createCut('c')
        self.assertEqual(type(c), sbol2.Cut)
        c = sa.locations['c']
        self.assertEqual(type(c), sbol2.Cut)

    def test_get_range(self):
        cd = sbol2.ComponentDefinition('cd')
        sa = cd.sequenceAnnotations.create('sa')
        r = sa.locations.createRange('r')
        self.assertEqual(type(r), sbol2.Range)
        # SYNBICT uses getRange with no argument. It returns the first
        # object.
        r2 = sa.locations.getRange()
        self.assertEqual(r2, r)
        # getCut with zero args should raise a type error because the
        # first object is a Range.
        with self.assertRaises(TypeError):
            sa.locations.getCut()

    def test_get_cut(self):
        cd = sbol2.ComponentDefinition('cd')
        sa = cd.sequenceAnnotations.create('sa')
        c = sa.locations.createCut('c')
        self.assertEqual(type(c), sbol2.Cut)
        # SYNBICT uses getCut with no argument. It returns the first
        # object.
        c2 = sa.locations.getCut()
        self.assertEqual(c2, c)
        # getRange with zero args should raise a type error because
        # the first object is a Cut.
        with self.assertRaises(TypeError):
            sa.locations.getRange()

    def test_hidden_sequence(self):
        # Sequence should be hidden when writing SBOL
        doc = sbol2.Document()
        cd = sbol2.ComponentDefinition('cd1', sbol2.BIOPAX_DNA)
        cd.name = 'cd1-name'
        cd.description = 'cd1-description'
        seq = sbol2.Sequence('cd1_sequence', 'GCAT')
        cd.sequence = seq
        doc.addComponentDefinition(cd)
        xml = doc.writeString()
        graph = rdflib.Graph()
        graph.parse(data=xml)
        # We shouldn't find SBOL_SEQUENCE within the component definition
        bad_triple = (cd.identity, sbol2.SBOL_SEQUENCE, None)
        self.assertEqual([], list(graph.triples(bad_triple)))
        good_triple = (cd.identity, sbol2.SBOL_SEQUENCE_PROPERTY, None)
        good_triples = list(graph.triples(good_triple))
        self.assertEqual(len(good_triples), 1)
        self.assertEqual(good_triples[0], (cd.identity,
                                           sbol2.SBOL_SEQUENCE_PROPERTY,
                                           seq.identity))

    def test_sequence_validation(self):
        cd = sbol2.ComponentDefinition('cd1', sbol2.BIOPAX_DNA)
        cd.name = 'cd1-name'
        cd.description = 'cd1-description'
        seq = sbol2.Sequence('cd1_sequence', 'GCAT')
        cd.sequence = seq
        self.assertEqual([seq.identity], cd.sequences)

    @unittest.expectedFailure
    def test_sequences_validation(self):
        self.fail('Not yet implemented')


if __name__ == '__main__':
    unittest.main()
