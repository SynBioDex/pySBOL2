import unittest

import sbol


class TestImplementation(unittest.TestCase):

    def test_implementation_exported(self):
        self.assertIn('Implementation', dir(sbol))
