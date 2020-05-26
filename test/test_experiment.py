import unittest

import sbol2


class TestExperiment(unittest.TestCase):

    def test_exported(self):
        self.assertIn('Experiment', dir(sbol2))
        self.assertIn('ExperimentalData', dir(sbol2))


if __name__ == '__main__':
    unittest.main()
