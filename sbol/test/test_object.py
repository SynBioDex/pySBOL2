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

    def test_compare(self):
        # This didn't work because the SBOLObject.__eq__ method was
        # broken.  See issue https://github.com/llotneb/SBOL/issues/62
        sbol.setHomespace('http://example.org/Unit_Test')
        doc = sbol.Document()
        md1 = doc.moduleDefinitions.create('Foo1')
        self.assertEqual(len(doc.moduleDefinitions), 1)
        md2 = doc.moduleDefinitions.create('Foo2')
        self.assertEqual(len(doc.moduleDefinitions), 2)

    def test_eq(self):
        sbol.setHomespace('http://example.org/Unit_Test')
        doc = sbol.Document()
        md1 = doc.moduleDefinitions.create('Foo1')
        self.assertEqual(len(doc.moduleDefinitions), 1)
        md2 = sbol.ModuleDefinition(uri='Foo2')
        self.assertNotEqual(md1, md2)


if __name__ == '__main__':
    unittest.main()
