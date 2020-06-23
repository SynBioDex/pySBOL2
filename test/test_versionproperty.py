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

    def test_init_store(self):
        # Ensure that property constructors initialize the parent
        # object's value store
        obj = sbol2.SBOLObject()
        type_uri = 'http://example.com#thing'
        obj.thing = sbol2.VersionProperty(obj, type_uri, '0', '*')
        self.assertIn(type_uri, obj.properties)
        self.assertEqual([], obj.properties[type_uri])
        self.assertEqual([], obj.thing)


if __name__ == '__main__':
    unittest.main()
