import locale
import logging
import os
import unittest
import tempfile
import shutil
import rdflib
import rdflib.compare
import sbol2

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
SBOL_TEST_SUITE = os.path.join(MODULE_LOCATION, 'SBOLTestSuite')

DEBUG_ENV_VAR = 'SBOL_TEST_DEBUG'


class TestRoundTripSBOL2(unittest.TestCase):

    def setUp(self):
        # Create temp directory
        self.temp_out_dir = tempfile.mkdtemp()
        # Disable validation to avoid unnecessary round trips
        # to the online validator
        sbol2.Config.setOption(sbol2.ConfigOptions.VALIDATE, False)
        self.logger = logging.getLogger('sbol2.test')
        if not self.logger.hasHandlers():
            logging.basicConfig()
        if DEBUG_ENV_VAR in os.environ:
            self.logger.setLevel(logging.DEBUG)

    def tearDown(self):
        # Remove directory after the test
        if self.temp_out_dir:
            shutil.rmtree(self.temp_out_dir)
            self.temp_out_dir = None

    def run_round_trip_file(self, test_path):
        """Runs a round trip test on the file at the given path.
        Path can be relative or absolute.
        """
        filename = os.path.basename(test_path)
        test2_path = os.path.join(self.temp_out_dir, filename)
        # Read the document, then write it back to disk
        doc = sbol2.Document()
        doc.read(test_path)
        doc.write(test2_path)

        # Read the newly written document and compare results
        doc2 = sbol2.Document()
        doc2.read(test2_path)
        self.assertTrue(doc.compare(doc2))

        # Now compare the graphs in RDF
        g1 = rdflib.Graph()
        g1.load(test_path)
        iso1 = rdflib.compare.to_isomorphic(g1)
        g2 = rdflib.Graph()
        g2.load(test2_path)
        iso2 = rdflib.compare.to_isomorphic(g2)
        rdf_diff = rdflib.compare.graph_diff(iso1, iso2)
        if rdf_diff[1] or rdf_diff[2]:
            self.logger.warning('Detected %d different RDF triples in %s' %
                                (len(rdf_diff[1]) + len(rdf_diff[2]), test_path))
            if not self.logger.isEnabledFor(logging.DEBUG):
                self.logger.warning('Set environment variable %s to see details',
                                    DEBUG_ENV_VAR)
            for stmt in rdf_diff[1]:
                self.logger.debug('Only in original: %r', stmt)
            for stmt in rdf_diff[2]:
                self.logger.debug('Only in loaded: %r', stmt)
            self.fail('Differences in RDF detected')

    def run_round_trip_dir(self, directory, skip_list=None):
        dir_name = os.path.basename(directory)
        for filename in os.listdir(directory):
            if skip_list and filename in skip_list:
                continue
            if filename.endswith('rdf') or filename.endswith('xml'):
                test_path = os.path.join(directory, filename)
                with self.subTest(filename=os.path.join(dir_name, filename)):
                    self.setUp()
                    self.run_round_trip_file(test_path)
                    self.tearDown()

    def test_sbol2_files(self):
        test_dir = os.path.join(SBOL_TEST_SUITE, 'SBOL2')
        # test_source_location.xml has a serialization error in SBOL2Serialize
        self.run_round_trip_dir(test_dir)

    def test_sbol2_bp_files(self):
        test_dir = os.path.join(SBOL_TEST_SUITE, 'SBOL2_bp')
        self.run_round_trip_dir(test_dir)

    def test_sbol2_ic_files(self):
        test_dir = os.path.join(SBOL_TEST_SUITE, 'SBOL2_ic')
        self.run_round_trip_dir(test_dir)

    def test_sbol2_nc_files(self):
        test_dir = os.path.join(SBOL_TEST_SUITE, 'SBOL2_nc')
        # SBOL1and2Test.xml has a namespace error when serializing
        # Handle it for now as an expected failure below
        self.run_round_trip_dir(test_dir, ['SBOL1and2Test.xml'])

    @unittest.expectedFailure  # See issue #210
    def test_sbol_1_and_2(self):
        # Invalid namespace prefix in lxml.etree when serializing the document
        test_path = os.path.join(SBOL_TEST_SUITE, 'SBOL2_nc',
                                 'SBOL1and2Test.xml')
        self.run_round_trip_file(test_path)

    def test_utf8_roundtrip(self):
        # Test loading a utf-8 SBOL file without LANG set. This was a
        # bug at one time, and only shows itself when LANG is unset.
        # Here we simulate that by temporarily setting the locale to
        # the generic 'C' locale.
        test_path = os.path.join(SBOL_TEST_SUITE, 'SBOL2', 'pICSL50014.xml')
        loc = locale.getlocale()
        try:
            locale.setlocale(locale.LC_ALL, 'C')
            self.run_round_trip_file(test_path)
        finally:
            locale.setlocale(locale.LC_ALL, loc)


if __name__ == '__main__':
    unittest.main()
