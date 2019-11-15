import locale
import logging
import os
import unittest
import tempfile
import shutil
import sys
import rdflib
import rdflib.compare
from sbol.document import *

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
TEST_LOC_SBOL2 = os.path.join(MODULE_LOCATION, 'SBOLTestSuite', 'SBOL2')
FILES_SBOL2 = os.listdir(TEST_LOC_SBOL2)
FILES_SBOL2.sort()
TEST_FILES_SBOL2 = []
for i in FILES_SBOL2:
    if i.endswith('rdf'):
        TEST_FILES_SBOL2.append(i)
    if i.endswith('xml'):
        TEST_FILES_SBOL2.append(i)

DEBUG_ENV_VAR = 'SBOL_TEST_DEBUG'


class TestRoundTripSBOL2(unittest.TestCase):

    def setUp(self):
        # Create temp directory
        self.temp_out_dir = tempfile.mkdtemp()
        self.logger = logging.getLogger('sbol.test')
        if not self.logger.hasHandlers():
            logging.basicConfig()
        if DEBUG_ENV_VAR in os.environ:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug('Debug logging enabled')

    def tearDown(self):
        # Remove directory after the test
        if self.temp_out_dir:
            shutil.rmtree(self.temp_out_dir)
            self.temp_out_dir = None

    def run_round_trip(self, test_file):
        split_path = os.path.splitext(test_file)
        self.doc = Document()   # Document for read and write
        self.doc.read(os.path.join(TEST_LOC_SBOL2,
                                   split_path[0] + split_path[1]))
        self.doc.write(os.path.join(self.temp_out_dir, split_path[0] +
                                    '_out' + split_path[1]))

        self.doc2 = Document()  # Document to compare for equality
        self.doc2.read(os.path.join(self.temp_out_dir, split_path[0] +
                                    '_out' + split_path[1]))
        self.assertTrue(self.doc.compare(self.doc2))

        # Now compare the graphs in RDF
        test_path = os.path.join(TEST_LOC_SBOL2, test_file)
        test2_file = split_path[0] + '_out' + split_path[1]
        test2_path = os.path.join(self.temp_out_dir, test2_file)

        g1 = rdflib.Graph()
        g1.load(test_path)
        iso1 = rdflib.compare.to_isomorphic(g1)
        g2 = rdflib.Graph()
        g2.load(test2_path)
        iso2 = rdflib.compare.to_isomorphic(g2)
        rdf_diff = rdflib.compare.graph_diff(iso1, iso2)
        if rdf_diff[1] or rdf_diff[2]:
            self.logger.warning('Detected %d differences in RDF',
                                len(rdf_diff[1]) + len(rdf_diff[2]))
            if not self.logger.isEnabledFor(logging.DEBUG):
                self.logger.warning('Set environment variable %s to see details',
                                    DEBUG_ENV_VAR)
            for stmt in rdf_diff[1]:
                self.logger.debug('Only in original: %r', stmt)
            for stmt in rdf_diff[2]:
                self.logger.debug('Only in loaded: %r', stmt)

    def test_sbol2_files(self):
        subtest = 1
        for f in TEST_FILES_SBOL2:
            if os.path.basename(f) == 'test_source_location.xml':
                # This one has an error. Temporarily give it its own
                # test and expect the failure.
                continue
            with self.subTest(filename=f):
                self.setUp()
                self.run_round_trip(f)
                self.tearDown()

    @unittest.expectedFailure
    def test_source_location(self):
        self.run_round_trip(os.path.join(TEST_LOC_SBOL2, 'test_source_location.xml'))

    def test_utf8_roundtrip(self):
        # Test loading a utf-8 SBOL file without LANG set. This was a
        # bug at one time, and only shows itself when LANG is unset.
        # Here we simulate that by temporarily setting the locale to
        # the generic 'C' locale.
        loc = locale.getlocale()
        try:
            locale.setlocale(locale.LC_ALL, 'C')
            self.run_round_trip(os.path.join(TEST_LOC_SBOL2, 'pICSL50014.xml'))
        finally:
            locale.setlocale(locale.LC_ALL, loc)


class TestRoundTripFailSBOL2(unittest.TestCase):
    def setUp(self):
        # Create temp directory
        self.temp_out_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove directory after the test
        shutil.rmtree(self.temp_out_dir)

    def run_round_trip_assert_fail(self, test_file):
        split_path = os.path.splitext(test_file)
        self.doc = Document()   # Document for read and write
        self.doc.read(os.path.join(TEST_LOC_SBOL2, split_path[0] + split_path[1]))
        self.doc.write(os.path.join(self.temp_out_dir,
                                    split_path[0] + '_out' + split_path[1]))

        self.doc2 = Document()  # Document to compare for equality
        self.doc2.read(os.path.join(self.temp_out_dir,
                                    split_path[0] + '_out' + split_path[1]))
        # Expected to fail
        self.assertRaises(AssertionError,
                          lambda: self.assertEqual(self.doc.compare(self.doc2), 1))


class SimpleTest(unittest.TestCase):
    def test_read(self):
        test_file = str(TEST_FILES_SBOL2[0])
        split_path = os.path.splitext(test_file)
        self.doc = Document()   # Document for read and write
        self.doc.read(os.path.join(TEST_LOC_SBOL2, split_path[0] + split_path[1]))


def runTests(test_list):
    if test_list is None or test_list == []:
        return
    suite_list = []
    loader = unittest.TestLoader()
    for test_class in test_list:
        suite = loader.loadTestsFromTestCase(test_class)
        suite_list.append(suite)

    full_test_suite = unittest.TestSuite(suite_list)

    unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(full_test_suite)


def runRoundTripTests():
    runTests([TestRoundTripSBOL2, TestRoundTripFailSBOL2])


if __name__ == '__main__':
    runRoundTripTests()
