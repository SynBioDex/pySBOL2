import unittest
from sbol.document import *
from sbol.config import *
import os
import sys

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
CRISPR_EXAMPLE = os.path.join(MODULE_LOCATION, 'resources', 'crispr_example.xml')

class TestSequence(unittest.TestCase):

    def setUp(self):
        pass

    def testAddSequence(self):
        test_seq = Sequence("R0010", "ggctgca")
        doc = Document()
        doc.addSequence(test_seq)
        seq = doc.sequences.get("R0010").elements

        self.assertEqual(seq, 'ggctgca')

    def testRemoveSequence(self):
        test_seq = Sequence("R0010", "ggctgca")
        doc = Document()
        doc.addSequence(test_seq)
        doc.sequences.remove(0)
        self.assertRaises(SBOLError, lambda: doc.sequences.get("R0010"))

    def testSeqDisplayId(self):
        doc = Document()
        doc.read(CRISPR_EXAMPLE)

        # List of displayIds
        listseq = ['CRP_b_seq', 'CRa_U6_seq', 'gRNA_b_seq', 'mKate_seq']
        listseq = [rdflib.Literal(x) for x in listseq]

        listseq_read = [seq.displayId for seq in doc.sequences]

        self.assertCountEqual(listseq_read, listseq)

    def testSequenceElement(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_typed_uris', False)
        doc = Document()
        doc.read(os.path.join(MODULE_LOCATION, 'resources/crispr_example.xml'))
        # Sequence to test against
        seq = ('GCTCCGAATTTCTCGACAGATCTCATGTGATTACGCCAAGCTACGGGCGGAGTACTGTCCTC'
               'CGAGCGGAGTACTGTCCTCCGAGCGGAGTACTGTCCTCCGAGCGGAGTACTGTCCTCCGAGC'
               'GGAGTTCTGTCCTCCGAGCGGAGACTCTAGATACCTCATCAGGAACATGTTGGAATTCTAGG'
               'CGTGTACGGTGGGAGGCCTATATAAGCAGAGCTCGTTTAGTGAACCGTCAGATCGCCTCGAG'
               'TACCTCATCAGGAACATGTTGGATCCAATTCGACC')

        seq_read = doc.sequences.get('CRP_b_seq').elements
        self.assertEquals(seq_read, seq)

    def testUpdateSequenceElement(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_typed_uris', False)
        doc = Document()
        doc.read(os.path.join(MODULE_LOCATION, 'resources/crispr_example.xml'))
        # Sequence to test against
        seq = 'AAAAA'
        doc.sequences.get('CRP_b_seq').elements = seq
        seq_read = doc.sequences.get('CRP_b_seq').elements
        self.assertEquals(seq_read, seq)

    # File I/O Tests
    def testUpdateWrite(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_typed_uris', False)
        doc = Document()
        doc.read(os.path.join(MODULE_LOCATION, 'resources/crispr_example.xml'))
        # Sequence to test against
        seq = 'AAAAA'
        doc.sequences.get('CRP_b_seq').elements = seq
        # Write to disk
        doc.write('test.xml')
        # Compare
        doc2 = Document()  # Document to compare for equality
        doc2.read('test.xml')
        seq_read = doc2.sequences.get('CRP_b_seq').elements
        self.assertEquals(seq_read, seq)


if __name__ == '__main__':
    unittest.main()
