import os
import posixpath
import unittest

import sbol2

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
SBOL_TEST_SUITE = os.path.join(MODULE_LOCATION, 'SBOLTestSuite')


class MyTestCase(unittest.TestCase):

    def test_exported(self):
        self.assertIn('CombinatorialDerivation', dir(sbol2))
        self.assertIn('VariableComponent', dir(sbol2))

    def test_read(self):
        fname = os.path.join(SBOL_TEST_SUITE,
                             'SBOL2_ic/gfp_reporter_template.xml')
        doc = sbol2.Document(fname)
        uri = 'http://michael.zhang/GFP_Reporter_Template_CombinatorialDerivation'
        cd: sbol2.CombinatorialDerivation = doc.find(uri)
        self.assertIsNotNone(cd)
        self.assertEqual(1, len(cd.variableComponents))
        vc_uri = posixpath.join(uri, 'CDS_Component_VariableComponent')
        vc: sbol2.VariableComponent = doc.find(vc_uri)
        self.assertEqual(vc.identity, cd.variableComponents[0].identity)
        self.assertIsInstance(vc, sbol2.VariableComponent)
        self.assertEqual(3, len(vc.variants))

    def test_read2(self):
        fname = os.path.join(SBOL_TEST_SUITE,
                             'SBOL2_ic/eukaryotic_transcriptional_unit.xml')
        doc = sbol2.Document(fname)
        uri = posixpath.join('http://michael.zhang',
                             'Eukaryotic_Transcriptional_Unit_CombinatorialDerivation')
        cd: sbol2.CombinatorialDerivation = doc.find(uri)
        self.assertIsNotNone(cd)
        self.assertEqual(2, len(cd.variableComponents))
        vc_uri = posixpath.join(uri, 'Pro_Component_VariableComponent')
        vc: sbol2.VariableComponent = doc.find(vc_uri)
        self.assertIsNotNone(vc)
        self.assertIsInstance(vc, sbol2.VariableComponent)
        self.assertEqual(1, len(vc.variantDerivations))


if __name__ == '__main__':
    unittest.main()
