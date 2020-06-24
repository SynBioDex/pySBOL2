import unittest
import sbol2 as sbol


class TestDesign(unittest.TestCase):

    # This is expected to fail because `design.structure` and
    # `design.function` both return a ReferencedObject instance instead
    # of None. We'll have to deal with that at some point if we want
    # to maintain backward compatibility.
    @unittest.expectedFailure  # See issue #197
    def test_constructor_empty(self):
        # There was a bug where a Design could not be constructed with
        # no arguments. The original pySBOL allows this. This test
        # ensures backward compatibility with the empty constructor
        # call.
        design = sbol.Design()
        self.assertIsNone(design.structure)
        self.assertIsNone(design.function)


if __name__ == '__main__':
    unittest.main()
