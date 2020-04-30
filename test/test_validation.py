import unittest

import rdflib

import sbol2
from sbol2.validation import sbol_rule_10202
from sbol2.componentdefinition import libsbol_rule_20


class TestValidation(unittest.TestCase):

    def test_is_alphanumeric_or_underscore(self):
        # is alpha
        self.assertTrue(sbol2.is_alphanumeric_or_underscore('A'))
        self.assertTrue(sbol2.is_alphanumeric_or_underscore('a'))
        self.assertTrue(sbol2.is_alphanumeric_or_underscore('M'))
        self.assertTrue(sbol2.is_alphanumeric_or_underscore('m'))
        self.assertTrue(sbol2.is_alphanumeric_or_underscore('Z'))
        self.assertTrue(sbol2.is_alphanumeric_or_underscore('z'))
        # is numeric
        self.assertTrue(sbol2.is_alphanumeric_or_underscore('0'))
        self.assertTrue(sbol2.is_alphanumeric_or_underscore('3'))
        self.assertTrue(sbol2.is_alphanumeric_or_underscore('9'))
        # is underscore
        self.assertTrue(sbol2.is_alphanumeric_or_underscore('_'))
        # not alpha or numeric or underscore
        self.assertFalse(sbol2.is_alphanumeric_or_underscore('$'))
        self.assertFalse(sbol2.is_alphanumeric_or_underscore('\n'))
        self.assertFalse(sbol2.is_alphanumeric_or_underscore('-'))
        # More to ensure the function is exported than anything else
        self.assertTrue(sbol2.is_not_alphanumeric_or_underscore('-'))
        self.assertFalse(sbol2.is_not_alphanumeric_or_underscore('A'))

    def test_sbol_rule_10202(self):
        with self.assertRaises(TypeError):
            sbol_rule_10202(None, None)

    def test_libsbol_rule_20_empty(self):
        # This rule synchronized ComponentDefinition.sequence with
        # ComponentDefinition.sequences
        cd = sbol2.ComponentDefinition('cd1')
        seq = sbol2.Sequence('seq1', 'GCAT')
        with self.assertRaises(sbol2.SBOLError):
            libsbol_rule_20('foo', seq)
        with self.assertRaises(sbol2.SBOLError):
            libsbol_rule_20(cd, 'foo')
        cd.sequence = seq
        self.assertEqual([seq.identity], cd.sequences)

    def test_libsbol_rule_20_empty_set_with(self):
        # This rule synchronized ComponentDefinition.sequence with
        # ComponentDefinition.sequences
        cd = sbol2.ComponentDefinition('cd1')
        seq = sbol2.Sequence('seq1', 'GCAT')
        expected = [rdflib.URIRef('http://example.com/foo/1'),
                    seq.identity,
                    rdflib.URIRef('https://sbolstandard.org/bar/1')]
        # Go behind the scenes for the purposes of testing
        cd.properties[sbol2.SBOL_SEQUENCE_PROPERTY] = expected
        libsbol_rule_20(cd, seq)
        # Expect sequences to remain the same, but they've all been
        # converted to URIRefs
        self.assertEqual(expected, cd.sequences)

    def test_libsbol_rule_20_empty_set_without(self):
        # This rule synchronized ComponentDefinition.sequence with
        # ComponentDefinition.sequences
        cd = sbol2.ComponentDefinition('cd1')
        seq = sbol2.Sequence('seq1', 'GCAT')
        expected = ['http://example.com/foo/1',
                    'https://sbolstandard.org/bar/1']
        cd.sequences = expected
        cd.sequence = seq
        # Expect sequences to be overwritten to be only
        # the assigned sequence
        self.assertEqual([seq.identity], cd.sequences)


if __name__ == '__main__':
    unittest.main()
