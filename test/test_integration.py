import unittest

from sbol2 import *


class TestIntegrate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        setHomespace('https://example.com')

    def setUp(self):
        self.doc = Document()
        self.wt_cd = ComponentDefinition('wt_cd')
        self.wt_cd.sequence = Sequence('wt_seq')
        self.insert_cd = ComponentDefinition('insert_cd')
        self.insert_cd.sequence = Sequence('insert_seq')
        self.integrated_cd = ComponentDefinition('integrated_cd')
        self.doc.addComponentDefinition([self.integrated_cd, self.insert_cd, self.wt_cd])

    def testSourceLocation(self):
        # Test insertion splits the targt ComponentDefinition
        # into 2 Components each with a SourceLocation
        self.wt_cd.sequence.elements = 'atcg'
        self.insert_cd.sequence.elements = 'gg'
        self.integrated_cd.integrateAtBaseCoordinate(self.wt_cd, self.insert_cd, 3)
        components = [c for c in self.integrated_cd.components
                      if c.definition == self.wt_cd.identity]
        self.assertEqual(len(components), 2)
        self.assertEqual(len(components[0].sourceLocations), 1)
        self.assertEqual(len(components[1].sourceLocations), 1)
        l0 = components[0].sourceLocations.getRange()
        l1 = components[1].sourceLocations.getRange()
        self.assertEqual(l0.start, 1)
        self.assertEqual(l0.end, 2)
        self.assertEqual(l1.start, 3)
        self.assertEqual(l1.end, 4)

    def testIntegrationPrimaryStructure(self):
        self.wt_cd.sequence.elements = 'atcg'
        self.insert_cd.sequence.elements = 'gg'
        self.integrated_cd.integrateAtBaseCoordinate(self.wt_cd, self.insert_cd, 3)
        primary_structure = self.integrated_cd.getPrimaryStructure()
        primary_structure = [c.identity for c in primary_structure]
        self.assertListEqual(primary_structure, [self.wt_cd.identity,
                                                 self.insert_cd.identity,
                                                 self.wt_cd.identity])

    def testIntegrationNegative(self):
        # An exception should be raised if user tries to insert
        # at a negative base coordinate
        with self.assertRaises(ValueError):
            self.wt_cd.sequence.elements = 'atcg'
            self.insert_cd.sequence.elements = 'gg'
            self.integrated_cd.integrateAtBaseCoordinate(self.wt_cd, self.insert_cd, -3)

    def testIntegrationPositive(self):
        # An exception should be raised if the user attempts to
        # appending at a location beyond the end of the initial
        # sequence.
        with self.assertRaises(ValueError):
            self.wt_cd.sequence.elements = 'atcg'
            self.insert_cd.sequence.elements = 'gg'
            self.integrated_cd.integrateAtBaseCoordinate(self.wt_cd, self.insert_cd, 8)

    def testIntegration0(self):
        # An exception should be raised if user tries to insert
        # at 0 base coordinate. Base coordinates are indexed from 1
        with self.assertRaises(ValueError):
            self.wt_cd.sequence.elements = 'atcg'
            self.insert_cd.sequence.elements = 'gg'
            self.integrated_cd.integrateAtBaseCoordinate(self.wt_cd, self.insert_cd, 0)

    def testIntegration1(self):
        # Test inserting at the beginning of the sequence. Prepending.
        self.wt_cd.sequence.elements = 'atcg'
        self.insert_cd.sequence.elements = 'gg'
        self.integrated_cd.integrateAtBaseCoordinate(self.wt_cd, self.insert_cd, 1)
        self.integrated_cd.compile()
        self.assertEqual(self.integrated_cd.sequence.elements, 'ggatcg')

    def testIntegration2(self):
        # Test inserting within the sequence.
        self.wt_cd.sequence.elements = 'atcg'
        self.insert_cd.sequence.elements = 'gg'
        self.integrated_cd.integrateAtBaseCoordinate(self.wt_cd, self.insert_cd, 2)
        self.integrated_cd.compile()
        self.assertEqual(self.integrated_cd.sequence.elements, 'aggtcg')

    def testIntegration3(self):
        # Test inserting within the sequence.
        self.wt_cd.sequence.elements = 'atcg'
        self.insert_cd.sequence.elements = 'gg'
        self.integrated_cd.integrateAtBaseCoordinate(self.wt_cd, self.insert_cd, 3)
        self.integrated_cd.compile()
        self.assertEqual(self.integrated_cd.sequence.elements, 'atggcg')

    def testIntegration4(self):
        # Test inserting one base before the end of the sequence.
        self.wt_cd.sequence.elements = 'atcg'
        self.insert_cd.sequence.elements = 'gg'
        self.integrated_cd.integrateAtBaseCoordinate(self.wt_cd, self.insert_cd, 4)
        self.integrated_cd.compile()
        self.assertEqual(self.integrated_cd.sequence.elements, 'atcggg')

    def testIntegrationN(self):
        # Test appending at the end of the initial sequence.
        self.wt_cd.sequence.elements = 'atcg'
        self.insert_cd.sequence.elements = 'gg'
        self.integrated_cd.integrateAtBaseCoordinate(self.wt_cd, self.insert_cd, 5)
        self.integrated_cd.compile()
        self.assertEqual(self.integrated_cd.sequence.elements, 'atcggg')

    def testMissingDocument(self):
        # Test that compile fails with a raised exception when
        # this CD or the insert is not associated with a Document
        self.wt_cd.sequence.elements = 'atcg'
        self.insert_cd.sequence.elements = 'gg'
        self.wt_cd = self.doc.componentDefinitions.remove(self.wt_cd.identity)
        with self.assertRaises(ValueError):
            self.integrated_cd.integrateAtBaseCoordinate(self.wt_cd, self.insert_cd, 4)
        self.doc.componentDefinitions.add(self.wt_cd)
        self.insert_cd = self.doc.componentDefinitions.remove(self.insert_cd.identity)
        with self.assertRaises(ValueError):
            self.integrated_cd.integrateAtBaseCoordinate(self.wt_cd, self.insert_cd, 4)
