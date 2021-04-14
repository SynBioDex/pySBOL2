import os
import unittest

import rdflib

import sbol2 as sbol
import sbol2

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
PARTS_LOCATION = os.path.join(MODULE_LOCATION, 'resources', 'tutorial',
                              'parts.xml')
CRISPR_LOCATION = os.path.join(MODULE_LOCATION, 'resources',
                               'crispr_example.xml')


class TestIdentified(unittest.TestCase):

    def test_getDisplayId_SBOLCompliant(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        expected = 'CRISPR_Template'
        crispr_template = sbol.ModuleDefinition(expected)
        self.assertEqual(crispr_template.displayId, expected)

    def test_getPersistentIdentity_SBOLCompliant(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        expected = 'http://sbols.org/CRISPR_Example/CRISPR_Template'
        self.assertEqual(crispr_template.persistentIdentity,
                         expected)

    def test_getVersion_SBOLCompliant(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        self.assertEqual(crispr_template.version, '1')

    def test_setDisplayId_SBOLCompliant(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        crispr_template.displayId = 'test'
        self.assertEqual(str(crispr_template.displayId), 'test')
        self.assertEqual(crispr_template.displayId, 'test')

    def test_setPersistentIdentity_SBOLCompliant(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        expected = 'test'
        crispr_template.persistentIdentity = expected
        self.assertEqual(crispr_template.persistentIdentity, expected)

    def test_setVersion_SBOLCompliant(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        crispr_template.version = '2'
        self.assertEqual(crispr_template.version, '2')

    def test_getDisplayId_hasHomespace(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, False)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        self.assertEqual(None, crispr_template.displayId)

    def test_getPersistentIdentity_hasHomespace(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, False)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        expected = 'http://sbols.org/CRISPR_Example/CRISPR_Template'
        self.assertEqual(crispr_template.persistentIdentity, expected)

    def test_getVersion_hasHomespace(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, False)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        self.assertEqual(crispr_template.version, '1')

    def test_setPersistentIdentity_hasHomespace(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, False)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        expected = 'test'
        crispr_template.persistentIdentity = expected
        self.assertEqual(crispr_template.persistentIdentity, expected)

    def test_setVersion_hasHomespace(self):
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, False)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        crispr_template.version = '2'
        self.assertEqual(crispr_template.version, '2')

    def test_name(self):
        d = sbol.Document()
        d.read(PARTS_LOCATION)
        cd = d.componentDefinitions['http://examples.org/ComponentDefinition/AmeR/1']
        expected_name = 'AmeR'
        self.assertEqual(cd.name, expected_name)

    def test_was_derived_from(self):
        d = sbol.Document()
        d.read(PARTS_LOCATION)
        cd = d.componentDefinitions['http://examples.org/ComponentDefinition/AmeR/1']
        uri = 'https://synbiohub.programmingbiology.org/public/Cello_Parts/AmeR/1'
        expected = [uri]
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
        expected = [uri]
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

    def test_copy_child_objects(self):
        doc = sbol.Document()
        cd = doc.componentDefinitions.create('cd')
        c1 = cd.components.create('c1')
        c2 = cd.components.create('c2')
        sc1 = cd.sequenceConstraints.create('sc1')
        sc2 = cd.sequenceConstraints.create('sc2')
        sa1 = cd.sequenceConstraints.create('sa1')
        sa2 = cd.sequenceConstraints.create('sa2')

        doc2 = sbol.Document()
        cd_copy = cd.copy(target_doc=doc2)
        self.assertEqual([c.identity for c in cd.components],
                         [c.identity for c in cd_copy.components])
        self.assertEqual([sc.identity for sc in cd.sequenceConstraints],
                         [sc.identity for sc in cd_copy.sequenceConstraints])
        self.assertEqual([sa.identity for sa in cd.sequenceAnnotations],
                         [sa.identity for sa in cd_copy.sequenceAnnotations])

    def test_import_object_into_new_namespace(self):
        # When copying an object into a new namespace, confirm that it's URI is copied
        # into the new namespace. Also confirm that any ReferencedObject attributes
        # whose values point to an object in the old namespace are also copied into the
        # new namespace
        sbol.setHomespace('http://examples.org')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        doc = sbol.Document()
        comp = sbol.ComponentDefinition('cd')
        seq = sbol.Sequence('seq')
        doc.addComponentDefinition(comp)
        doc.addSequence(seq)
        comp.sequences = seq.identity

        # Import from old homespace into new homespace
        old_homespace = sbol.getHomespace()
        sbol.setHomespace('http://acme.com')
        comp_copy = comp.copy(None, old_homespace)

        # Verify new namespace was correctly substituted
        self.assertEqual(comp_copy.identity, 'http://acme.com/cd/1')
        self.assertEqual(comp_copy.persistentIdentity, 'http://acme.com/cd')
        self.assertEqual(comp_copy.sequences[0], 'http://acme.com/seq/1')

        # Verify wasDerivedFrom relationship
        self.assertEqual(comp_copy.wasDerivedFrom[0], comp.identity)

        # Ensure these are equal under the covers
        self.assertEqual(type(comp.properties[sbol.SBOL_SEQUENCE_PROPERTY][0]),
                         rdflib.URIRef)
        self.assertEqual(type(comp.properties[sbol.SBOL_SEQUENCE_PROPERTY][0]),
                         type(comp_copy.properties[sbol.SBOL_SEQUENCE_PROPERTY][0]))

    def test_replace_namespace(self):
        sbol.setHomespace('http://wallacecorporation.com')
        old_namespace = 'http://tyrellcorporation.com'
        old_uri = rdflib.URIRef(old_namespace + '/foo')
        new_uri = sbol.identified.replace_namespace(old_uri, old_namespace,
                                                    sbol.SBOL_COMPONENT_DEFINITION)
        self.assertEqual(type(new_uri), rdflib.URIRef)
        self.assertEqual(new_uri, rdflib.URIRef(sbol.getHomespace() + '/foo'))

    def test_import_into_nontyped_namespace_from_typed_namespace(self):
        # Copy an sbol-typed URI to a non-typed, sbol-compliant URI
        sbol.setHomespace('http://examples.org')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)

        doc = sbol.Document()
        comp = sbol.ComponentDefinition('cd')
        seq = sbol.Sequence('seq')
        comp.sequences = seq.identity
        doc.addComponentDefinition(comp)
        doc.addSequence(seq)

        # Import the object into the new namespace
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        old_homespace = sbol.getHomespace()
        sbol.setHomespace('http://acme.com')
        comp_copy = comp.copy(None, old_homespace)

        # Verify new namespace was correctly substituted and type token was successfully
        # removed
        self.assertEqual(comp_copy.identity, 'http://acme.com/cd/1')
        self.assertEqual(comp_copy.persistentIdentity, 'http://acme.com/cd')
        self.assertEqual(comp_copy.sequences[0], 'http://acme.com/seq/1')

        # Verify wasDerivedFrom relationship
        self.assertEqual(comp_copy.wasDerivedFrom[0], comp.identity)

    def test_import_into_typed_namespace_from_nontyped_namespace(self):

        # Copy an sbol-typed URI to a non-typed, sbol-compliant URI
        sbol.setHomespace('http://examples.org')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)

        doc = sbol.Document()
        comp = sbol.ComponentDefinition('cd')
        seq = sbol.Sequence('seq')
        comp.sequences = seq.identity
        doc.addComponentDefinition(comp)
        doc.addSequence(seq)

        # Import the object into the new namespace
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)
        old_homespace = sbol.getHomespace()
        sbol.setHomespace('http://acme.com')
        comp_copy = comp.copy(None, old_homespace)

        # Verify new namespace was correctly substituted and type token was successfully
        # added
        self.assertEqual(comp_copy.identity,
                         'http://acme.com/ComponentDefinition/cd/1')
        self.assertEqual(comp_copy.persistentIdentity,
                         'http://acme.com/ComponentDefinition/cd')
        self.assertEqual(comp_copy.sequences[0],
                         'http://acme.com/Sequence/seq/1')

        # Verify wasDerivedFrom relationship
        self.assertEqual(comp_copy.wasDerivedFrom[0], comp.identity)

    def test_copy_namespace(self):
        # Confirm that extension namespaces are copied into the target Document
        extension_prefix = 'extension_prefix'
        extension_namespace = 'http://examples.org#'
        doc = sbol.Document()
        target_doc = sbol.Document()
        cd = sbol.ComponentDefinition('cd')
        doc.addComponentDefinition(cd)
        doc.addNamespace(extension_namespace, extension_prefix)
        cd.extension_property = sbol.property.TextProperty(cd, extension_namespace +
                                                           'extension_property', '0',
                                                           '1', None, 'foo')
        cd_copy = cd.copy(target_doc)
        self.assertTrue(target_doc._namespaces[extension_prefix] ==
                        rdflib.URIRef(extension_namespace))

    def test_copy_and_increment_version(self):
        # When copying an object within the same Document, the version should be
        # automatically incrememented
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        doc = sbol.Document()
        comp = sbol.ComponentDefinition('foo', sbol.constants.BIOPAX_DNA, '1.0.0')
        doc.addComponentDefinition(comp)

        comp_copy = comp.copy()
        self.assertEqual(comp.version, '1.0.0')
        self.assertEqual(comp_copy.version, '2.0.0')
        self.assertEqual(comp_copy.identity, comp.persistentIdentity + '/2.0.0')
        self.assertEqual(comp_copy.wasDerivedFrom[0], comp.identity)
        self.assertEqual(comp_copy.types[0], sbol.constants.BIOPAX_DNA)

    def test_copy_to_new_document(self):
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        doc = sbol.Document()
        comp1 = sbol.ComponentDefinition('cd1', sbol.constants.BIOPAX_DNA, '2')
        comp2 = sbol.ComponentDefinition('cd2', sbol.constants.BIOPAX_DNA, '2')
        comp2.wasDerivedFrom = comp1.identity
        doc.addComponentDefinition([comp1, comp2])

        # Since the object is cloned, the wasDerivedFrom should not be a circular
        # reference (this would violate SBOL-spec validation rules)
        doc2 = sbol.Document()
        comp3 = comp2.copy(doc2)
        self.assertEqual(comp3.identity, comp2.identity)
        self.assertEqual(len(doc2.componentDefinitions), 1)

        # Since self was cloned, check that wasDerivedFrom is not a circular reference
        # (this would violate SBOL-spec validation rules)
        self.assertEqual(comp3.wasDerivedFrom[0], comp1.identity)
        self.assertNotEqual(comp3.wasDerivedFrom[0], comp2.identity)

        # Confirm version is the same as the copied object
        self.assertEqual(comp3.version, '2')

    def test_copy_issue_397(self):
        sbol2.Config.setOption('sbol_typed_uris', False)
        sbol2.Config.setOption('validate', False)
        sbol2.setHomespace('http://synbict.org')
        test_doc = sbol2.Document()
        parent_comp = test_doc.componentDefinitions.create('parent')
        child_sub_comp = parent_comp.components.create('child')
        child_sub_comp.definition = 'http://synbict.org/child/1'
        sbol2.setHomespace('http://sd2e.org')
        parent_copy = parent_comp.copy(test_doc, 'http://synbict.org', '1')
        child_copy = parent_copy.components.get('http://sd2e.org/parent/child/1')
        self.assertIsNotNone(child_copy.definition)
        self.assertEqual('http://synbict.org/child/1', child_copy.definition)


if __name__ == '__main__':
    unittest.main()
