import unittest

import sbol2 as sbol
from sbol2.validation import sbol_rule_10202


class TestValidation(unittest.TestCase):

    def test_is_alphanumeric_or_underscore(self):
        # is alpha
        self.assertTrue(sbol.is_alphanumeric_or_underscore('A'))
        self.assertTrue(sbol.is_alphanumeric_or_underscore('a'))
        self.assertTrue(sbol.is_alphanumeric_or_underscore('M'))
        self.assertTrue(sbol.is_alphanumeric_or_underscore('m'))
        self.assertTrue(sbol.is_alphanumeric_or_underscore('Z'))
        self.assertTrue(sbol.is_alphanumeric_or_underscore('z'))
        # is numeric
        self.assertTrue(sbol.is_alphanumeric_or_underscore('0'))
        self.assertTrue(sbol.is_alphanumeric_or_underscore('3'))
        self.assertTrue(sbol.is_alphanumeric_or_underscore('9'))
        # is underscore
        self.assertTrue(sbol.is_alphanumeric_or_underscore('_'))
        # not alpha or numeric or underscore
        self.assertFalse(sbol.is_alphanumeric_or_underscore('$'))
        self.assertFalse(sbol.is_alphanumeric_or_underscore('\n'))
        self.assertFalse(sbol.is_alphanumeric_or_underscore('-'))
        # More to ensure the function is exported than anything else
        self.assertTrue(sbol.is_not_alphanumeric_or_underscore('-'))
        self.assertFalse(sbol.is_not_alphanumeric_or_underscore('A'))

    def test_sbol_rule_10202(self):
        with self.assertRaises(TypeError):
            sbol_rule_10202(None, None)
