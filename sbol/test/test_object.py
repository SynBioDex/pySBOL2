import os
import unittest

import sbol

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
PARTS_LOCATION = os.path.join(MODULE_LOCATION, 'resources', 'tutorial',
                              'parts.xml')


class TestObject(unittest.TestCase):

    def test_getPropertyValues(self):
        d = sbol.Document()
        d.read(PARTS_LOCATION)
        cd = d.componentDefinitions['http://examples.org/ComponentDefinition/AmeR/1']
        values = cd.getPropertyValues(sbol.SBOL_NAME)
        self.assertEqual(len(values), 1)

    def test_getPropertyValue(self):
        d = sbol.Document()
        d.read(PARTS_LOCATION)
        cd = d.componentDefinitions['http://examples.org/ComponentDefinition/AmeR/1']
        expected = 'AmeR'
        name = cd.getPropertyValue(sbol.SBOL_NAME)
        self.assertEqual(name, expected)


if __name__ == '__main__':
    unittest.main()
