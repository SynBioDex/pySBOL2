import unittest
import sys
from .test_componentdefinition import TestComponentDefinitions
from .test_constants import TestConstants
from .test_design import TestDesign
from .test_document import TestDocument
from .test_identified import TestIdentified
from .test_config import TestConfig
from .test_moduledefinition import TestModuleDefinition
from .test_object import TestObject
from .test_ownedobject import TestOwnedObject
from .test_partshop import TestPartShop
from .test_property import TestProperty
from .test_referencedobjects import TestReferencedObjects
from .test_roundtrip import TestRoundTripSBOL2, TestRoundTripFailSBOL2
from .test_tutorial import TestSbolTutorial


def runTests(test_list=None):
    if test_list is None:
        test_list = [
            TestComponentDefinitions,
            TestConstants,
            TestConfig,
            TestDesign,
            TestDocument,
            TestIdentified,
            TestModuleDefinition,
            TestObject,
            TestOwnedObject,
            TestPartShop,
            TestProperty,
            TestReferencedObjects,
            TestSbolTutorial,
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
