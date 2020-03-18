import unittest
import sys
from .test_collection import TestCollection
from .test_componentdefinition import TestComponentDefinitions
from .test_constants import TestConstants
from .test_design import TestDesign
from .test_document import TestDocument
from .test_error import TestError
from .test_identified import TestIdentified
from .test_implementation import TestImplementation
from .test_interaction import TestInteraction
from .test_config import TestConfig
from .test_moduledefinition import TestModuleDefinition
from .test_object import TestObject
from .test_ownedobject import TestOwnedObject
from .test_partshop import TestPartShop
from .test_property import TestProperty
from .test_referencedobject import TestReferencedObjects
from .test_roundtrip import TestRoundTripSBOL2, TestRoundTripFailSBOL2
from .test_sequence import TestSequence
from .test_style import TestStyle
from .test_tutorial import TestSbolTutorial
from .test_validation import TestValidation


def runTests(test_list=None):
    if test_list is None:
        test_list = [
            TestCollection,
            TestComponentDefinitions,
            TestConfig,
            TestConstants,
            TestDesign,
            TestDocument,
            TestError,
            TestIdentified,
            TestImplementation,
            TestInteraction,
            TestModuleDefinition,
            TestObject,
            TestOwnedObject,
            TestPartShop,
            TestProperty,
            TestReferencedObjects,
            TestSbolTutorial,
            TestSequence,
            TestStyle,
            TestValidation,
        ]
    suite_list = []
    loader = unittest.TestLoader()
    for test_class in test_list:
        suite = loader.loadTestsFromTestCase(test_class)
        suite_list.append(suite)
    full_test_suite = unittest.TestSuite(suite_list)
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(full_test_suite)
    return result


def runRoundTripTests(test_list=(TestRoundTripSBOL2, TestRoundTripFailSBOL2)):
    result = runTests(test_list)
    return result
