import unittest

import sbol


class TestError(unittest.TestCase):

    def test_sbol_error_warning(self):
        # There are lots of places where the SBOLError constructor is
        # called with arguments in the wrong order. A warning has been
        # added to note these occurrences until they can be fixed.
        with self.assertWarns(RuntimeWarning):
            sbol.SBOLError(sbol.SBOLErrorCode.NOT_FOUND_ERROR,
                           'Item not found')

    def test_what(self):
        msg = 'Item not found'
        error = sbol.SBOLError(msg, sbol.SBOLErrorCode.NOT_FOUND_ERROR)
        self.assertEqual(error.what(), msg)

    def test_error_code(self):
        msg = 'Item not found'
        code = sbol.SBOLErrorCode.NOT_FOUND_ERROR
        error = sbol.SBOLError(msg, code)
        self.assertEqual(error.error_code(), code)
