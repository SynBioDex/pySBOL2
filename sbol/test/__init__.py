import unittest
import sys
from sbol.test.test_document import TestDocument
from sbol.test.test_identified import TestIdentified
from sbol.test.test_config import TestConfig
from sbol.test.test_property import TestProperty
from sbol.test.test_roundtrip import TestRoundTripSBOL2, TestRoundTripFailSBOL2


def runTests(test_list=(TestDocument, TestIdentified, TestConfig, TestProperty)):
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
