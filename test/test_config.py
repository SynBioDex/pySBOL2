import unittest
import warnings

import sbol2

CRISPR_URI = 'http://sbols.org/CRISPR_Example/CRISPR_Template'
CRISPR_URI_1 = 'http://sbols.org/CRISPR_Example/CRISPR_Template/1'
CRISPR_MD_URI_1 = 'http://sbols.org/CRISPR_Example/ModuleDefinition/CRISPR_Template/1'
CRISPR_CD_URI_1 = 'http://sbols.org/CRISPR_Example/ComponentDefinition/CRISPR_Template/1'


class TestConfig(unittest.TestCase):

    def test_setOption_invalidOption(self):
        with self.assertRaises(sbol2.SBOLError):
            sbol2.Config.setOption('invalid_option', 2)

    def test_setOption_invalidOptionVal(self):
        with self.assertRaises(sbol2.SBOLError):
            sbol2.Config.setOption(sbol2.ConfigOptions.VERBOSE.value, 'Yellow')

    def test_hasHomespace_True(self):
        sbol2.setHomespace('http://sbols.org/CRISPR_Example/')
        self.assertTrue(sbol2.hasHomespace())

    def test_hasHomespace_False(self):
        sbol2.setHomespace('')
        self.assertFalse(sbol2.hasHomespace())

    def test_openworld_noHomespace(self):
        """See: https://pysbol2.readthedocs.io/en/latest/getting_started.html"""
        sbol2.setHomespace('')
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, False)
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol2.ModuleDefinition(CRISPR_URI)
        self.assertEqual(CRISPR_URI, str(crispr_template))
        self.assertEqual(CRISPR_URI, crispr_template.identity)

    def test_openworld_useHomespace(self):
        """See: https://pysbol2.readthedocs.io/en/latest/getting_started.html"""
        # Note: In tutorial CRISPR_Example is followed by a trailing slash.
        # This results in two slashes instead of one in both the original pySBOL
        # and the new code.
        sbol2.setHomespace('http://sbols.org/CRISPR_Example')
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, False)
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol2.ModuleDefinition('CRISPR_Template')
        self.assertEqual(CRISPR_URI, str(crispr_template))
        self.assertEqual(CRISPR_URI, crispr_template.identity)

    def test_SBOLCompliant(self):
        """See: https://pysbol2.readthedocs.io/en/latest/getting_started.html"""
        sbol2.setHomespace('http://sbols.org/CRISPR_Example')
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol2.ModuleDefinition('CRISPR_Template')
        self.assertEqual(CRISPR_URI_1, str(crispr_template))
        self.assertEqual(CRISPR_URI_1, crispr_template.identity)

    def test_SBOLCompliant_typed(self):
        """See: https://pysbol2.readthedocs.io/en/latest/getting_started.html"""
        sbol2.setHomespace('http://sbols.org/CRISPR_Example')
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)
        crispr_template_md = sbol2.ModuleDefinition('CRISPR_Template')
        expected_crispr_template_md = CRISPR_MD_URI_1
        self.assertEqual(expected_crispr_template_md, str(crispr_template_md))
        self.assertEqual(expected_crispr_template_md,
                         crispr_template_md.identity)
        crispr_template_cd = sbol2.ComponentDefinition('CRISPR_Template')
        expected_crispr_template_cd = CRISPR_CD_URI_1
        self.assertEqual(expected_crispr_template_cd, str(crispr_template_cd))
        self.assertEqual(expected_crispr_template_cd,
                         crispr_template_cd.identity)

    def test_ca_path(self):
        with warnings.catch_warnings(record=True) as warns:
            sbol2.Config.getOption('ca-path')
            sbol2.Config.setOption('ca-path', '/fake/path')
        self.assertEqual(len(warns), 2)


if __name__ == '__main__':
    unittest.main()
