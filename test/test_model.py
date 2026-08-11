"""Unit tests for Model."""

import unittest

import sbol2


class TestModel(unittest.TestCase):
    """Unit tests for Model."""

    def test_model_exported(self):
        """Test that the Model class is exported from sbol2."""
        # https://github.com/SynBioDex/pySBOL2/issues/448
        self.assertIn("Model", dir(sbol2), "Model is not exported from sbol2.")


if __name__ == "__main__":
    unittest.main()
