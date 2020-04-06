import os
import unittest
import warnings

import rdflib

import sbol2 as sbol

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

    def test_set_property_value_deprecated(self):
        # Verify that setPropertyValue is deprecated
        md = sbol.ModuleDefinition('md')
        with warnings.catch_warnings(record=True) as warns:
            md.setPropertyValue('myprop', 'foo')
        self.assertEqual(len(warns), 1)

    def test_set_property_value(self):
        # Suppress the deprecation warnings
        with warnings.catch_warnings(record=True) as warns:
            self.deprecated_test_set_property_value()

    def deprecated_test_set_property_value(self):
        my_property = 'http://example.com/myproperty'
        md = sbol.ModuleDefinition('md1')
        # value argument must be of type string. If not, expect type error
        with self.assertRaises(TypeError):
            md.setPropertyValue(my_property, 2)
        with self.assertRaises(TypeError):
            md.setPropertyValue(my_property, ['foo', 'bar'])
        # Test basic setting
        empty_str = ''
        empty_literal = rdflib.Literal(empty_str)
        foo_literal = rdflib.Literal('foo')
        md.setPropertyValue(my_property, foo_literal)
        self.assertEqual(md.getPropertyValue(my_property), foo_literal)
        # Test overwriting a single existing value
        bar_literal = rdflib.Literal('bar')
        md.setPropertyValue(my_property, bar_literal)
        self.assertEqual(md.getPropertyValue(my_property), bar_literal)
        # Test setting an existing multi-value property
        md.properties[rdflib.URIRef(my_property)] = [foo_literal, bar_literal]
        self.assertEqual(md.getPropertyValue(my_property), foo_literal)
        self.assertEqual(md.getPropertyValues(my_property), [foo_literal, bar_literal])
        baz_literal = rdflib.Literal('baz')
        md.setPropertyValue(my_property, baz_literal)
        self.assertEqual(md.getPropertyValue(my_property), baz_literal)
        self.assertEqual(md.getPropertyValues(my_property), [baz_literal, bar_literal])
        # Unset the value
        md.setPropertyValue(my_property, empty_str)
        self.assertEqual(md.getPropertyValue(my_property), empty_literal)
        # This may seem odd, but it is the way pySBOL/libSBOL worked,
        # so we do it for backward compatibility
        self.assertEqual(md.getPropertyValues(my_property), [empty_literal, bar_literal])

        # What about a plain string? Does that get converted to URIRef or Literal?
        #  If a value is present, mimic that value's type
        #  Else make the value a Literal
        foo_str = 'foo'
        bar_str = 'bar'
        foo_uri = rdflib.URIRef(foo_str)
        bar_uri = rdflib.URIRef(bar_str)
        md2 = sbol.ModuleDefinition('md2')
        # String gets converted to Literal
        md2.setPropertyValue(my_property, foo_str)
        self.assertEqual(md2.getPropertyValue(my_property), foo_literal)
        # Ok to overwrite a Literal with a URIRef
        md2.setPropertyValue(my_property, foo_uri)
        self.assertEqual(md2.getPropertyValue(my_property), foo_uri)
        # Now setting a str value should convert it to a URIRef
        # because that's what is already there
        md2.setPropertyValue(my_property, bar_str)
        self.assertEqual(md2.getPropertyValue(my_property), bar_uri)
        # Ok to overwrite a URIRef with a Literal
        md2.setPropertyValue(my_property, foo_literal)
        self.assertEqual(md2.getPropertyValue(my_property), foo_literal)
        # Unsetting the value
        md2.setPropertyValue(my_property, '')
        self.assertEqual(md2.getPropertyValue(my_property), empty_literal)

    def test_serialize_property_value(self):
        # Set a property value to the empty string and verify that it
        # can be serialized and deserialized properly. The underlying
        # question is what does the internal representation need to be
        # to have that happen correctly.
        my_property = 'http://example.com/myproperty'
        empty_str = ''
        empty_literal = rdflib.Literal(empty_str)
        foo_str = 'foo'
        foo_literal = rdflib.Literal(foo_str)
        doc = sbol.Document()
        md = doc.moduleDefinitions.create('md')
        with warnings.catch_warnings(record=True):
            md.setPropertyValue(my_property, foo_str)
        self.assertEqual(md.getPropertyValue(my_property), foo_literal)
        with warnings.catch_warnings(record=True):
            md.setPropertyValue(my_property, empty_str)
        self.assertEqual(md.getPropertyValue(my_property), empty_literal)
        # Now serialize the document to a string
        serialized = doc.writeString()
        doc2 = sbol.Document()
        doc2.readString(serialized)
        self.assertEqual(len(doc2.moduleDefinitions), 1)
        md2 = doc2.moduleDefinitions[0]
        self.assertEqual(md2.displayId, md.displayId)
        self.assertEqual(md2.getPropertyValue(my_property), empty_literal)
