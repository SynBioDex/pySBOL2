import io
import locale
import os
import tempfile
import unittest
import unittest.mock

import rdflib

import sbol2
import sbol2 as sbol

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
TEST_LOCATION = os.path.join(MODULE_LOCATION, 'resources', 'crispr_example.xml')
CRISPR_LOCATION = TEST_LOCATION

# For testing reading of annotations
ANNO_LOCATION = os.path.join(MODULE_LOCATION, 'SBOLTestSuite', 'SBOL2',
                             'AnnotationOutput.xml')


class TestDocument(unittest.TestCase):

    def setUp(self):
        # One of the unit tests changes the validator URL
        # configuration, so we capture it here and reset it in
        # tearDown(). It would be nice to have a method to reset to
        # factory configuration.
        self.validator_url = sbol2.Config.getOption(sbol2.ConfigOptions.VALIDATOR_URL)

    def tearDown(self):
        sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATOR_URL,
                               self.validator_url)

    def test_empty_len0(self):
        doc = sbol.Document()
        # print(doc)
        self.assertEqual(0, len(doc), "Length of document should be 0")

    def test_addGetTopLevel_uri(self):
        doc = sbol.Document()
        # Tutorial doesn't drop final forward slash, but this isn't right.
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        cas9 = sbol.ComponentDefinition('Cas9', sbol.BIOPAX_PROTEIN)
        doc.addModuleDefinition(crispr_template)
        doc.addComponentDefinition(cas9)

        # Note: tutorial has 1.0.0 instead of 1 but this doesn't work
        crispr_template_uri = 'http://sbols.org/CRISPR_Example/CRISPR_Template/1'
        crispr_template_2 = doc.getModuleDefinition(crispr_template_uri)
        cas9_2 = doc.getComponentDefinition('http://sbols.org/CRISPR_Example/Cas9/1')
        self.assertEqual(crispr_template, crispr_template_2)
        self.assertEqual(cas9, cas9_2)

    def test_addGetTopLevel_displayId(self):
        doc = sbol.Document()
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        cas9 = sbol.ComponentDefinition('Cas9', sbol.BIOPAX_PROTEIN)
        doc.addModuleDefinition(crispr_template)
        doc.addComponentDefinition(cas9)

        crispr_template_2 = doc.moduleDefinitions['CRISPR_Template']
        cas9_2 = doc.componentDefinitions['Cas9']
        self.assertEqual(crispr_template, crispr_template_2)
        self.assertEqual(cas9, cas9_2)

    def test_addGetTopLevel_indexing(self):
        doc = sbol.Document()
        # Tutorial doesn't drop final forward slash, but this isn't right.
        sbol.setHomespace('http://sbols.org/CRISPR_Example')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        crispr_template = sbol.ModuleDefinition('CRISPR_Template')
        cas9 = sbol.ComponentDefinition('Cas9', sbol.BIOPAX_PROTEIN)
        doc.addModuleDefinition(crispr_template)
        doc.addComponentDefinition(cas9)

        crispr_template_2 = doc.moduleDefinitions[0]
        cas9_2 = doc.componentDefinitions[0]
        self.assertEqual(crispr_template, crispr_template_2)
        self.assertEqual(cas9, cas9_2)

    def test_iteration(self):
        doc = sbol.Document()
        doc.read(TEST_LOCATION)
        i = 0
        for obj in doc:
            i += 1
            # print(obj)
        self.assertEqual(len(doc), 31)
        # print(doc)

    def test_identity(self):
        # The sbol:identity relation should not be written out when
        # serializing SBOL.
        doc = sbol.Document()
        doc.read(TEST_LOCATION)
        result = doc.writeString()
        self.assertNotIn('sbol:identity', result)

    def test_utf8_append(self):
        utf8_path = os.path.join(MODULE_LOCATION, 'SBOLTestSuite', 'SBOL2',
                                 'pICSL50014.xml')
        doc = sbol.Document()
        doc.append(utf8_path)

    def test_utf8_append_no_locale(self):
        # Test loading a utf-8 SBOL file without LANG set. This was a
        # bug at one time, and only shows itself when LANG is unset.
        # Here we simulate that by temporarily setting the locale to
        # the generic 'C' locale.
        utf8_path = os.path.join(MODULE_LOCATION, 'SBOLTestSuite', 'SBOL2',
                                 'pICSL50014.xml')
        loc = locale.getlocale()
        try:
            locale.setlocale(locale.LC_ALL, 'C')
            doc = sbol.Document()
            doc.append(utf8_path)
        finally:
            locale.setlocale(locale.LC_ALL, loc)

    def test_utf8_read(self):
        utf8_path = os.path.join(MODULE_LOCATION, 'SBOLTestSuite', 'SBOL2',
                                 'pICSL50014.xml')
        doc = sbol.Document()
        doc.read(utf8_path)

    def test_utf8_read_no_locale(self):
        # Test loading a utf-8 SBOL file without LANG set. This was a
        # bug at one time, and only shows itself when LANG is unset.
        # Here we simulate that by temporarily setting the locale to
        # the generic 'C' locale.
        utf8_path = os.path.join(MODULE_LOCATION, 'SBOLTestSuite', 'SBOL2',
                                 'pICSL50014.xml')
        loc = locale.getlocale()
        try:
            locale.setlocale(locale.LC_ALL, 'C')
            doc = sbol.Document()
            doc.read(utf8_path)
        finally:
            locale.setlocale(locale.LC_ALL, loc)

    def test_constructor(self):
        doc = sbol.Document(TEST_LOCATION)
        self.assertEqual(len(doc), 31)
        self.assertEqual(len(doc.componentDefinitions), 25)

    def test_find(self):
        doc = sbol.Document(TEST_LOCATION)
        found = doc.find('http://sbols.org/CRISPR_Example/CRISPR_Template')
        # At one point Document.find was returning -1 because it was calling str.find
        self.assertNotEqual(found, -1)
        self.assertIsNone(found)
        found = doc.find('http://sbols.org/CRISPR_Example/CRISPR_Template/1.0.0')
        self.assertNotEqual(found, -1)
        self.assertIsNotNone(found)

    def test_lookup(self):
        # Test simple key lookup via the __getitem__() method
        doc = sbol.Document()
        md = doc.moduleDefinitions.create('foo')
        md2 = doc.moduleDefinitions[md.displayId]
        self.assertEqual(md.identity, md2.identity)

    def test_crispr_lookup(self):
        doc = sbol.Document(TEST_LOCATION)
        uri = 'http://sbols.org/CRISPR_Example/CRISPR_Template/1.0.0'
        display_id = 'CRISPR_Template'
        md = doc.moduleDefinitions[uri]
        self.assertIsNotNone(md)
        self.assertEqual(md.identity, uri)
        self.assertEqual(md.displayId, display_id)
        # Test lookup by displayId. This was broken when loading from a file.
        md = doc.moduleDefinitions[display_id]
        self.assertIsNotNone(md)
        self.assertEqual(md.identity, uri)
        self.assertEqual(md.displayId, display_id)

    def test_find_property_value(self):
        # find_property_value wasn't comparing against the passed
        # `value` parameter, so it was returning all identities in the
        # document.
        sbol.setHomespace('http://examples.org')
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)
        doc = sbol.Document()
        cd = doc.moduleDefinitions.create('foo')
        cd.roles = sbol.SO_PROMOTER
        test_uri = 'http://examples.org/does/not/exist/1'
        matches = doc.find_property_value(sbol.SBOL_IDENTITY, test_uri)
        self.assertEqual(len(matches), 0)
        matches = doc.find_property_value(sbol.SBOL_ROLES, sbol.SO_PROMOTER)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], cd)

    def test_add_namespace(self):
        doc = sbol.Document()
        cd = doc.componentDefinitions.create('cd')
        cd.foo = sbol.property.TextProperty(cd, 'http://examples.org#foo',
                                            '0', '1', None, 'bar')
        doc.readString(doc.writeString())
        namespaces = [n[1] for n in doc.graph.namespace_manager.namespaces()]
        self.assertFalse('http://examples.org#' in namespaces)
        doc.addNamespace('http://examples.org#', 'examples')
        doc.readString(doc.writeString())
        namespaces = [n for n in doc.graph.namespace_manager.namespaces()]
        self.assertIn(('examples', rdflib.URIRef('http://examples.org#')),
                      namespaces)

    def test_namespace_fail(self):
        doc = sbol.Document()
        with self.assertRaises(ValueError):
            doc.addNamespace('http://examples.org', 'foo')

    def test_doc(self):
        doc = sbol.Document()
        # This was actually broken, so don't laugh at it
        self.assertEqual(doc.doc, doc)
        md = doc.moduleDefinitions.create('foo')
        self.assertEqual(doc, md.doc)
        m = md.modules.create('bar')
        self.assertEqual(doc, m.doc)

    def test_compare(self):
        doc = sbol.Document()
        doc2 = sbol.Document()
        self.assertTrue(doc.compare(doc2))
        doc.addNamespace('http://example.org#', 'bar')
        self.assertFalse(doc.compare(doc2))

    def test_get_top_level(self):
        doc = sbol.Document()
        self.assertTrue(hasattr(doc, 'getTopLevel'))
        # Expect a not found error in an empty document
        try:
            doc.getTopLevel('foo')
        except sbol.SBOLError as err:
            self.assertEqual(err.error_code(),
                             sbol.SBOLErrorCode.SBOL_ERROR_NOT_FOUND)
        else:
            self.fail('Expected SBOLError')
        cd = doc.componentDefinitions.create('foo')
        cd2 = doc.getTopLevel(cd.identity)
        self.assertEqual(cd, cd2)
        # Test access via string. Above was via URIRef.
        cd2 = doc.getTopLevel(str(cd.identity))
        self.assertEqual(cd, cd2)

    def test_addImplementation(self):
        doc = sbol.Document()
        with self.assertRaises(Exception):
            # This raises an attribute exception right now, and that
            # should change in the future.
            doc.addImplementation('foo')
        impl = sbol.Implementation(uri='foo')
        doc.addImplementation(impl)
        self.assertEqual(doc.implementations[0], impl)
        impl2 = sbol.Implementation(uri='bar')
        impl3 = sbol.Implementation(uri='baz')
        doc.addImplementation([impl2, impl3])
        self.assertEqual(doc.implementations[1], impl2)
        self.assertEqual(doc.implementations[2], impl3)

    def test_addImplementationGenerator(self):
        # We should be able to add implementations from a generator.
        # We should not be restricted to adding only a list. Any
        # Iterable should be fine.
        def impl_gen(count):
            for i in range(count):
                uri = 'impl{}'.format(i)
                yield sbol.Implementation(uri=uri)
        homespace = 'http://sbols.org/sbol_test'
        sbol.setHomespace(homespace)
        doc = sbol.Document()
        doc.addImplementation(impl_gen(3))
        uri_template = '{}/impl{}/1'
        self.assertEqual(doc.implementations[0].identity,
                         uri_template.format(homespace, '0'))
        self.assertEqual(doc.implementations[1].identity,
                         uri_template.format(homespace, '1'))
        self.assertEqual(doc.implementations[2].identity,
                         uri_template.format(homespace, '2'))

    def test_getImplementation(self):
        homespace = 'http://sbols.org/sbol_test'
        sbol.setHomespace(homespace)
        doc = sbol.Document()
        impl = sbol.Implementation(uri='foo')
        doc.addImplementation(impl)
        impl2 = sbol.Implementation(uri='bar')
        doc.addImplementation(impl2)
        # Get by index
        self.assertEqual(doc.getImplementation(0), impl)
        self.assertEqual(doc.getImplementation(1), impl2)
        # Get by short URI
        self.assertEqual(doc.getImplementation('foo'), impl)
        self.assertEqual(doc.getImplementation('bar'), impl2)
        # Get by full URI
        uri_template = '{}/Implementation/{}/1'
        uri = rdflib.URIRef(uri_template.format(homespace, 'foo'))
        self.assertEqual(doc.getImplementation(uri), impl)
        uri = rdflib.URIRef(uri_template.format(homespace, 'bar'))
        self.assertEqual(doc.getImplementation(uri), impl2)

    def test_bool(self):
        doc = sbol.Document()
        self.assertTrue(doc)

    def test_from_user_to_user(self):
        # Test proper conversion of user-facing types from RDFlib types
        # through the Property interfaces after serializing and de-serializing
        doc = sbol.Document()
        cd = doc.componentDefinitions.create('cd')
        cd.int_property = sbol.IntProperty(cd, 'http://examples.org', '0', '1', None, 42)
        self.assertEqual(42, cd.int_property)
        doc2 = sbol.Document()
        doc2.readString(doc.writeString())
        cd2 = doc2.componentDefinitions['cd']
        cd2.int_property = sbol.IntProperty(cd, 'http://examples.org', '0', '1', None)
        self.assertEqual(42, cd2.int_property)

    def test_range(self):
        # Test proper serializing and de-serializing of range properties
        doc = sbol.Document()
        cd = doc.componentDefinitions.create('cd')
        sa = cd.sequenceAnnotations.create('sa')
        r = sa.locations.createRange('r')
        r.start = 42
        doc2 = sbol.Document()
        doc2.readString(doc.writeString())
        r = doc2.componentDefinitions['cd'].sequenceAnnotations['sa'].locations['r']
        self.assertEqual(r.start, 42)

    def test_clone_document(self):
        doc = sbol.Document()
        doc2 = doc.copy()
        self.assertTrue(doc.compare(doc2))

    def test_validate(self):
        validate_online = sbol2.Config.getOption(sbol2.ConfigOptions.VALIDATE_ONLINE)
        try:
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE_ONLINE, False)
            doc = sbol2.Document()
            # Add a module definition
            doc.moduleDefinitions.create('md')
            result = doc.validate()
            expected = 'Valid.'
            self.assertEqual(result, expected)
        finally:
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE_ONLINE, validate_online)

    def test_validate_bad_url(self):
        validate_online = sbol2.Config.getOption(sbol2.ConfigOptions.VALIDATE_ONLINE)
        try:
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATOR_URL, self.validator_url + 'foo/bar')
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE_ONLINE, True)
            doc = sbol2.Document()
            with self.assertRaises(sbol2.SBOLError):
                doc.validate()
        finally:
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE_ONLINE, validate_online)

    def test_read_annotations(self):
        # Test reading a file with annotations and make sure they end
        # up where we expect them
        doc = sbol2.Document(filename=ANNO_LOCATION)
        # There is 1 component definition
        self.assertEqual(len(doc.componentDefinitions), 1)
        cd = doc.componentDefinitions[0]
        info_uri = rdflib.URIRef('http://partsregistry.org/information')
        sigma_uri = rdflib.URIRef('http://partsregistry.org/sigmafactor')
        regulation_uri = rdflib.URIRef('http://partsregistry.org/regulation')
        self.assertNotIn(info_uri, cd.properties)
        self.assertIn(info_uri, cd.owned_objects)
        # TODO What is the real API for accessing the extension object?
        info = cd.owned_objects[info_uri][0]
        self.assertIsNotNone(info)
        self.assertEqual(info.getPropertyValue(sigma_uri),
                         '//rnap/prokaryote/ecoli/sigma70')
        self.assertEqual(info.getPropertyValue(regulation_uri),
                         '//regulation/constitutive')

    def test_recursive_add(self):
        # Make sure that when an object gets added to a document
        # all of its child objects also get added.
        cd = sbol2.ComponentDefinition('cd')
        comp = sbol2.Component('cd_c')
        cd.components.add(comp)
        # Use of cd.sequence is dubious because the sequence attribute
        # isn't really there in SBOL 2.3. But it's the test case that
        # found the bug with recursive addition of objects, so we use it.
        seq = sbol2.Sequence('cd_seq')
        cd.sequence = seq
        doc = sbol2.Document()
        doc.addComponentDefinition(cd)
        # The cd and sequence should be in the document
        # The component is not top level, so doesn't get added
        self.assertEqual(2, len(doc))

    def test_add_attachment(self):
        doc = sbol2.Document()
        test_attach = sbol2.Attachment("TEST")
        doc.addAttachment(test_attach)
        self.assertEqual(1, len(doc.attachments))
        self.assertTrue(test_attach.compare(doc.attachments[0]))

    def test_get_collection(self):
        doc = sbol2.Document()
        self.assertTrue(hasattr(doc, 'getCollection'))
        c1 = doc.collections.create('c1')
        self.assertEqual(c1, doc.getCollection('c1'))
        self.assertEqual(c1, doc.getCollection(c1.identity))

    def test_read_string_clear(self):
        # Test that Document.readString() clears the document
        doc = sbol2.Document()
        cd = doc.componentDefinitions.create('test_cd')
        _ = cd.components.create('test_c')
        self.assertEqual(1, len(cd.components))
        doc.readString(doc.writeString())
        self.assertEqual(1, len(cd.components))
        cd = doc.componentDefinitions[cd.identity]
        self.assertEqual(1, len(cd.components))


class NonTopLevelExtension(sbol2.Identified):

    RDF_TYPE = 'http://example.org/test#NonTopLevelExtension'

    def __init__(self, uri='example'):
        super().__init__(uri=uri,
                         type_uri=NonTopLevelExtension.RDF_TYPE)


class TopLevelExtension(sbol2.TopLevel):

    RDF_TYPE = 'http://example.org/test#TopLevelExtension'

    def __init__(self, uri='example'):
        super().__init__(uri=uri,
                         type_uri=TopLevelExtension.RDF_TYPE)
        self.child = sbol2.OwnedObject(self, 'http://example.org/test#child',
                                       NonTopLevelExtension, '0', '1', [])


class ComponentDefinitionOverride(sbol2.ComponentDefinition):

    def __init__(self, uri='example'):
        super().__init__(uri=uri)


class TestDocumentExtensionObjects(unittest.TestCase):

    def test_register_extension_class(self):

        # Define extension object
        doc = sbol2.Document()
        cd = ComponentDefinitionOverride('cd')
        doc.add(cd)

        # Round-trip the extension data
        doc2 = sbol2.Document()
        doc2.readString(doc.writeString())
        cd = doc2.getExtensionObject(cd.identity)

        # Note the extension object's type is not preserved!
        self.assertIs(type(cd), sbol2.ComponentDefinition)
        self.assertIsNot(type(cd), ComponentDefinitionOverride)

        # Now register the class and attempt to round-trip again
        doc2 = sbol2.Document()
        sbol2.Config.register_extension_class(ComponentDefinitionOverride,
                                              sbol2.SBOL_COMPONENT_DEFINITION)
        doc2.readString(doc.writeString())
        cd = doc2.getExtensionObject(cd.identity)

        # This time the extension object's type is preserved!
        self.assertIs(type(cd), ComponentDefinitionOverride)
        self.assertIsNot(type(cd), sbol2.ComponentDefinition)

        # The object is stored in Document.componentDefinitions
        self.assertEqual(len(doc2.componentDefinitions), 1)

        # Restore
        sbol2.Config.register_extension_class(sbol2.ComponentDefinition,
                                              sbol2.SBOL_COMPONENT_DEFINITION)

    def test_get_extension_object(self):
        doc = sbol2.Document(CRISPR_LOCATION)

        # This returns an object. A TopLevel, not sure what type it is beyond that
        uri = 'http://sbols.org/CRISPR_Example/mKate_gene/1.0.0'
        obj = doc.getExtensionObject(uri)
        self.assertIsNotNone(obj)
        self.assertIsInstance(obj, sbol2.TopLevel)

        # This should raise a not found error because the URI is not
        # contained in the CRISPR test data
        uri = 'http://sbols.org/CRISPR_Example/mKate_genie/1.0.0'
        with self.assertRaises(sbol2.SBOLError) as cm:
            doc.getExtensionObject(uri)
        raised = cm.exception
        self.assertEqual(sbol2.SBOLErrorCode.SBOL_ERROR_NOT_FOUND,
                         raised.error_code())

    def test_add_extension_object(self):
        # We need to construct and add an extension object
        # It should then be accessible via getExtensionObject
        # We can also peel back the curtain and make sure the object
        #  is in doc.SBOLObjects and the URI is not in doc.OwnedObjects
        # Three kinds of things to add:
        #  1. An existing type, like ComponentDefinition
        cd = sbol2.ComponentDefinition('cd')
        doc = sbol2.Document()
        doc.addExtensionObject(cd)
        self.assertEqual(1, len(doc.componentDefinitions))
        obj = doc.getExtensionObject(cd.identity)
        self.assertEqual(cd, obj)

        #  2. A new type that is a TopLevel
        tle = TopLevelExtension('tle')
        doc = sbol2.Document()
        doc.addExtensionObject(tle)
        obj = doc.getExtensionObject(tle.identity)
        self.assertEqual(tle, obj)

        #  3. A new type that is not a TopLevel
        # This object won't be found. There is no way for the document to
        # hold on to the object if it isn't a TopLevel
        ntle = NonTopLevelExtension('ntle')
        doc = sbol2.Document()
        doc.addExtensionObject(ntle)
        with self.assertRaises(sbol2.SBOLError) as cm:
            doc.getExtensionObject(ntle.identity)
        raised = cm.exception
        self.assertEqual(sbol2.SBOLErrorCode.SBOL_ERROR_NOT_FOUND,
                         raised.error_code())
        obj = doc.find(ntle.identity)
        self.assertIsNone(obj)

    @unittest.expectedFailure  # See issue #368
    def test_parent_child_extensions(self):
        doc = sbol2.Document()
        tle = TopLevelExtension('tle')
        ntle = NonTopLevelExtension('ntle')
        tle.child = ntle
        doc.add(tle)
        self.assertEqual(len(doc.SBOLObjects), 1)

        # Verify that the parent-child relationship is preserved upon round-trip
        doc.readString(doc.writeString())
        self.assertEqual(len(doc.SBOLObjects), 1)
        self.assertIsNotNone(tle.child)

    def test_register_parent_child_extensions(self):
        # Show that we can load the parent/child relationship when the
        # extension classes are registered. The methods around this one
        # try to do the same thing without registration of the extension
        # classes
        #
        # This is all wrapped in a `try` so that we can clean up the
        # registration in the finally clause
        try:
            sbol2.Config.register_extension_class(TopLevelExtension,
                                                  TopLevelExtension.RDF_TYPE)
            sbol2.Config.register_extension_class(NonTopLevelExtension,
                                                  NonTopLevelExtension.RDF_TYPE)
            doc = sbol2.Document()
            tle = TopLevelExtension('tle')
            ntle = NonTopLevelExtension('ntle')
            tle.child = ntle
            doc.add(tle)
            self.assertEqual(len(doc.SBOLObjects), 1)

            # Verify that the parent-child relationship is preserved upon round-trip
            doc.readString(doc.writeString())
            self.assertEqual(len(doc.SBOLObjects), 1)
            self.assertIsNotNone(tle.child)
        finally:
            # Clean up
            tle_uri = rdflib.URIRef(TopLevelExtension.RDF_TYPE)
            ntle_uri = rdflib.URIRef(NonTopLevelExtension.RDF_TYPE)
            self.assertIn(tle_uri, sbol2.Config.SBOL_DATA_MODEL_REGISTER)
            self.assertIn(ntle_uri, sbol2.Config.SBOL_DATA_MODEL_REGISTER)
            del sbol2.Config.SBOL_DATA_MODEL_REGISTER[tle_uri]
            del sbol2.Config.SBOL_DATA_MODEL_REGISTER[ntle_uri]
            self.assertNotIn(tle_uri, sbol2.Config.SBOL_DATA_MODEL_REGISTER)
            self.assertNotIn(ntle_uri, sbol2.Config.SBOL_DATA_MODEL_REGISTER)

    @unittest.expectedFailure  # See Issue #368
    def test_parent_child_extensions_top_level(self):
        doc = sbol2.Document()
        tle = TopLevelExtension('tle')
        ntle = NonTopLevelExtension('ntle')
        tle.child = ntle
        doc.add(tle)
        self.assertEqual(len(doc.SBOLObjects), 1)

        # Verify that the parent-child relationship is preserved upon round-trip
        doc2 = sbol2.Document()
        doc2.readString(doc.writeString())
        self.assertNotIsInstance(doc2.get(ntle.identity), sbol2.TopLevel)
        self.assertEqual(len(doc.SBOLObjects), 1)
        self.assertIsNotNone(tle.child)

    def test_add_remove_citation(self):
        doc = sbol2.Document()
        sbol1_spec = 'http://www.nature.com/nbt/journal/v32/n6/full/nbt.2891.html'
        sbol2_spec = 'https://doi.org/10.1515/jib-2018-0001'
        sbol3_spec = ('https://sbolstandard.org/wp-content'
                      '/uploads/2020/04/SBOL3.0specification.pdf')
        self.assertEqual([], doc.citations)
        doc.addCitation(sbol1_spec)
        self.assertEqual([sbol1_spec], doc.citations)
        doc.addCitation(sbol2_spec)
        self.assertEqual([sbol1_spec, sbol2_spec], doc.citations)
        doc.addCitation(sbol3_spec)
        expected = [sbol1_spec, sbol2_spec, sbol3_spec]
        self.assertEqual(expected, doc.citations)
        doc.removeCitation(1)
        self.assertEqual([sbol1_spec, sbol3_spec], doc.citations)

    def test_add_remove_keyword(self):
        doc = sbol2.Document()
        keyword1 = 'http://example.com/keyword#key1'
        keyword2 = 'http://example.com/keyword#key2'
        keyword3 = 'http://example.com/keyword#key3'
        self.assertEqual([], doc.keywords)
        doc.addKeyword(keyword1)
        self.assertEqual([keyword1], doc.keywords)
        doc.addKeyword(keyword2)
        self.assertEqual([keyword1, keyword2], doc.keywords)
        doc.addKeyword(keyword3)
        expected = [keyword1, keyword2, keyword3]
        self.assertEqual(expected, doc.keywords)
        doc.removeKeyword(1)
        self.assertEqual([keyword1, keyword3], doc.keywords)

    def test_version(self):
        doc = sbol2.Document()
        self.assertIsNotNone(doc.version)
        old_version = doc.version
        doc.append(CRISPR_LOCATION, overwrite=True)
        self.assertIsNotNone(doc.version)
        self.assertEqual(old_version, doc.version)

    def test_idempotent_read(self):
        doc = sbol2.Document()
        doc.read(CRISPR_LOCATION)
        old_len = len(doc)
        cd_uri = 'http://sbols.org/CRISPR_Example/gRNA_b/1.0.0'
        cd = doc.componentDefinitions[cd_uri]
        self.assertEqual(1, len(cd.roles))

        # Now load the same file again and make sure the size of the
        # document didn't increase, and the number of roles on the
        # ComponentDefinition didn't increase.
        doc.append(CRISPR_LOCATION, overwrite=True)
        self.assertEqual(old_len, len(doc))
        cd = doc.componentDefinitions[cd_uri]
        self.assertEqual(1, len(cd.roles))

        # Now load the file one more time and make sure the size of the
        # document didn't increase, and the number of roles on the
        # ComponentDefinition didn't increase.
        doc.append(CRISPR_LOCATION, overwrite=True)
        self.assertEqual(old_len, len(doc))
        cd = doc.componentDefinitions[cd_uri]
        self.assertEqual(1, len(cd.roles))

    def test_idempotent_read2(self):
        validate_online = sbol2.Config.getOption(sbol2.ConfigOptions.VALIDATE_ONLINE)
        try:
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE_ONLINE, False)
            doc = sbol2.Document()
            doc.read(CRISPR_LOCATION)
            old_doc_len = len(doc)
            cd_uri = 'http://sbols.org/CRISPR_Example/gRNA_b/1.0.0'
            cd = doc.componentDefinitions['http://sbols.org/CRISPR_Example/gRNA_b/1.0.0']
            cd.components.create('c')
            old_component_len = len(cd.components)
            with tempfile.TemporaryDirectory() as tmpdirname:
                temp_file = os.path.join(tmpdirname, 'test.xml')
                doc.write(temp_file)
                doc.append(temp_file, overwrite=True)
            cd = doc.componentDefinitions[cd_uri]
            self.assertEqual(old_component_len, len(cd.components))
            self.assertEqual(old_doc_len, len(doc))
        finally:
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE_ONLINE, validate_online)

    def test_write_validation(self):
        # Test that write performs validation if requested
        # and skips validation if requested.
        validate_online = sbol2.Config.getOption(sbol2.ConfigOptions.VALIDATE_ONLINE)
        validate = sbol2.Config.getOption(sbol2.ConfigOptions.VALIDATE)
        verbose = sbol2.Config.getOption(sbol2.ConfigOptions.VERBOSE)
        try:
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE_ONLINE, False)
            doc = sbol2.Document()
            doc.moduleDefinitions.create('md1')
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE, True)
            sbol2.Config.setOption(sbol2.ConfigOptions.VERBOSE, True)
            with tempfile.TemporaryDirectory() as tmpdirname:
                test_file = os.path.join(tmpdirname, 'test.xml')
                with unittest.mock.patch('sys.stdout', new=io.StringIO()) as fake_out:
                    # Write to disk
                    result = doc.write(test_file)
                    self.assertEqual('Valid.', result)
                    # Expect timing output
                    output = fake_out.getvalue().strip()
                    self.assertTrue(output.startswith('Validation request took'))
                    self.assertTrue(output.endswith('seconds'))
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE, False)
            with tempfile.TemporaryDirectory() as tmpdirname:
                test_file = os.path.join(tmpdirname, 'test.xml')
                # Write to disk
                result = doc.write(test_file)
                self.assertTrue(result.startswith('Validation disabled.'))
        finally:
            # Reset original config values
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE, validate)
            sbol2.Config.setOption(sbol2.ConfigOptions.VERBOSE, verbose)
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE_ONLINE, validate_online)

    def test_append_string_no_overwrite(self):
        doc = sbol2.Document(CRISPR_LOCATION)
        with self.assertRaises(sbol2.SBOLError) as cm:
            doc.appendString(doc.writeString(), overwrite=False)
        exc = cm.exception
        self.assertEqual(sbol2.SBOLErrorCode.DUPLICATE_URI_ERROR,
                         exc.error_code())

    def test_append_string(self):
        doc = sbol2.Document()
        cd = doc.componentDefinitions.create('cd1')
        cd.components.create('c1')
        self.assertEqual(1, len(cd.components))
        doc.appendString(doc.writeString(), overwrite=True)
        self.assertEqual(1, len(cd.components))

    def test_append_string_2(self):
        doc = sbol2.Document()
        cd = doc.componentDefinitions.create('cd1')
        cd.components.create('c1')
        cd.roles = ['foo']
        self.assertEqual(1, len(cd.components))
        self.assertEqual('c1', cd.components[0].displayId)
        doc2 = sbol2.Document()
        cd_updated = doc2.componentDefinitions.create('cd1')
        cd_updated.components.create('c2')
        cd_updated.roles = ['bar']
        doc.appendString(doc2.writeString(), overwrite=True)
        self.assertEqual(1, len(cd.components))
        self.assertEqual('c2', cd.components[0].displayId)
        self.assertEqual(cd.roles, ['bar'])

    def test_import_from_format(self):
        validate_online = sbol2.Config.getOption(sbol2.ConfigOptions.VALIDATE_ONLINE)
        try:
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE_ONLINE, False)
            genbank_path = os.path.join(MODULE_LOCATION, 'resources', 'brevig-flu.gb')
            doc = sbol2.Document()
            self.assertEqual(0, len(doc))
            doc.importFromFormat(genbank_path)
            self.assertEqual(4, len(doc))
            # Maybe get something out, like a sequence, and make sure
            # it's there and starts with the right stuff.
            self.assertEqual(1, len(doc.sequences))
            display_id = 'AY130766_seq'
            sequence: sbol2.Sequence = doc.getSequence(display_id)
            self.assertTrue(sequence.elements.startswith('atgagtctt'))
            self.assertEqual(982, len(sequence.elements))
            # Ensure temp file does not exist after running Document.importFromFormat()
            # See https://github.com/SynBioDex/pySBOL2/issues/402
            self.assertFalse(os.path.exists('genbank2sbol.json'))
        finally:
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE_ONLINE, validate_online)

    def test_genbank_conversion(self):
        # Make sure an empty document successfully converts to GenBank
        # format.
        # See https://github.com/SynBioDex/pySBOL2/issues/401
        validate_online = sbol2.Config.getOption(sbol2.ConfigOptions.VALIDATE_ONLINE)
        try:
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE_ONLINE, False)
            doc = sbol2.Document()
            with tempfile.TemporaryDirectory() as tmpdirname:
                temp_file = os.path.join(tmpdirname, 'test.gb')
                doc.exportToFormat('GenBank', temp_file)
                self.assertTrue(os.path.exists(temp_file))
        finally:
            sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE_ONLINE, validate_online)


if __name__ == '__main__':
    unittest.main()
