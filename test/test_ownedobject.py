import unittest

import sbol2
import sbol2 as sbol


class TestOwnedObject(unittest.TestCase):

    def setUp(self):
        # All tests in this file use the default homespace
        sbol.setHomespace('http://examples.org')
        # All tests in this file use SBOL compliant URIs
        sbol.Config.setOption(sbol.ConfigOptions.SBOL_COMPLIANT_URIS.value, True)
        sbol.Config.setOption(sbol.ConfigOptions.SBOL_TYPED_URIS.value, True)

    # Test all the classes that contain OwnedObjects to be sure they
    # provide a callable builder argument
    def test_containers(self):
        # Note: Alphabetical Order
        x = sbol.Activity()
        x = sbol.CombinatorialDerivation()
        x = sbol.Component()
        x = sbol.ComponentDefinition()
        x = sbol.Document()
        x = sbol.Interaction()
        x = sbol.Module()
        x = sbol.ModuleDefinition()
        x = sbol.Participation()
        x = sbol.SequenceAnnotation()

    # These are classes that are considered outside the core, and thus
    # outside the beta. They use OwnedObject, so they will need to be
    # updated in the future.
    @unittest.expectedFailure  # See issue #310
    def test_non_beta_classes(self):
        # These are all in dbtl.py
        x = sbol.Analysis()
        x = sbol.Build()
        x = sbol.Design()

    def test_create(self):
        doc = sbol.Document()
        thing = doc.moduleDefinitions.create('thing1')
        self.assertIs(type(thing), sbol.ModuleDefinition)
        # md = doc.moduleDefinitions.get(thing.identity)
        # self.assertEqual(thing.identity, md.identity)

    def test_create2(self):
        # Test that the create adds the new object to the owned object.
        #
        # This seems to be a problem in the implementation of
        # ModuleDefinition.assemble()
        doc = sbol.Document()
        md = doc.moduleDefinitions.create('thing1')
        self.assertEqual(len(md.modules), 0)
        module = md.modules.create('thing2')
        self.assertEqual(len(md.modules), 1)

    def test_uri_generation(self):
        doc = sbol.Document()
        md = doc.moduleDefinitions.create('foo')
        expected = 'http://examples.org/ModuleDefinition/foo/1'
        self.assertEqual(md.identity, expected)
        m = md.modules.create('bar')
        expected = 'http://examples.org/ModuleDefinition/foo/bar/1'
        self.assertEqual(m.identity, expected)

    def test_displayId_lookup(self):
        # Test lookup of an object by its display Id via the
        # __getitem__() method.
        doc = sbol.Document()
        md = doc.moduleDefinitions.create('foo')
        m = md.modules.create('bar')
        m2 = md.modules['bar']
        self.assertEqual(m.identity, m2.identity)

    def test_uri_lookup(self):
        # Test lookup of an object by its URI via the
        # __getitem__() method.
        doc = sbol.Document()
        md = doc.moduleDefinitions.create('foo')
        m = md.modules.create('bar')
        m2 = md.modules[m.identity]
        self.assertEqual(m.identity, m2.identity)

    def test_assignment(self):
        doc = sbol.Document()
        md = doc.moduleDefinitions.create('foo')
        m1 = sbol.Module('m1')
        m2 = sbol.Module('m2')
        md.modules = [m1, m2]
        self.assertEqual(list(md.modules), [m1, m2])

    def test_value(self):
        doc = sbol2.Document()
        self.assertEqual([], doc.componentDefinitions.value)

    def test_set_no_doc(self):
        # Add a module when the parent module definition is not in a
        # Document
        md = sbol.ModuleDefinition('foo')
        m1 = sbol.Module('m1')
        md.modules.set([m1])
        self.assertEqual(m1, md.modules.get(0))
        self.assertEqual(m1, md.modules.find(m1.identity))

    def test_find(self):
        md = sbol.ModuleDefinition('foo')
        m1 = md.modules.create('m1')
        self.assertEqual(m1, md.modules.get(0))
        self.assertEqual(m1, md.modules.find(m1.identity))
        self.assertEqual(m1, md.modules.find(m1.displayId))
        self.assertEqual(m1, md.modules.find(str(m1.displayId)))
        self.assertEqual(m1, md.modules.find('m1'))

    def test_get_by_persistent_id(self):
        # This grows out of an issue with SYNBICT
        # Searching by persistent id was not working
        sbol2.Config.setHomespace('http://synbict.org')
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, False)
        doc = sbol2.Document()
        md = doc.moduleDefinitions.create('nand_circuit')
        # Search by the persistent identity
        search_string = md.persistentIdentity
        self.assertEqual(md, doc.getModuleDefinition(search_string))

    def test_remove_by_display_id(self):
        doc = sbol2.Document()
        cd = doc.componentDefinitions.create('cd1')
        self.assertIn(cd.displayId, doc.componentDefinitions)
        self.assertIn(cd.identity, doc.SBOLObjects)
        doc.componentDefinitions.remove(cd.displayId)
        self.assertNotIn(cd.displayId, doc.componentDefinitions)
        self.assertNotIn(cd.identity, doc.SBOLObjects)

    def test_remove_by_identity(self):
        doc = sbol2.Document()
        cd = doc.componentDefinitions.create('cd1')
        self.assertIn(cd.identity, doc.componentDefinitions)
        self.assertIn(cd.identity, doc.SBOLObjects)
        doc.componentDefinitions.remove(cd.identity)
        self.assertNotIn(cd.identity, doc.componentDefinitions)
        self.assertNotIn(cd.identity, doc.SBOLObjects)

    def test_remove_by_persistent_identity(self):
        doc = sbol2.Document()
        cd = doc.componentDefinitions.create('cd1')
        self.assertIn(cd.persistentIdentity, doc.componentDefinitions)
        self.assertIn(cd.identity, doc.SBOLObjects)
        doc.componentDefinitions.remove(cd.persistentIdentity)
        self.assertNotIn(cd.persistentIdentity, doc.componentDefinitions)
        self.assertNotIn(cd.identity, doc.SBOLObjects)

    def test_init_store(self):
        # Ensure that property constructors initialize the parent
        # object's value store
        obj = sbol2.SBOLObject()
        type_uri = 'http://example.com#thing'
        obj.thing = sbol2.OwnedObject(obj, type_uri, int, '0', '*')
        self.assertIn(type_uri, obj.owned_objects)
        self.assertEqual([], obj.owned_objects[type_uri])
        self.assertEqual([], obj.thing.value)

    def test_duplicate_uri_no_doc(self):
        cd = sbol2.ComponentDefinition('cd')
        cd.sequenceAnnotations.create('sa')
        with self.assertRaises(sbol2.SBOLError) as cm:
            cd.sequenceAnnotations.create('sa')
        raised = cm.exception
        self.assertEqual(raised.error_code(),
                         sbol2.SBOLErrorCode.SBOL_ERROR_URI_NOT_UNIQUE)

    def test_duplicate_uri_in_doc(self):
        doc = sbol2.Document()
        cd = doc.componentDefinitions.create('cd')
        cd.sequenceAnnotations.create('sa')
        with self.assertRaises(sbol2.SBOLError) as cm:
            cd.sequenceAnnotations.create('sa')
        raised = cm.exception
        self.assertEqual(raised.error_code(),
                         sbol2.SBOLErrorCode.SBOL_ERROR_URI_NOT_UNIQUE)


if __name__ == '__main__':
    unittest.main()
