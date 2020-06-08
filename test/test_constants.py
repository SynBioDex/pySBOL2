import os
import unittest

import sbol2 as sbol

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
TEST_LOCATION = os.path.join(MODULE_LOCATION, 'resources', 'crispr_example.xml')


class TestConstants(unittest.TestCase):

    def test_igem_standard_assembly(self):
        # IGEM_STANDARD_ASSEMBLY is a function in pySBOL.
        self.assertTrue(callable(sbol.IGEM_STANDARD_ASSEMBLY),
                        'IGEM_STANDARD_ASSEMBLY is not callable')

    def test_in_roles(self):
        doc = sbol.Document()
        doc.read(TEST_LOCATION)
        md_uri = 'http://sbols.org/CRISPR_Example/CRISPR_Template/1.0.0'
        md = doc.moduleDefinitions[md_uri]
        i_uri = ('http://sbols.org/CRISPR_Example/CRISPR_Template' +
                 '/cas9_complex_formation/1.0.0')
        i = md.interactions[i_uri]
        p_uri = ('http://sbols.org/CRISPR_Example/CRISPR_Template' +
                 '/cas9_complex_formation/cas9_gRNA_complex/1.0.0')
        p = i.participations[p_uri]
        # p.roles is a list of URIs
        # The constant should be in the list of roles
        self.assertIn(sbol.SBO_PRODUCT, p.roles)
