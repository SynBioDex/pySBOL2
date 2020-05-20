import logging
import os
import unittest

import sbol2

LOGGER_NAME = 'sbol2.test'
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

    def init_tutorial(self):
        # Set the default namespace (e.g. "http://my_namespace.org")
        namespace = "http://my_namespace.org"
        homespace = sbol2.setHomespace(namespace)

        # Test homespace
        self.assertIsNone(homespace)
        self.assertEqual(sbol2.getHomespace(), namespace)

        # Create a new SBOL document
        doc = sbol2.Document()

        # Test empty document
        self.assertIsInstance(doc, sbol2.Document)
        self.assertEqual(len(doc), 0)

        return doc

    def get_device_from_xml(self, doc):
        # Load some generic parts from `parts.xml` into another Document
        generic_parts = sbol2.Document(PARTS_FILE)

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

    def get_device_from_synbiohub(self, doc):
        # Start an interface to igem's public part shop on
        # SynBioHub. Located at `https://synbiohub.org/public/igem`
        partshop = sbol2.PartShop('https://synbiohub.org/public/igem')

        # Search the part shop for parts from the iGEM interlab study
        # using the search term `interlab`
        records = partshop.search('interlab')

        # Import the medium strength device into your document
        medium_device_uri = records[0].identity
        self.assertEqual(32, len(doc))
        partshop.pull(medium_device_uri, doc)
        self.assertEqual(35, len(doc))

    def extract_cds_from_devices(self, doc):
        # Extract the medium strength promoter `BBa_J23106` from your document.
        # TODO: BBa_j23106 does not appear in the document
        # medium_strength_promoter = doc.componentDefinitions['BBa_J23106']

        # Extract the ribosomal binding site (rbs) `Q2` from your document.
        self.rbs = doc.componentDefinitions['Q2']
        self.assertEqual('http://my_namespace.org/ComponentDefinition/Q2/1',
                         self.rbs.identity)

        # Extract the coding region (cds) `LuxR` from your document.
        self.cds = doc.componentDefinitions['LuxR']
        self.assertEqual('http://my_namespace.org/ComponentDefinition/LuxR/1',
                         self.cds.identity)

        # Extract the terminator `ECK120010818` from your document.
        self.terminator = doc.componentDefinitions['ECK120010818']
        self.assertEqual('http://my_namespace.org/ComponentDefinition/ECK120010818/1',
                         self.terminator.identity)

    def test_tutorial(self):
        doc = self.init_tutorial()
        self.get_device_from_xml(doc)
        self.get_device_from_synbiohub(doc)
        self.extract_cds_from_devices(doc)
