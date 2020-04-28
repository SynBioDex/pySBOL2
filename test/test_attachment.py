import unittest

import sbol2


class TestAttachment(unittest.TestCase):

    def test_exported(self):
        # Ensure Attachment is exported from sbol2
        self.assertIn('Attachment', dir(sbol2))


if __name__ == '__main__':
    unittest.main()
