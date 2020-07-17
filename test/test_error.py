import unittest

import sbol2


class TestError(unittest.TestCase):

    def test_sbol_error_warning(self):
        # There are lots of places where the SBOLError constructor is
        # called with arguments in the wrong order. A warning has been
        # added to note these occurrences until they can be fixed.
        with self.assertWarns(RuntimeWarning):
            sbol2.SBOLError('Item not found',
                            sbol2.SBOLErrorCode.NOT_FOUND_ERROR)

    def test_what(self):
        msg = 'Item not found'
        error = sbol2.SBOLError(sbol2.SBOLErrorCode.NOT_FOUND_ERROR, msg)
        self.assertEqual(error.what(), msg)

    def test_error_code(self):
        msg = 'Item not found'
        code = sbol2.SBOLErrorCode.NOT_FOUND_ERROR
        error = sbol2.SBOLError(code, msg)
        self.assertEqual(error.error_code(), code)
