import unittest

import rdflib

import sbol2


class TestAttachment(unittest.TestCase):

    def test_exported(self):
        # Ensure Attachment is exported from sbol2
        self.assertIn('Attachment', dir(sbol2))

    def test_type_uri(self):
        # Test that after construction the attachment has the correct URI.
        # This was a problem until the arguments to the constructor were
        # rearranged.
        test_attach = sbol2.Attachment("TEST")
        self.assertEqual(sbol2.SBOL_ATTACHMENT, test_attach.rdf_type)


if __name__ == '__main__':
    unittest.main()
