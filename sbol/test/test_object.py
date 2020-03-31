import os
import unittest
import warnings

import rdflib

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
        expected = rdflib.Literal('AmeR')
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

    def test_type(self):
        cd = sbol.ComponentDefinition('foo')
        expected = sbol.SBOL_COMPONENT_DEFINITION
        self.assertEqual(cd.type, expected)
        doc = sbol.Document()
        md = doc.moduleDefinitions.create('bar')
        expected = sbol.SBOL_MODULE_DEFINITION
        self.assertEqual(md.type, expected)

    def test_cast(self):
        cd = sbol.ComponentDefinition('foo')
        cd2 = cd.cast(sbol.ComponentDefinition)
        self.assertEqual(cd, cd2)
        with self.assertRaises(TypeError):
            cd.cast(sbol.ModuleDefinition)
