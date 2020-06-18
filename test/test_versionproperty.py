import unittest

import sbol2


class TestVersionProperty(unittest.TestCase):

    def test_values(self):
        cd = sbol2.ComponentDefinition('cd1')
        self.assertEqual('1', cd.version)
        with self.assertRaises(ValueError):
            cd.version = 'tom'
        with self.assertRaises(ValueError):
            # Floats are not acceptable, must be a string
            cd.version = 1.2
        v = '2'
        cd.version = v
        self.assertEqual(v, cd.version)
        v = '2.3'
        cd.version = v
        self.assertEqual(v, cd.version)
        v = '2.3.1'
        cd.version = v
        self.assertEqual(v, cd.version)


if __name__ == '__main__':
    unittest.main()
