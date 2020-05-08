import unittest
import os

import sbol2
# backward compatibility
import sbol2 as sbol

import rdflib

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
TEST_LOCATION = os.path.join(MODULE_LOCATION, 'resources',
                             'crispr_example.xml')


class TestProperty(unittest.TestCase):
    def test_listProperty(self):
        plasmid = sbol.ComponentDefinition('pBB1', sbol.BIOPAX_DNA, '1.0.0')
        plasmid.roles = [sbol.SO_PLASMID, sbol.SO_CIRCULAR]
        self.assertEqual(len(plasmid.roles), 2)

    def test_noListProperty(self):
        plasmid = sbol.ComponentDefinition('pBB1', sbol.BIOPAX_DNA, '1.0.0')
        with self.assertRaises(TypeError):
            plasmid.version = ['1', '2']

    def test_addPropertyToList(self):
        plasmid = sbol.ComponentDefinition('pBB1', sbol.BIOPAX_DNA, '1.0.0')
        plasmid.roles = [sbol.SO_PLASMID]
        plasmid.addRole(sbol.SO_CIRCULAR)
        self.assertEqual(len(plasmid.roles), 2)

    def test_removePropertyFromList(self):
        plasmid = sbol.ComponentDefinition('pBB1', sbol.BIOPAX_DNA, '1.0.0')
        plasmid.roles = [sbol.SO_PLASMID, sbol.SO_CIRCULAR]
        plasmid.removeRole()
        self.assertEqual(len(plasmid.roles), 1)

    @unittest.expectedFailure  # See #93
    def test_unsetSingletonProperty(self):
        doc = sbol.Document()
        cd = doc.componentDefinitions.create('cd')
        cd.name = 'foo'
        self.assertEqual(cd.name, 'foo')
        cd.name = None
        self.assertEqual(cd.name, None)
        cd.name = 'foo'
        self.assertEqual(cd.name, 'foo')
        cd.name = ''
        self.assertEqual(cd.name, None)

    def test_unsetListProperty(self):
        plasmid = sbol.ComponentDefinition('pBB1', sbol.BIOPAX_DNA, '1.0.0')
        plasmid.roles = [sbol.SO_PLASMID, sbol.SO_CIRCULAR]
        plasmid.roles = []
        self.assertEqual(len(plasmid.roles), 0)

    def test_lenOwnedObject(self):
        d = sbol.Document()
        d.read(TEST_LOCATION)
        self.assertEqual(25, len(d.componentDefinitions))
        self.assertEqual(2, len(d.moduleDefinitions))
        self.assertEqual(4, len(d.sequences))

    def test_getitem(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example/')
        d = sbol.Document()
        d.read(TEST_LOCATION)
        s1 = d.sequences['CRa_U6_seq']
        expected = 'http://sbols.org/CRISPR_Example/CRa_U6_seq/1.0.0'
        self.assertEqual(expected, str(s1))

    def test_readProperties(self):
        d = sbol.Document()
        d.read(TEST_LOCATION)
        cd2 = d.componentDefinitions['http://sbols.org/CRISPR_Example/EYFP_gene/1.0.0']
        self.assertEqual(2, len(cd2.components))
        self.assertEqual(1, len(cd2.roles))
        md = d.moduleDefinitions['http://sbols.org/CRISPR_Example/CRISPR_Template/1.0.0']
        self.assertEqual(5, len(md.functionalComponents))
        self.assertEqual(3, len(md.interactions))
        self.assertEqual(0, len(md.roles))

    def test_text_property_constructor(self):
        # Test None as parent object
        with self.assertRaises(AttributeError):
            sbol.TextProperty(None, sbol.SBOL_NAME, '0', '*', [], 'foo')
        # Test string as parent object
        with self.assertRaises(AttributeError):
            sbol.TextProperty('foo', sbol.SBOL_NAME, '0', '*', [], 'foo')
        # Test with object whose properties attribute is not a dict
        with self.assertRaises(TypeError):
            md = sbol.ModuleDefinition()
            md.properties = []
            sbol.TextProperty(md, sbol.SBOL_NAME, '0', '*', [], 'foo')

    def test_literal_property_properties(self):
        md = sbol.ModuleDefinition()
        self.assertNotIn(sbol.UNDEFINED, md.properties)
        sbol.property.LiteralProperty(md, sbol.UNDEFINED, '0', '*', [], 'foo')
        # Creating the property should also create the entry in the
        # parent properties dict
        self.assertIn(sbol.UNDEFINED, md.properties)

    def test_text_property_setting_single(self):
        md = sbol.ModuleDefinition()
        testing_uri = rdflib.URIRef(sbol.SBOL_URI + "#Testing")
        tp = sbol.TextProperty(md, testing_uri, '0', '1', [])
        # Test setting to string
        expected = 'foo'
        tp.value = expected
        self.assertEqual(tp.value, rdflib.Literal(expected))
        # Test setting to None
        tp.value = None
        self.assertIsNone(tp.value)
        # Test integer
        with self.assertRaises(TypeError):
            tp.value = 3
        # Test setting to list
        with self.assertRaises(TypeError):
            tp.value = ['foo', 'bar']

    def test_text_property_setting_list(self):
        md = sbol.ModuleDefinition()
        testing_uri = rdflib.URIRef(sbol.SBOL_URI + "#Testing")
        tp = sbol.TextProperty(md, testing_uri, '0', '*', [])
        # Test setting to string
        expected = 'foo'
        tp.value = expected
        self.assertEqual(tp.value, [rdflib.Literal(expected)])
        # Test setting to None
        with self.assertRaises(TypeError):
            tp.value = None
        # Test setting to list
        expected = ['foo', 'bar']
        tp.value = expected
        self.assertEqual(tp.value, [rdflib.Literal(x) for x in expected])
        # Test setting to list of integers
        with self.assertRaises(TypeError):
            tp.value = [1, 2, 3]
        # Test setting to empty list
        expected = []
        tp.value = expected
        self.assertEqual(tp.value, [])

    def test_owned_object_singleton(self):
        cd = sbol.ComponentDefinition('cd')
        annotation_uri = rdflib.URIRef('http://examples.org#annotation_property')
        cd.annotation = sbol.property.OwnedObject(cd, annotation_uri, sbol.Identified,
                                                  '0', '1', None)
        self.assertIsNone(cd.annotation)
        cd.annotation = sbol.Identified('foo')
        self.assertEqual(type(cd.annotation), sbol.Identified)

    def test_owned_object_multiple(self):
        cd = sbol.ComponentDefinition('cd')
        annotation_uri = rdflib.URIRef('http://examples.org#annotation_property')
        cd.annotations = sbol.property.OwnedObject(cd, annotation_uri, sbol.Identified,
                                                   '0', '*', None)
        self.assertEqual(type(cd.annotations), sbol.property.OwnedObject)
        cd.annotations.add(sbol.Identified('foo_0'))
        cd.annotations.add(sbol.Identified('foo_1'))
        self.assertEqual(type(cd.annotations), sbol.property.OwnedObject)

    def test_owned_object_find(self):
        doc = sbol.Document()
        md = doc.moduleDefinitions.create('foo')
        # find() underlies __contains__ so test `in`
        self.assertIn('foo', doc.moduleDefinitions)
        self.assertNotIn('bar', doc.moduleDefinitions)
        # find something that is in the collection
        md2 = doc.moduleDefinitions.find('foo')
        self.assertEqual(md, md2)
        # find something that is not in the collection
        with self.assertRaises(sbol.SBOLError):
            doc.moduleDefinitions.find('bar')
        # confirm we get the expected error code
        try:
            doc.moduleDefinitions.find('bar')
        except sbol.SBOLError as err:
            self.assertEqual(err.error_code(),
                             sbol.SBOLErrorCode.NOT_FOUND_ERROR)
        else:
            self.fail('Expected SBOLError')

    def test_referenced_object(self):
        # Test referenced object property is initialized to correct types
        cd0 = sbol.ComponentDefinition('cd0')
        self.assertEqual(type(cd0.sequences), list)

        c = cd0.components.create('c')
        self.assertEqual(c.definition, None)

        # Test assignment
        cd1 = sbol.ComponentDefinition('cd1')
        c.definition = cd1.identity
        self.assertEqual(c.definition, cd1.identity)

        seq0a = sbol.Sequence('seq0a')
        seq0b = sbol.Sequence('seq0b')
        cd0.sequences = [seq0a.identity, seq0b.identity]
        self.assertEqual(cd0.sequences, [seq0a.identity, seq0b.identity])

        c.definition = cd1
        self.assertEqual(c.definition, cd1.identity)

        # Test conversion to URIRef
        c.definition = str(cd1.identity)
        self.assertEqual(type(c.definition), rdflib.URIRef)

        cd0.sequences = [str(seq0a.identity), str(seq0b.identity)]
        self.assertEqual([type(s) for s in cd0.sequences],
                         [rdflib.URIRef, rdflib.URIRef])

        # Test unset
        c.definition = None
        self.assertEqual(c.definition, None)

        c.definition = cd1.identity
        c.definition = ''
        self.assertEqual(c.definition, None)

        cd0.sequences = []
        self.assertEqual(cd0.sequences, [])

        cd0.sequences = [seq0a.identity, seq0b.identity]
        cd0.sequences = None
        self.assertEqual(cd0.sequences, [])

        with self.assertRaises(TypeError):
            cd0.sequences = [seq0a.identity, seq0b.identity]
            cd0.sequences = [None, None]
            self.assertEqual(cd0.sequences, [])

    def test_int_property(self):
        r = sbol.location.Range('r')
        r.start = 42
        self.assertEqual(type(r.start), int)
        self.assertEqual(r.start, 42)
        with self.assertRaises(TypeError):
            r.start = 'forty-two'

    def test_uri_property_list(self):
        cd = sbol.ComponentDefinition('cd')
        foo_str = 'foo'
        bar_str = 'bar'
        foo_uri = rdflib.URIRef(foo_str)
        bar_uri = rdflib.URIRef(bar_str)
        cd.roles = foo_str
        self.assertEqual(cd.roles, [foo_uri])
        # This used to append. Eek!
        cd.roles = bar_str
        self.assertEqual(cd.roles, [bar_uri])
        # This used to append. Eek!
        cd.roles = [foo_str, bar_str]
        self.assertEqual(cd.roles, [foo_uri, bar_uri])
        with self.assertRaises(TypeError):
            cd.roles = 34

    def test_uri_property_append(self):
        cd = sbol.ComponentDefinition('cd')
        foo_str = 'foo'
        bar_str = 'bar'
        foo_uri = rdflib.URIRef(foo_str)
        bar_uri = rdflib.URIRef(bar_str)
        cd.roles = foo_str
        self.assertEqual(cd.roles, [foo_uri])
        # append has no effect. This is because the list that is
        # returned by `cd.roles` is not connected with the internal
        # data representation.
        cd.roles.append(bar_str)
        self.assertEqual(cd.roles, [foo_uri])
        # The `+=` operator is a good way for users to append new
        # items to the list
        cd.roles += [bar_str]
        self.assertEqual(cd.roles, [foo_uri, bar_uri])

    def test_owned_object_remove(self):
        md = sbol.ModuleDefinition('md')
        m1 = md.modules.create('m1')
        m2 = md.modules.create('m2')
        self.assertEqual(list(md.modules), [m1, m2])
        md.modules.remove(m2.identity)
        self.assertEqual(list(md.modules), [m1])

    def test_validation_rules(self):
        md = sbol2.ModuleDefinition()
        with self.assertRaises(TypeError):
            # No validation rules, so `'AND'` is interpreted
            # as validation rules
            tp = sbol2.TextProperty(md, 'http://example.com#logic', '0', '1',
                                    'AND')
        # Use an empty list to specify no validation rules
        tp = sbol2.TextProperty(md, 'http://example.com#logic', '0', '1',
                                [], 'AND')
        # Should add a test for callable validation rules
