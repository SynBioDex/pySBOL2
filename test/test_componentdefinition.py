import os
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
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        expected = 'BB0001'
        test_CD = sbol2.ComponentDefinition(expected)
        doc = sbol2.Document()
        doc.addComponentDefinition(test_CD)
        self.assertIsNotNone(doc.componentDefinitions.get(expected))
        displayId = doc.componentDefinitions.get(expected).displayId
        self.assertEqual(displayId, expected)

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
        doc = sbol2.Document()
        doc.read(CRISPR_EXAMPLE)
        # List of displayIds
        expected = ['CRP_b', 'CRa_U6', 'EYFP', 'EYFP_cds', 'EYFP_gene',
                    'Gal4VP16', 'Gal4VP16_cds', 'Gal4VP16_gene',
                    'cas9_gRNA_complex', 'cas9_generic',
                    'cas9m_BFP', 'cas9m_BFP_cds',
                    'cas9m_BFP_gRNA_b', 'cas9m_BFP_gene',
                    'gRNA_b', 'gRNA_b_gene', 'gRNA_b_nc', 'gRNA_b_terminator',
                    'gRNA_generic', 'mKate', 'mKate_cds', 'mKate_gene',
                    'pConst', 'target', 'target_gene']
        actual = [cd.displayId for cd in doc.componentDefinitions]
        self.assertCountEqual(actual, expected)

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
        self.assertCountEqual(list_cd, list_cd_true)

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

    def testHasUpstreamComponent(self):
        uri = 'http://sbols.org/CRISPR_Example/gRNA_b_gene/1.0.0'
        doc = sbol2.Document()
        doc.read(CRISPR_EXAMPLE)
        cd = doc.componentDefinitions.get(uri)
        self.assertIsNotNone(cd)
        # First element, has no upstream component
        uri = 'http://sbols.org/CRISPR_Example/gRNA_b_gene/CRa_U6/1.0.0'
        c = cd.components.get(uri)
        self.assertFalse(cd.hasUpstreamComponent(c))
        # Second element has above as upstream component
        uri = 'http://sbols.org/CRISPR_Example/gRNA_b_gene/gRNA_b_nc/1.0.0'
        c = cd.components.get(uri)
        self.assertTrue(cd.hasUpstreamComponent(c))
        # Third element has both above as upstream components
        uri = 'http://sbols.org/CRISPR_Example/gRNA_b_gene/gRNA_b_terminator/1.0.0'
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
        graph.parse(data=xml, format='xml')
        # We shouldn't find SBOL_SEQUENCE within the component definition
        identity_uri = rdflib.URIRef(cd.identity)
        bad_triple = (identity_uri, rdflib.URIRef(sbol2.SBOL_SEQUENCE), None)
        self.assertEqual([], list(graph.triples(bad_triple)))
        good_triple = (identity_uri, rdflib.URIRef(sbol2.SBOL_SEQUENCE_PROPERTY), None)
        good_triples = list(graph.triples(good_triple))
        self.assertEqual(len(good_triples), 1)
        self.assertEqual(good_triples[0], (identity_uri,
                                           rdflib.URIRef(sbol2.SBOL_SEQUENCE_PROPERTY),
                                           rdflib.URIRef(seq.identity)))

    def test_remove_hidden_sequence(self):
        # Objects contained in a hidden property shouldn't persist if they are
        # removed from the Document top level
        doc = sbol2.Document()
        cd = doc.componentDefinitions.create('cd1')
        cd.sequence = sbol2.Sequence('cd1_sequence')
        self.assertIn('cd1_sequence', doc.sequences)
        doc.sequences.remove('cd1_sequence')
        self.assertIsNone(cd.sequence)

    def test_sequence_validation(self):
        # sequence and sequences should be synced up
        cd = sbol2.ComponentDefinition('cd1', sbol2.BIOPAX_DNA)
        seq = sbol2.Sequence('cd1_sequence', 'GCAT')
        cd.sequence = seq
        self.assertEqual([cd.sequence.identity], cd.sequences)

    def test_nonexistent_sequence(self):
        # If a ComponentDefinition is in a Document and has a URI in
        # sequences that is not in the document,
        # ComponentDefinition.sequence should return None.
        doc = sbol2.Document()
        cd = sbol2.ComponentDefinition('cd')
        doc.add(cd)
        cd.sequences = ['http://example.com/sbol2/sequence/1']
        self.assertIsNone(cd.sequence)

    def test_hidden_property_adder(self):
        # Assignment of a TopLevel object to a hidden property (in this case
        # assigning a Sequence object to the sequence property) should
        # simultaneously add that object to the Document top level
        doc = sbol2.Document()
        cd = doc.componentDefinitions.create('cd')
        cd.sequence = sbol2.Sequence('seq')
        self.assertIsNotNone(cd.sequence)
        self.assertIs(cd.sequence, doc.getSequence(cd.sequence.identity))


class TestAssemblyRoutines(unittest.TestCase):

    def test_inspect_primary_structure(self):
        # Test that components can be retrieved in the sequential order specified by
        # SequenceContraint relationships
        doc = sbol2.Document()
        cd_root = doc.componentDefinitions.create('root')
        c0 = cd_root.components.create('c0')
        c1 = cd_root.components.create('c1')
        c2 = cd_root.components.create('c2')

        # The following components are created in reverse order for purposes of
        # validating the hasUpstreamComponent and getUpstreamComponent methods
        cd2 = doc.componentDefinitions.create('cd2')
        cd1 = doc.componentDefinitions.create('cd1')
        cd0 = doc.componentDefinitions.create('cd0')

        c0.definition = cd0
        c1.definition = cd1
        c2.definition = cd2
        sc0 = cd_root.sequenceConstraints.create('sc0')
        sc1 = cd_root.sequenceConstraints.create('sc1')
        sc0.subject = c0
        sc0.object = c1
        sc1.subject = c1
        sc1.object = c2
        self.assertEqual(cd_root.hasUpstreamComponent(c0), False)
        self.assertEqual(cd_root.hasUpstreamComponent(c1), True)
        self.assertEqual(cd_root.getUpstreamComponent(c2), c1)

        self.assertEqual(cd_root.hasDownstreamComponent(c2), False)
        self.assertEqual(cd_root.hasDownstreamComponent(c1), True)
        self.assertEqual(cd_root.getDownstreamComponent(c0), c1)

        self.assertEqual(cd_root.getFirstComponent(), c0)
        self.assertEqual(cd_root.getLastComponent(), c2)
        self.assertEqual(cd_root.getPrimaryStructureComponents(), [c0, c1, c2])
        self.assertEqual(cd_root.getPrimaryStructure(), [cd0, cd1, cd2])

    def test_assemble(self):
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        RBS = sbol2.ComponentDefinition("B0032")
        CDS = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        promoter.sequence = sbol2.Sequence('R0010')
        RBS.sequence = sbol2.Sequence('B0032')
        CDS.sequence = sbol2.Sequence('E0040')
        terminator.sequence = sbol2.Sequence('B0012')

        promoter.sequence.elements = 'a'
        RBS.sequence.elements = 't'
        CDS.sequence.elements = 'c'
        terminator.sequence.elements = 'g'

        promoter.roles = sbol2.SO_PROMOTER
        RBS.roles = sbol2.SO_RBS
        CDS.roles = sbol2.SO_CDS
        terminator.roles = sbol2.SO_TERMINATOR

        doc.addComponentDefinition([gene, promoter, RBS, CDS, terminator])
        gene.assemblePrimaryStructure(['R0010', 'B0032', 'E0040', 'B0012'])
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [c.identity for c in primary_structure]

        self.assertEqual(primary_structure, [promoter.identity, RBS.identity,
                         CDS.identity, terminator.identity])

    def test_compile_sequence(self):
        doc = sbol2.Document()
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        CDS = sbol2.ComponentDefinition("B0032")
        RBS = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")
        scar = sbol2.ComponentDefinition('scar')

        promoter.sequence = sbol2.Sequence('R0010')
        RBS.sequence = sbol2.Sequence('B0032')
        CDS.sequence = sbol2.Sequence('E0040')
        terminator.sequence = sbol2.Sequence('B0012')
        scar.sequence = sbol2.Sequence('scar')

        promoter.sequence.elements = 'aaa'
        RBS.sequence.elements = 'aaa'
        CDS.sequence.elements = 'aaa'
        terminator.sequence.elements = 'aaa'
        scar.sequence.elements = 'ttt'

        doc.addComponentDefinition(gene)
        gene.assemblePrimaryStructure([promoter, scar, RBS, scar, CDS, scar,
                                      terminator])
        target_seq = gene.compile()

        self.assertEqual(target_seq, 'aaatttaaatttaaatttaaa')
        self.assertEqual(target_seq, gene.sequence.elements)

    def test_compile_autoconstruct_sequence(self):
        # Ensure that autoconstruction of Sequence URIs works correctly with
        # different configuration options
        root_id = 'root'
        sub_id = 'sub'
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)
        doc = sbol2.Document()
        root = doc.componentDefinitions.create(root_id)
        sub = doc.componentDefinitions.create(sub_id)
        root.compile([sub])
        expected_identity = sbol2.getHomespace() + '/Sequence/' + root_id + '/1'
        self.assertEqual(root.sequence.identity, expected_identity)

        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        doc = sbol2.Document()
        root = doc.componentDefinitions.create(root_id)
        sub = doc.componentDefinitions.create(sub_id)
        root.compile([sub])
        expected_identity = sbol2.getHomespace() + '/' + root_id + '_seq/1'
        self.assertEqual(root.sequence.identity, expected_identity)

        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)

    def test_recursive_compile(self):
        doc = sbol2.Document()
        cd1 = sbol2.ComponentDefinition('cd1')
        cd2 = sbol2.ComponentDefinition('cd2')
        cd3 = sbol2.ComponentDefinition('cd3')
        cd4 = sbol2.ComponentDefinition('cd4')
        cd5 = sbol2.ComponentDefinition('cd5')
        cd1.sequence = sbol2.Sequence('cd1')
        cd2.sequence = sbol2.Sequence('cd2')
        cd3.sequence = sbol2.Sequence('cd3')
        cd4.sequence = sbol2.Sequence('cd4')
        cd5.sequence = sbol2.Sequence('cd5')
        cd1.sequence.elements = 'tt'
        cd2.sequence.elements = 'gg'
        cd3.sequence.elements = 'n'
        cd4.sequence.elements = 'aa'
        cd5.sequence.elements = 'n'
        doc.addComponentDefinition([cd1, cd2, cd3, cd4, cd5])
        cd3.assemblePrimaryStructure([cd1, cd2])
        cd5.assemblePrimaryStructure([cd4, cd3])
        cd5.compile()
        self.assertEqual(cd3.sequence.elements, 'ttgg')
        self.assertEqual(cd5.sequence.elements, 'aattgg')
        r1 = cd3.sequenceAnnotations['cd1_annotation_0'].\
            locations['cd1_annotation_0_range']
        r2 = cd3.sequenceAnnotations['cd2_annotation_0'].\
            locations['cd2_annotation_0_range']
        r4 = cd5.sequenceAnnotations['cd4_annotation_0'].\
            locations['cd4_annotation_0_range']
        self.assertEqual(r1.start, 3)
        self.assertEqual(r1.end, 4)
        self.assertEqual(r2.start, 5)
        self.assertEqual(r2.end, 6)
        self.assertEqual(r4.start, 1)
        self.assertEqual(r4.end, 2)

    def test_standard_assembly(self):
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        RBS = sbol2.ComponentDefinition("B0032")
        CDS = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        promoter.sequence = sbol2.Sequence('R0010')
        RBS.sequence = sbol2.Sequence('B0032')
        CDS.sequence = sbol2.Sequence('E0040')
        terminator.sequence = sbol2.Sequence('B0012')

        promoter.sequence.elements = 'a'
        RBS.sequence.elements = 't'
        CDS.sequence.elements = 'c'
        terminator.sequence.elements = 'g'

        promoter.roles = sbol2.SO_PROMOTER
        RBS.roles = sbol2.SO_RBS
        CDS.roles = sbol2.SO_CDS
        terminator.roles = sbol2.SO_TERMINATOR

        doc.addComponentDefinition(gene)
        gene.assemblePrimaryStructure([promoter, RBS, CDS, terminator],
                                      sbol2.IGEM_STANDARD_ASSEMBLY)
        target_seq = gene.compile()

        self.assertEqual(target_seq, 'atactagagttactagctactagagg')

    def test_assemble_with_displayIds(self):
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)

        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        RBS = sbol2.ComponentDefinition("B0032")
        CDS = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        promoter.sequence = sbol2.Sequence('R0010')
        RBS.sequence = sbol2.Sequence('B0032')
        CDS.sequence = sbol2.Sequence('E0040')
        terminator.sequence = sbol2.Sequence('B0012')

        promoter.sequence.elements = 'a'
        RBS.sequence.elements = 't'
        CDS.sequence.elements = 'c'
        terminator.sequence.elements = 'g'

        promoter.roles = sbol2.SO_PROMOTER
        RBS.roles = sbol2.SO_RBS
        CDS.roles = sbol2.SO_CDS
        terminator.roles = sbol2.SO_TERMINATOR

        doc.addComponentDefinition([gene, promoter, RBS, CDS, terminator])
        gene.assemblePrimaryStructure(['R0010', 'B0032', 'E0040', 'B0012'])
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [c.identity for c in primary_structure]
        self.assertEqual(primary_structure, [promoter.identity, RBS.identity,
                         CDS.identity, terminator.identity])

        target_seq = gene.compile()
        self.assertEqual(target_seq, 'atcg')

    def test_assembly_multiple_sequenceannotations(self):
        # Currently hierarchical assembly of Components with multiple SequenceAnnotations
        # is not supported, and an exception will be thrown if the user attempts it
        doc = sbol2.Document()
        root = doc.componentDefinitions.create('root')
        sub0 = doc.componentDefinitions.create('sub0')
        sub1 = doc.componentDefinitions.create('sub1')

        sub0.sequence = sbol2.Sequence('sub0', 'tttt')
        sub1.sequence = sbol2.Sequence('sub1', 'aa')
        root.assemblePrimaryStructure([sub0, sub1])
        root.compile()

        # Add a second SequenceAnnotation
        sa = root.sequenceAnnotations.create('sub0_annotation_1')
        sa.component = root.components['sub0_0']
        with self.assertRaises(sbol2.SBOLError) as err:
            root.compile()
        self.assertEqual(err.exception.error_code(),
                         sbol2.SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT)

    def test_assembly_multiple_ranges(self):
        # Currently hierarchical assembly of Components with multiple Ranges
        # is not supported, and an exception will be thrown if the user attempts it
        doc = sbol2.Document()
        root = doc.componentDefinitions.create('root')
        sub0 = doc.componentDefinitions.create('sub0')
        sub1 = doc.componentDefinitions.create('sub1')

        sub0.sequence = sbol2.Sequence('sub0', 'tttt')
        sub1.sequence = sbol2.Sequence('sub1', 'aa')
        root.assemblePrimaryStructure([sub0, sub1])

        sub0_0 = root.components['sub0_0']
        sub1_0 = root.components['sub1_0']
        sa0 = root.sequenceAnnotations.create('sa0')
        sa0.component = sub0_0
        r0 = sa0.locations.createRange('r0')
        r1 = sa0.locations.createRange('r1')
        sa1 = root.sequenceAnnotations.create('sa1')
        sa1.component = sub1_0
        r2 = sa1.locations.createRange('r2')
        r0.start = 1
        r0.end = 2
        r1.start = 3
        r1.end = 4
        r2.start = 5
        r2.end = 6
        with self.assertRaises(sbol2.SBOLError) as err:
            root.compile()
        self.assertEqual(err.exception.error_code(),
                         sbol2.SBOLErrorCode.SBOL_ERROR_INVALID_ARGUMENT)

    def test_delete_upstream(self):
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        rbs = sbol2.ComponentDefinition("B0032")
        cds = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        doc.addComponentDefinition([gene, promoter, rbs, cds, terminator])
        gene.assemblePrimaryStructure([promoter, rbs, cds, terminator])
        primary_structure_components = gene.getPrimaryStructureComponents()
        c_promoter = primary_structure_components[0]
        c_rbs = primary_structure_components[1]
        c_cds = primary_structure_components[2]
        c_terminator = primary_structure_components[3]

        gene.deleteUpstreamComponent(c_cds)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [promoter.identity, cds.identity,
                                   terminator.identity]
        self.assertEqual(primary_structure, valid_primary_structure)

        # Test deletion when the target Component is the first Component
        gene.deleteUpstreamComponent(c_cds)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [cds.identity, terminator.identity]
        self.assertEqual(primary_structure, valid_primary_structure)

        # Test failure when user tries to delete a Component upstream of the first
        # Component
        with self.assertRaises(ValueError):
            gene.deleteUpstreamComponent(c_promoter)
        # Test failure when the user supplies a Component that isn't part of the
        # primary structure
        with self.assertRaises(ValueError):
            gene.deleteUpstreamComponent(sbol2.Component())

    def test_delete_downstream(self):
        doc = sbol2.Document()
        gene = sbol2.ComponentDefinition("BB0001")
        promoter = sbol2.ComponentDefinition("R0010")
        rbs = sbol2.ComponentDefinition("B0032")
        cds = sbol2.ComponentDefinition("E0040")
        terminator = sbol2.ComponentDefinition("B0012")

        doc.addComponentDefinition([gene, promoter, rbs, cds, terminator])
        gene.assemblePrimaryStructure([promoter, rbs, cds, terminator])
        primary_structure_components = gene.getPrimaryStructureComponents()
        c_promoter = primary_structure_components[0]
        c_rbs = primary_structure_components[1]
        c_cds = primary_structure_components[2]
        c_terminator = primary_structure_components[3]

        gene.deleteDownstreamComponent(c_rbs)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [promoter.identity, rbs.identity,
                                   terminator.identity]
        self.assertEqual(primary_structure, valid_primary_structure)

        # Test deletion when the target Component is the last Component
        gene.deleteDownstreamComponent(c_rbs)
        primary_structure = gene.getPrimaryStructure()
        primary_structure = [cd.identity for cd in primary_structure]
        valid_primary_structure = [promoter.identity, rbs.identity]
        self.assertEqual(primary_structure, valid_primary_structure)

        # Test failure when user tries to delete Component upstream of the first
        # Component
        with self.assertRaises(ValueError):
            gene.deleteDownstreamComponent(c_cds)
        # Test failure when the user supplies a Component that isn't part of the
        # primary structure
        with self.assertRaises(ValueError):
            gene.deleteDownstreamComponent(sbol2.Component())

    def test_insert_downstream(self):
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
        valid_primary_structure = [promoter.identity, rbs.identity, cds.identity,
                                   terminator.identity]
        self.assertEqual(primary_structure, valid_primary_structure)

    def test_insert_upstream(self):
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
        valid_primary_structure = [promoter.identity, rbs.identity, cds.identity,
                                   terminator.identity]
        self.assertEqual(primary_structure, valid_primary_structure)

    def test_add_remove_role(self):
        cd = sbol2.ComponentDefinition('c1')
        self.assertEqual([], cd.roles)
        cd.addRole(sbol2.SO_PROMOTER)
        self.assertEqual([sbol2.SO_PROMOTER], cd.roles)
        cd.addRole(sbol2.SO_MISC)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC], cd.roles)
        cd.addRole(sbol2.SO_CDS)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC, sbol2.SO_CDS], cd.roles)
        cd.removeRole(1)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_CDS], cd.roles)

    def test_add_remove_type(self):
        cd = sbol2.ComponentDefinition('c1')
        self.assertEqual([sbol2.BIOPAX_DNA], cd.types)
        cd.addType(sbol2.BIOPAX_RNA)
        self.assertEqual([sbol2.BIOPAX_DNA, sbol2.BIOPAX_RNA], cd.types)
        cd.addType(sbol2.BIOPAX_COMPLEX)
        expected = [sbol2.BIOPAX_DNA, sbol2.BIOPAX_RNA, sbol2.BIOPAX_COMPLEX]
        self.assertEqual(expected, cd.types)
        cd.removeType(1)
        self.assertEqual([sbol2.BIOPAX_DNA, sbol2.BIOPAX_COMPLEX], cd.types)


if __name__ == '__main__':
    unittest.main()
