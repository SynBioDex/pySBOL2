import unittest
import sbol2


class TestMeasurement(unittest.TestCase):

    def test_add_remove_type(self):
        measurement = sbol2.Measurement()
        self.assertEqual([], measurement.types)
        measurement.addType(sbol2.BIOPAX_DNA)
        self.assertEqual([sbol2.BIOPAX_DNA], measurement.types)
        measurement.addType(sbol2.BIOPAX_RNA)
        self.assertEqual([sbol2.BIOPAX_DNA, sbol2.BIOPAX_RNA], measurement.types)
        measurement.addType(sbol2.BIOPAX_COMPLEX)
        expected = [sbol2.BIOPAX_DNA, sbol2.BIOPAX_RNA, sbol2.BIOPAX_COMPLEX]
        self.assertEqual(expected, measurement.types)
        measurement.removeType(1)
        self.assertEqual([sbol2.BIOPAX_DNA, sbol2.BIOPAX_COMPLEX], measurement.types)


if __name__ == '__main__':
    unittest.main()
