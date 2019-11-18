__version__ = '3.0.0'

# Anything imported here is part of the public API. Limit what gets
# imported to only those things that are actually needed.
#
# We should be using `__all__` for the list of exported items for this
# module, but the list of items in `constants.py` is extensive. So
# instead of `__all__`, we will try to be careful about what gets
# imported into this file. In the absence of __all__, all imported
# symbols are also exported.
from .config import Config, ConfigOptions, hasHomespace, setHomespace
from .constants import *
from .document import Document
from .componentdefinition import ComponentDefinition
from .moduledefinition import ModuleDefinition
from .sbolerror import SBOLError
from .sequence import Sequence


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
