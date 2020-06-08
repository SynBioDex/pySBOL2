import os
import unittest

import sbol2

MY_DIR = os.path.dirname(os.path.abspath(__file__))
PARTS_FILE = os.path.join(MY_DIR, 'resources', 'tutorial', 'parts.xml')
PROMOTER_URI = 'https://synbiohub.org/public/igem/BBa_R0040/1'

expected_sequence = '\
tccctatcagtgatagagattgacatccctatcagtgatagagatactgagcactactagagGCCATGCCATTGGCTTTTGATAGAGGAC\
AACTACTAGtactagATGAACATTAAAAATATAAATGCTAATGAGAAGATAATTGATAAAATTAAAACTTGTAATAATAATAAAGATATTAATCAAT\
GTTTATCTGAAATAGCAAAGATAATACATTGTGAATATTACCTATTCGCTATTATCTATCCTCACTCAATAATTAAACCTGATGTTTCAATTATAGA\
TAATTACCCTGAAAAATGGCGTAAATATTATGATGATGCCGGACTACTAGAATATGACCCTGTAGTCGATTACTCTAAGTCCCATCATTCACCAATT\
AATTGGAACGTATTCGAAAAAAAAACAATAAAAAAAGAGTCTCCGAATGTAATAAAAGAAGCACAGGAATCGGGACTCATTACTGGATTTAGCTTTC\
CAATTCATACTGCAAGTAATGGTTTTGGAATGCTCAGTTTTGCTCATTCAGATAAAGATATTTATACTGACAGTTTATTTTTACACGCTAGTACAAA\
TGTACCATTAATGCTTCCTTCTTTAGTCGATAATTATCAAAAAATAAATACGACACGTAAAAAGTCAGATTCTATTTTAACAAAAAGAGAAAAAGAA\
TGCTTAGCGTGGGCGAGTGAAGGAAAAAGTACATGGGATATTTCAAAAATACTTGGCTGCAGTGAGCGTACTGTCACTTTTCATTTAACCAATACTC\
AAATGAAACTCAATACAACTAACCGCTGCCAAAGTATTTCTAAAGCAATTTTAACTGGCGCCATTAATTGTCCATACCTTAAAAATTAAtactagag\
GTCAGTTTCACCTGTTTTACGTAAAAACCCGCTTCGGCGGGTTTTTACTTTTGG'


class TestSbolTutorial(unittest.TestCase):
    """Encode the SBOL tutorial in a unit test.

    See https://github.com/SynBioDex/Community-Media/blob/master/2019/IWBDA19/workshop/solution.ipynb
    """

    def setUp(self):
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS, True)

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
        self.assertEqual(32, len(doc))
        partshop.pull(PROMOTER_URI, doc)
        self.assertEqual(35, len(doc))

    def extract_cds_from_devices(self, doc):
        # Extract the promoter from your document.
        self.promoter = doc.componentDefinitions[PROMOTER_URI]
        self.assertEqual(PROMOTER_URI, self.promoter.identity)

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

    def create_new_device(self, doc: sbol2.Document):
        # Create a new empty device named `my_device`
        my_device = doc.componentDefinitions.create('my_device')

        # Assemble the new device from the promoter, rbs, cds, and terminator from above.
        my_device.assemblePrimaryStructure([self.promoter,
                                            self.rbs,
                                            self.cds,
                                            self.terminator],
                                           sbol2.IGEM_STANDARD_ASSEMBLY)
        # Expecting the 4 components above plus 3 assembly scars
        self.assertEqual(7, len(my_device.getPrimaryStructure()))

        # Set the role of the device with the Sequence Ontology term `gene`
        my_device.roles = [sbol2.SO_GENE]

        # Compile the sequence for the new device
        my_device.compile()
        self.assertEqual(expected_sequence, my_device.sequence.elements)

    def test_tutorial(self):
        doc = self.init_tutorial()
        self.get_device_from_xml(doc)
        self.get_device_from_synbiohub(doc)
        self.extract_cds_from_devices(doc)
        self.create_new_device(doc)
