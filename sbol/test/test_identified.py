import os
import unittest

import rdflib

import sbol

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
PARTS_LOCATION = os.path.join(MODULE_LOCATION, 'resources', 'tutorial',
                              'parts.xml')
CRISPR_LOCATION = os.path.join(MODULE_LOCATION, 'resources',
                               'crispr_example.xml')


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

    def test_was_derived_from(self):
        d = sbol.Document()
        d.read(PARTS_LOCATION)
        cd = d.componentDefinitions['http://examples.org/ComponentDefinition/AmeR/1']
        uri = 'https://synbiohub.programmingbiology.org/public/Cello_Parts/AmeR/1'
        expected = [rdflib.term.URIRef(uri)]
        self.assertEqual(cd.wasDerivedFrom, expected)

    def test_was_derived_from2(self):
        d = sbol.Document()
        d.read(CRISPR_LOCATION)
        cd = d.componentDefinitions['http://sbols.org/CRISPR_Example/CRP_b/1.0.0']
        expected = []
        self.assertEqual(cd.wasDerivedFrom, expected)

    def test_was_generated_by(self):
        d = sbol.Document()
        d.read(PARTS_LOCATION)
        cd = d.componentDefinitions['http://examples.org/ComponentDefinition/AmeR/1']
        uri = 'http://examples.org/Activity/CelloUCF2sbol_Activity/1'
        expected = [rdflib.term.URIRef(uri)]
        self.assertEqual(cd.wasGeneratedBy, expected)

    def test_was_generated_by2(self):
        d = sbol.Document()
        d.read(CRISPR_LOCATION)
        cd = d.componentDefinitions['http://sbols.org/CRISPR_Example/CRP_b/1.0.0']
        expected = []
        self.assertEqual(cd.wasGeneratedBy, expected)


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
        Config.setOption('sbol_compliant_uris', True)
        Config.setOption('sbol_typed_uris', False)
        doc = Document()
        comp = ComponentDefinition('cd')
        seq = Sequence('seq')
        doc.addComponentDefinition(comp)
        doc.addSequence(seq)
        comp.sequences = seq.identity

        # Import the object into a new namespace
        old_homespace = getHomespace()
        setHomespace('http://acme.com')
        comp_copy = comp.copy(None, old_homespace)  # Import from old homespace into new homespace
        self.assertEqual(comp_copy.identity, 'http://acme.com/cd/1')
        self.assertEqual(comp_copy.sequences[0], 'http://acme.com/seq/1')

    def test_import_into_nontyped_namespace_from_typed_namespace(self):
        # Now repeat. This time copy an sbol-typed URI to a non-typed, sbol-compliant URI
        setHomespace('http://examples.org')
        Config.setOption('sbol_typed_uris', True)

        doc = Document()
        comp = ComponentDefinition('cd')
        seq = Sequence('seq')
        comp.sequences = seq.identity
        doc.addComponentDefinition(comp)
        doc.addSequence(seq)

        # Import the object into the new namespace, while removing the type token from the URI
        Config.setOption('sbol_typed_uris', False)
        old_homespace = getHomespace()
        setHomespace('http://acme.com')
        comp_copy = comp.copy(None, old_homespace)  # Import from old homespace into new homespace
        self.assertEqual(comp_copy.identity, 'http://acme.com/cd/1')
        self.assertEqual(comp_copy.sequences[0], 'http://acme.com/seq/1')      

    def test_import_into_typed_namespace_from_nontyped_namespace(self):

        # Now repeat. This time copy an sbol-typed URI to a non-typed, sbol-compliant URI
        setHomespace('http://examples.org')
        Config.setOption('sbol_typed_uris', False)

        doc = Document()
        comp = ComponentDefinition('cd')
        seq = Sequence('seq')
        comp.sequences = seq.identity
        doc.addComponentDefinition(comp)
        doc.addSequence(seq)

        # Import the object into the new namespace, while removing the type token from the URI
        Config.setOption('sbol_typed_uris', True)
        old_homespace = getHomespace()
        setHomespace('http://acme.com')
        comp_copy = comp.copy(None, old_homespace)  # Import from old homespace into new homespace
        self.assertEqual(comp_copy.identity, 'http://acme.com/ComponentDefinition/cd/1')
        self.assertEqual(comp_copy.sequences[0], 'http://acme.com/Sequence/seq/1')

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

    def test_copy_and_increment_version(self):
        Config.setOption('sbol_typed_uris', False)
        doc = Document()
        comp = ComponentDefinition('foo', BIOPAX_DNA, '1.0.0')
        doc.addComponentDefinition(comp)

        # Copy an object within a single Document, the version should be automatically incrememented
        comp_copy = comp.copy()
        self.assertEquals(comp.version, '1.0.0')
        self.assertEquals(comp_copy.version, '2.0.0')
        self.assertEquals(comp_copy.identity, comp.persistentIdentity + '/2.0.0')
        self.assertEquals(comp_copy.wasDerivedFrom[0], comp.identity)
        self.assertEquals(comp_copy.types[0], BIOPAX_DNA)

    def test_copy_to_new_document(self):
        Config.setOption('sbol_typed_uris', False)
        doc = Document()
        comp1 = doc.componentDefinitions.create('cd1')
        comp2 = doc.componentDefinitions.create('cd2')
        comp2.wasDerivedFrom = comp1.identity

        # Clone the object to another Document, the wasDerivedFrom should not be a circular reference
        doc2 = Document()
        comp3 = comp2.copy(doc2)
        self.assertEquals(comp3.identity, comp2.identity)
        self.assertEquals(comp3.wasDerivedFrom[0], comp1.identity)
        self.assertNotEqual(comp3.wasDerivedFrom[0], comp2.identity)

if __name__ == '__main__':
    unittest.main()
