import os
import unittest
import sbol2


MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))

# For testing reading of measurements
MEASURE_LOCATION = os.path.join(MODULE_LOCATION, 'SBOLTestSuite', 'SBOL2',
                                'Measure.xml')


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

    def test_read(self):
        doc = sbol2.Document(MEASURE_LOCATION)
        md_uri = 'http://www.async.ece.utah.edu/md'
        md = doc.getModuleDefinition(md_uri)
        interaction_uri = 'http://www.async.ece.utah.edu/md/i'
        interaction = md.interactions.get(interaction_uri)
        measurement_uri = 'http://www.async.ece.utah.edu/md/i/i_measure'
        measurement = interaction.measurements.get(measurement_uri)
        self.assertIsNotNone(measurement)
        # Expecting this to be a Measurement, for starters
        # This wasn't the case, see issue #304
        self.assertTrue(isinstance(measurement, sbol2.Measurement))
        self.assertEqual(0.04, measurement.value)
        self.assertEqual('http://purl.obolibrary.org/obo/UO_0000077', measurement.unit)


if __name__ == '__main__':
    unittest.main()
