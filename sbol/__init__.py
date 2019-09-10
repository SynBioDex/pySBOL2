__version__ = '3.0.0'

# NOTE: I have to manually specify 'sbol'. Why?
from sbol.document import Document
from sbol.componentdefinition import ComponentDefinition
from sbol.moduledefinition import ModuleDefinition
from sbol.sequence import Sequence

# NOTE: I have to manually include all of these, which is quite a pain.
__all__ = ['Document', 'ComponentDefinition', 'ModuleDefinition', 'Sequence']


def testSBOL():
    """
    Function to test pySBOL API.
    """
    import sbol.test as unit_tests
    unit_tests.runTests()


def testRoundTrip():
    """
    Function to run test suite for pySBOL
    """
    import sbol.test as unit_tests
    unit_tests.runRoundTripTests()


def testSBOLHook():
    """
    Function to test pySBOL API. Exits 1 or 0 depending on whether
    all tests pass.
    :return:
    """
    import sbol.test as unit_tests
    result = unit_tests.runTests()
    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)
