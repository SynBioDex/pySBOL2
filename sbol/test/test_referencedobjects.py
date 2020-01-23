import locale
import logging
import os
import unittest

import sbol

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
TEST_LOCATION = os.path.join(MODULE_LOCATION, 'resources', 'crispr_example.xml')


class TestReferencedObjects(unittest.TestCase):

    def test_participant_type(self):
        doc = sbol.Document()
        doc.read(TEST_LOCATION)
        md_uri = 'http://sbols.org/CRISPR_Example/CRISPR_Template/1.0.0'
        md = doc.moduleDefinitions[md_uri]
        # Work with the first interaction
        i = md.interactions[0]
        # participant should be a string for backward compatibility
        self.assertEqual(type(i.participations[0].participant), str)

    def test_fc_definition(self):
        doc = sbol.Document()
        doc.read(TEST_LOCATION)
        md_uri = 'http://sbols.org/CRISPR_Example/CRISPR_Template/1.0.0'
        md = doc.moduleDefinitions[md_uri]
        fc_uri = ('http://sbols.org/CRISPR_Example/CRISPR_Template' +
                  '/cas9_gRNA_complex/1.0.0')
        fc = md.functionalComponents[fc_uri]
        # definition should be a string for backward compatibility
        self.assertEqual(type(fc.definition), str)
