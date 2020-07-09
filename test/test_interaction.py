import unittest

import sbol2 as sbol
import sbol2


class TestInteraction(unittest.TestCase):

    def __init__(self, *args):
        super().__init__(*args)
        self.homespace = 'http://example.org'

    def make_identity(self, homespace, name, version, tipe='Interaction'):
        uri = '{}/{}/{}/{}'
        return uri.format(homespace, tipe, name, version)

    def setUp(self):
        # Always reset homespace
        sbol.setHomespace(self.homespace)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)
        sbol.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS, True)

    def testEmptyConstructor(self):
        # This is the default name in the interaction constructor
        name = 'example'
        i = sbol.Interaction()
        expected_identity = self.make_identity(self.homespace, name,
                                               sbol.VERSION_STRING)
        self.assertEqual(i.identity, expected_identity)
        self.assertEqual(i.displayId, name)
        self.assertEqual(i.version, sbol.VERSION_STRING)
        self.assertEqual(i.rdf_type, sbol.SBOL_INTERACTION)
        md = sbol.ModuleDefinition()
        md.interactions.add(i)
        self.assertEqual(len(md.interactions), 1)

    def test1ArgConstructor(self):
        name = 'foo'
        i = sbol.Interaction(name)
        expected_identity = self.make_identity(self.homespace, name,
                                               sbol.VERSION_STRING)
        self.assertEqual(i.identity, expected_identity)
        self.assertEqual(i.displayId, name)
        self.assertEqual(i.version, sbol.VERSION_STRING)
        self.assertEqual(i.rdf_type, sbol.SBOL_INTERACTION)
        md = sbol.ModuleDefinition()
        md.interactions.add(i)
        self.assertEqual(len(md.interactions), 1)

    def test2ArgConstructor(self):
        name = 'foo'
        i = sbol.Interaction(name, sbol.SBO_INHIBITION)
        expected_identity = self.make_identity(self.homespace, name,
                                               sbol.VERSION_STRING)
        self.assertEqual(i.identity, expected_identity)
        self.assertEqual(i.displayId, name)
        self.assertEqual(i.types, [sbol.SBO_INHIBITION])
        self.assertEqual(i.rdf_type, sbol.SBOL_INTERACTION)
        md = sbol.ModuleDefinition()
        md.interactions.add(i)
        self.assertEqual(len(md.interactions), 1)

    def test3ArgConstructor(self):
        name = 'foo'
        rdf_type = sbol.SBOL_INTERACTION + '2'
        i = sbol.Interaction(name, sbol.SBO_INHIBITION, type_uri=rdf_type)
        expected_identity = self.make_identity(self.homespace, name,
                                               sbol.VERSION_STRING,
                                               'Interaction2')
        self.assertEqual(i.identity, expected_identity)
        self.assertEqual(i.displayId, name)
        self.assertEqual(i.types, [sbol.SBO_INHIBITION])
        self.assertEqual(i.rdf_type, rdf_type)
        # Verify that when added to a module definition, this
        # interaction is in the list of interactions despite having a
        # different rdf_type. That's because the rdf_type is not taken
        # into account when adding to the module definition's
        # interactions property.
        md = sbol.ModuleDefinition()
        md.interactions.add(i)
        self.assertEqual(len(md.interactions), 1)
