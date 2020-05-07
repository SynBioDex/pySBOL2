import logging
import os
import subprocess
import sys
import unittest
import tempfile
import shutil
import rdflib
import rdflib.compare

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_DIR = os.path.join(os.path.dirname(TEST_DIR), 'examples')
CRISPR_EXAMPLE = os.path.join(EXAMPLE_DIR, 'CRISPR_example.py')
EXPECTED_SBOL = os.path.join(TEST_DIR, 'SBOLTestSuite', 'SBOL2', 'RepressionModel.xml')


class TestCrisprExample(unittest.TestCase):

    def setUp(self):
        # Create temp directory
        self.temp_out_dir = tempfile.mkdtemp()
        self.logger = logging.getLogger('sbol2.test')
        if not self.logger.hasHandlers():
            logging.basicConfig()

    def tearDown(self):
        # Remove directory after the test
        if self.temp_out_dir:
            shutil.rmtree(self.temp_out_dir)
            self.temp_out_dir = None

    def test_crispr_example(self):
        cmd = [sys.executable, CRISPR_EXAMPLE]
        subprocess.check_call(cmd, cwd=self.temp_out_dir)
        out_path = os.path.join(self.temp_out_dir, 'crispr_example.xml')
        self.assertTrue(os.path.exists(out_path))
        # Load the output
        actual_graph = rdflib.Graph()
        actual_graph.load(out_path)
        actual_iso = rdflib.compare.to_isomorphic(actual_graph)
        # Load the expected output
        expected_graph = rdflib.Graph()
        expected_graph.load(EXPECTED_SBOL)
        expected_iso = rdflib.compare.to_isomorphic(expected_graph)
        rdf_diff = rdflib.compare.graph_diff(expected_iso, actual_iso)
        if rdf_diff[1] or rdf_diff[2]:
            self.logger.warning('Detected %d different RDF triples in %s' %
                                (len(rdf_diff[1]) + len(rdf_diff[2]), out_path))
            for stmt in rdf_diff[1]:
                self.logger.warning('Only in expected: %r', stmt)
            for stmt in rdf_diff[2]:
                self.logger.warning('Only in actual: %r', stmt)
            self.fail('Differences in RDF detected')


if __name__ == '__main__':
    unittest.main()
