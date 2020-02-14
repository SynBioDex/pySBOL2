import os
import unittest

import rdflib

import sbol

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
PARTS_LOCATION = os.path.join(MODULE_LOCATION, 'resources', 'tutorial',
                              'parts.xml')


class TestIdentified(unittest.TestCase):

    def test_getDisplayId_SBOLCompliant(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', True)
        sbol.Config.setOption('sbol_typed_uris', False)
        expected = 'CRISPR_Template'
        crispr_template = sbol.ModuleDefinition(expected)
        self.assertEqual(str(crispr_template.displayId), expected)
        self.assertEqual(crispr_template.displayId, rdflib.Literal(expected))

    def test_getPersistentIdentity_SBOLCompliant(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', True)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        expected = 'http://sbols.org/CRISPR_Example/CRISPR_Template'
        self.assertEqual(crispr_template.persistentIdentity,
                         rdflib.URIRef(expected))

    def test_getVersion_SBOLCompliant(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', True)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        self.assertEqual(str(crispr_template.version), '1')
        self.assertEqual(crispr_template.version, rdflib.Literal('1'))

    def test_setDisplayId_SBOLCompliant(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', True)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        crispr_template.displayId = 'test'
        self.assertEqual(str(crispr_template.displayId), 'test')
        self.assertEqual(crispr_template.displayId, rdflib.Literal('test'))

    def test_setPersistentIdentity_SBOLCompliant(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', True)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        expected = 'test'
        crispr_template.persistentIdentity = expected
        self.assertEqual(crispr_template.persistentIdentity,
                         rdflib.URIRef(expected))

    def test_setVersion_SBOLCompliant(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', True)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        crispr_template.version = '2'
        self.assertEqual(str(crispr_template.version), '2')
        self.assertEqual(crispr_template.version, rdflib.Literal('2'))

    def test_getDisplayId_hasHomespace(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', False)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        self.assertEqual(None, crispr_template.displayId)

    def test_getPersistentIdentity_hasHomespace(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', False)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        expected = 'http://sbols.org/CRISPR_Example/CRISPR_Template'
        self.assertEqual(crispr_template.persistentIdentity,
                         rdflib.URIRef(expected))

    def test_getVersion_hasHomespace(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', False)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        self.assertEqual(str(crispr_template.version), '1')
        self.assertEqual(crispr_template.version, rdflib.Literal('1'))

    def test_setPersistentIdentity_hasHomespace(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', False)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        expected = 'test'
        crispr_template.persistentIdentity = expected
        self.assertEqual(crispr_template.persistentIdentity,
                         rdflib.URIRef(expected))

    def test_setVersion_hasHomespace(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption('sbol_compliant_uris', False)
        sbol.Config.setOption('sbol_typed_uris', False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        crispr_template.version = '2'
        self.assertEqual(str(crispr_template.version), '2')
        self.assertEqual(crispr_template.version, rdflib.Literal('2'))

    def test_name(self):
        d = sbol.Document()
        d.read(PARTS_LOCATION)
        cd = d.componentDefinitions['http://examples.org/ComponentDefinition/AmeR/1']
        expected_name = 'AmeR'
        self.assertEqual(str(cd.name), expected_name)
        self.assertEqual(cd.name, rdflib.Literal(expected_name))


if __name__ == '__main__':
    unittest.main()
