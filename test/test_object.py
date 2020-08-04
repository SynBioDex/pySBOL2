import collections
import os
import unittest
import warnings

import rdflib

import sbol2
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
        expected = 'AmeR'
        name = cd.getPropertyValue(sbol.SBOL_NAME)
        self.assertEqual(name, expected)

    def test_compare(self):
        # This didn't work because the SBOLObject.__eq__ method was
        # broken.  See issue #62.
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
        # The bottom line is that SBOLObject.getPropertyValue() always
        # returns a string. That's what pysbol did, and what sbol2
        # should do.
        my_property = 'http://example.com/myproperty'
        md = sbol.ModuleDefinition('md1')
        # value argument must be of type string. If not, expect type error
        with self.assertRaises(TypeError):
            md.setPropertyValue(my_property, 2)
        foo_str = 'foo'
        bar_str = 'bar'
        with self.assertRaises(TypeError):
            md.setPropertyValue(my_property, [foo_str, bar_str])
        # Test basic setting
        empty_str = ''
        foo_literal = rdflib.Literal(foo_str)
        md.setPropertyValue(my_property, foo_literal)
        self.assertEqual(md.getPropertyValue(my_property), foo_str)
        # Test overwriting a single existing value
        md.setPropertyValue(my_property, bar_str)
        self.assertEqual(md.getPropertyValue(my_property), bar_str)
        # Test setting an existing multi-value property
        md.properties[rdflib.URIRef(my_property)] = [foo_str, bar_str]
        self.assertEqual(md.getPropertyValue(my_property), foo_str)
        self.assertEqual(md.getPropertyValues(my_property), [foo_str, bar_str])
        baz_str = 'baz'
        md.setPropertyValue(my_property, baz_str)
        self.assertEqual(md.getPropertyValue(my_property), baz_str)
        self.assertEqual([baz_str, bar_str], md.getPropertyValues(my_property))
        # Unset the value
        md.setPropertyValue(my_property, empty_str)
        self.assertEqual(md.getPropertyValue(my_property), empty_str)
        # This may seem odd, but it is the way pySBOL/libSBOL worked,
        # so we do it for backward compatibility
        self.assertEqual([empty_str, bar_str], md.getPropertyValues(my_property))

        # What about a plain string? Does that get converted to URIRef or Literal?
        #  If a value is present, mimic that value's type
        #  Else make the value a Literal
        foo_uri = rdflib.URIRef(foo_str)
        md2 = sbol.ModuleDefinition('md2')
        # String gets converted to Literal
        md2.setPropertyValue(my_property, foo_str)
        self.assertEqual(md2.getPropertyValue(my_property), foo_str)
        # Ok to overwrite a Literal with a URIRef
        md2.setPropertyValue(my_property, foo_uri)
        self.assertEqual(md2.getPropertyValue(my_property), foo_str)
        # Now setting a str value should convert it to a URIRef
        # because that's what is already there
        md2.setPropertyValue(my_property, bar_str)
        self.assertEqual(md2.getPropertyValue(my_property), bar_str)
        # Ok to overwrite a URIRef with a Literal
        md2.setPropertyValue(my_property, foo_literal)
        self.assertEqual(md2.getPropertyValue(my_property), foo_str)
        # Unsetting the value
        md2.setPropertyValue(my_property, '')
        self.assertEqual(md2.getPropertyValue(my_property), empty_str)

    def test_serialize_property_value(self):
        # Set a property value to the empty string and verify that it
        # can be serialized and deserialized properly. The underlying
        # question is what does the internal representation need to be
        # to have that happen correctly.
        my_property = 'http://example.com/myproperty'
        empty_str = ''
        foo_str = 'foo'
        doc = sbol.Document()
        md = doc.moduleDefinitions.create('md')
        with warnings.catch_warnings(record=True):
            md.setPropertyValue(my_property, foo_str)
        self.assertEqual(md.getPropertyValue(my_property), foo_str)
        with warnings.catch_warnings(record=True):
            md.setPropertyValue(my_property, empty_str)
        self.assertEqual(md.getPropertyValue(my_property), empty_str)
        # Now serialize the document to a string
        serialized = doc.writeString()
        doc2 = sbol.Document()
        doc2.readString(serialized)
        self.assertEqual(len(doc2.moduleDefinitions), 1)
        md2 = doc2.moduleDefinitions[0]
        self.assertEqual(md2.displayId, md.displayId)
        self.assertEqual(md2.getPropertyValue(my_property), empty_str)

    def test_this(self):
        # The `this` attribute should return the object itself. This
        # is for backward compatibility with pySBOL. It is a
        # deprecated attribute.
        md = sbol2.ModuleDefinition('md')
        # Enable all warnings
        warnings.simplefilter("default")
        with warnings.catch_warnings(record=True) as warns:
            self.assertEqual(md.this, md)
        # Verify that a warning was issued
        self.assertEqual(len(warns), 1)

    def test_compare_properties(self):
        # Test that two objects are equal even if a property is in a
        # different order
        expected1 = [sbol2.SBO_INHIBITION, sbol2.SBO_CONTROL]
        expected2 = [sbol2.SBO_CONTROL, sbol2.SBO_INHIBITION]
        md1 = sbol2.ModuleDefinition('md1')
        md1.roles = expected1
        md2 = sbol2.ModuleDefinition('md1')
        md2.roles = expected2
        self.assertTrue(md1.compare(md2))

    def test_compare_owned_objects(self):
        # Test that two objects are equal even if owned objects are in
        # a different order
        expected1 = [sbol2.Module('m1'), sbol2.Module('m2')]
        expected2 = [sbol2.Module('m2'), sbol2.Module('m1')]
        md1 = sbol2.ModuleDefinition('md1')
        md1.modules = expected1
        md2 = sbol2.ModuleDefinition('md1')
        md2.modules = expected2
        self.assertTrue(md1.compare(md2))

    def test_compare_recursive(self):
        # Test that the compare method is doing a recursive compare
        m1a = sbol2.Module('m1')
        m1b = sbol2.Module('m1')
        # m1a and m1b compare True
        self.assertTrue(m1a.compare(m1b))
        m2 = sbol2.Module('m2')
        # m2 is different from m1a and m1b
        self.assertFalse(m2.compare(m1a))
        self.assertFalse(m2.compare(m1b))

        md1a = sbol2.ModuleDefinition('md1')
        md1b = sbol2.ModuleDefinition('md1')
        # md1a and md1b compare True
        self.assertTrue(md1a.compare(md1b))
        md1a.modules = [m1a]
        md1b.modules = [m1b]
        # md1a and md1b still compare True
        self.assertTrue(md1a.compare(md1b))
        md1a.modules = [m2]
        # Now md1a and md1b compare False because of recursive
        # comparison of modules
        self.assertFalse(md1a.compare(md1b))

    def build_md_tree_3(self, suffix='1'):
        # Build a md->m->measurement tree for comparison
        meter_uri = 'http://www.ontology-of-units-of-measure.org/resource/om-2/metre'
        mdef = sbol2.ModuleDefinition('md' + suffix)
        module = sbol2.Module('m' + suffix)
        measurement = sbol2.Measurement('meas' + suffix, 5.0, meter_uri)
        module.measurements = [measurement]
        mdef.modules = [module]
        return mdef

    def test_compare_recursive_3(self):
        # Compare recursively at 3 levels instead of just 2
        tree1a = self.build_md_tree_3()
        tree1b = self.build_md_tree_3()
        tree2 = self.build_md_tree_3('2')
        self.assertTrue(tree1a.compare(tree1b))
        self.assertTrue(tree1b.compare(tree1a))
        self.assertFalse(tree1a.compare(tree2))
        self.assertFalse(tree2.compare(tree1a))
        self.assertFalse(tree1b.compare(tree2))
        self.assertFalse(tree2.compare(tree1b))

    def test_is_hashable(self):
        obj = sbol2.SBOLObject()
        self.assertTrue(isinstance(obj, collections.abc.Hashable))
        # Make sure the hash function returns a reasonable value. The
        # hashable test above can be fooled according to the
        # documentation.
        self.assertTrue(isinstance(hash(obj), int))

    def test_get_property(self):
        # If a property is unset, return an empty string instead of
        # an IndexError
        fc = sbol2.FunctionalComponent()
        self.assertEqual('', fc.getPropertyValue(sbol2.SBOL_NAME))

        # getPropertyValue always returns a string, even if the
        # property is an IntProperty
        c = sbol.Cut()
        self.assertEqual('0', c.getPropertyValue(sbol.SBOL_AT))


if __name__ == '__main__':
    unittest.main()
