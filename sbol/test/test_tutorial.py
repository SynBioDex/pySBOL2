import logging
import os
import unittest

import sbol

LOGGER_NAME = 'sbol.test'
DEBUG_ENV_VAR = 'SBOL_TEST_DEBUG'
MY_DIR = os.path.dirname(os.path.abspath(__file__))
PARTS_FILE = os.path.join(MY_DIR, 'resources', 'tutorial', 'parts.xml')


class TestSbolTutorial(unittest.TestCase):
    """Encode the SBOL tutorial in a unit test.

    See https://github.com/SynBioDex/Community-Media/blob/master/2019/IWBDA19/workshop/solution.ipynb
    """

    def setUp(self):
        self.logger = logging.getLogger(LOGGER_NAME)
        if not self.logger.hasHandlers():
            logging.basicConfig()
        if DEBUG_ENV_VAR in os.environ:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug('Debug logging enabled')

    @unittest.expectedFailure
    def test_tutorial(self):
        # Set the default namespace (e.g. “http://my_namespace.org”)
        namespace = "http://my_namespace.org"
        homespace = sbol.setHomespace(namespace)

        # Test homespace
        self.assertIsNone(homespace)
        self.assertEqual(sbol.getHomespace(), namespace)

        # Create a new SBOL document
        doc = sbol.Document()

        # Test empty document
        self.assertIsInstance(doc, sbol.Document)
        self.assertEqual(len(doc), 0)

        # Load some generic parts from `parts.xml` into another Document
        generic_parts = sbol.Document(PARTS_FILE)

        # Test loaded document
        self.assertEqual(len(generic_parts), 32)
        self.assertEqual(len(list(generic_parts.componentDefinitions)), 14)
        self.assertEqual(len(list(generic_parts.moduleDefinitions)), 0)

        # Copy the parts from `parts.xml` into your document.
        # Be sure to specify the original namespace `http://examples.org`
        generic_parts.copy("http://examples.org", doc)

        # Test copied document
        self.assertEqual(len(doc), 32)
        self.assertEqual(len(list(doc.componentDefinitions)), 14)
        self.assertEqual(len(list(doc.moduleDefinitions)), 0)
