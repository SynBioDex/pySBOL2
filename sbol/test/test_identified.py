import os
import unittest
import sbol
from sbol import *

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
PARTS_LOCATION = os.path.join(MODULE_LOCATION, 'resources', 'tutorial',
                              'parts.xml')


class TestIdentified(unittest.TestCase):

    def test_getDisplayId_SBOLCompliant(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', True)
        Config.setOption('sbol_typed_uris', False)
        crispr_template = ModuleDefinition('CRISPR_Template')
        self.assertEqual('CRISPR_Template', crispr_template.displayId)

    def test_getPersistentIdentity_SBOLCompliant(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', True)
        Config.setOption('sbol_typed_uris', False)
        crispr_template = ModuleDefinition('CRISPR_Template')
        self.assertEqual('http://sbols.org/CRISPR_Example/CRISPR_Template',
                         crispr_template.persistentIdentity)

    def test_getVersion_SBOLCompliant(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', True)
        Config.setOption('sbol_typed_uris', False)
        crispr_template = ModuleDefinition('CRISPR_Template')
        self.assertEqual('1', crispr_template.version)

    def test_setDisplayId_SBOLCompliant(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', True)
        Config.setOption('sbol_typed_uris', False)
        crispr_template = ModuleDefinition('CRISPR_Template')
        crispr_template.displayId = 'test'
        self.assertEqual('test', crispr_template.displayId)

    def test_setPersistentIdentity_SBOLCompliant(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', True)
        Config.setOption('sbol_typed_uris', False)
        crispr_template = ModuleDefinition('CRISPR_Template')
        crispr_template.persistentIdentity = 'test'
        self.assertEqual('test', crispr_template.persistentIdentity)

    def test_setVersion_SBOLCompliant(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', True)
        Config.setOption('sbol_typed_uris', False)
        crispr_template = ModuleDefinition('CRISPR_Template')
        crispr_template.version = '2'
        self.assertEqual('2', crispr_template.version)

    def test_getDisplayId_hasHomespace(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', False)
        Config.setOption('sbol_typed_uris', False)
        crispr_template = ModuleDefinition('CRISPR_Template')
        self.assertEqual(None, crispr_template.displayId)

    def test_getPersistentIdentity_hasHomespace(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', False)
        Config.setOption('sbol_typed_uris', False)
        crispr_template = ModuleDefinition('CRISPR_Template')
        self.assertEqual('http://sbols.org/CRISPR_Example/CRISPR_Template',
                         crispr_template.persistentIdentity)

    def test_getVersion_hasHomespace(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', False)
        Config.setOption('sbol_typed_uris', False)
        crispr_template = ModuleDefinition('CRISPR_Template')
        self.assertEqual('1', crispr_template.version)

    def test_setPersistentIdentity_hasHomespace(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', False)
        Config.setOption('sbol_typed_uris', False)
        crispr_template = ModuleDefinition('CRISPR_Template')
        crispr_template.persistentIdentity = 'test'
        self.assertEqual('test', crispr_template.persistentIdentity)

    def test_setVersion_hasHomespace(self):
        setHomespace('http://sbols.org/CRISPR_Example')
        Config.setOption('sbol_compliant_uris', False)
        Config.setOption('sbol_typed_uris', False)
        crispr_template = ModuleDefinition('CRISPR_Template')
        crispr_template.version = '2'
        self.assertEqual('2', crispr_template.version)

    def test_name(self):
        d = sbol.Document()
        d.read(PARTS_LOCATION)
        cd = d.componentDefinitions['http://examples.org/ComponentDefinition/AmeR/1']
        expected_name = 'AmeR'
        self.assertEqual(cd.name, expected_name)


class TestCopy(unittest.TestCase):

    def test_copy_properties(self):
        i = sbol.Identified('i')
        i.name = 'foo'
        i_copy = i.copy()
        self.assertEqual(i_copy.name, 'foo')

    def test_import_object_into_new_namespace(self):
        # When copying an object into a new namespace, confirm that it's URI is copied into the new namespace.
        # Also confirm that any ReferencedObject attributes whose values point to an object in the old namespace
        # are also copied into the new namespace

        setHomespace('http://examples.org')
        Config.setOption('sbol_typed_uris', False)
        comp = ComponentDefinition('cd')
        seq = Sequence('seq')
        comp.sequences = seq.identity

        # Import the object into a new namespace
        old_homespace = getHomespace()
        setHomespace('http://acme.com')
        comp_copy = comp.copy(None, old_homespace)  # Import from old homespace into new homespace
        self.assertEqual(comp_copy.identity, 'http://acme.com/cd/1')
        self.assertEqual(comp_copy.sequences[0], 'http://acme.com/seq/1')

    def test_copy_namespace(self):
        # Confirm that extension namespaces are copied into the target Document
        extension_prefix = 'extension_prefix'
        extension_namespace = 'http://examples.org#'
        doc = Document()
        target_doc = Document()
        cd = ComponentDefinition('cd')
        doc.addComponentDefinition(cd)
        doc.addNamespace(extension_namespace, extension_prefix)
        cd.extension_property = LiteralProperty(cd, extension_namespace + 'extension_property', '0', '1', None, 'foo')
        cd_copy = cd.copy(target_doc)
        self.assertTrue(target_doc._namespaces[extension_prefix] == URIRef(extension_namespace))

if __name__ == '__main__':
    unittest.main()
