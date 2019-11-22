import unittest
import sbol


class TestOwnedObject(unittest.TestCase):

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
    @unittest.expectedFailure
    def test_non_beta_classes(self):
        # These are all in dbtl.py
        x = sbol.Analysis()
        x = sbol.Build()
        x = sbol.Design()

    def test_create(self):
        doc = sbol.Document()
        thing = doc.moduleDefinitions.create('thing1')
        self.assertIs(type(thing), sbol.ModuleDefinition)


if __name__ == '__main__':
    unittest.main()
