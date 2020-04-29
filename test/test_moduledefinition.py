import logging
import unittest
import sbol2 as sbol


class TestModuleDefinition(unittest.TestCase):

    def setUp(self):
        # All tests in this file use the default homespace
        sbol.setHomespace('http://examples.org')
        # All tests in this file use SBOL compliant URIs
        sbol.Config.setOption(sbol.ConfigOptions.SBOL_COMPLIANT_URIS.value, True)
        sbol.Config.setOption(sbol.ConfigOptions.SBOL_TYPED_URIS.value, True)

    # Borrowed from libSBOL/wrapper/unit_tests.py
    def testApplyCallbackRecursively(self):
        # Assemble module hierarchy
        doc = sbol.Document()
        root = sbol.ModuleDefinition('root')
        sub = sbol.ModuleDefinition('sub')
        leaf = sbol.ModuleDefinition('leaf')
        doc.addModuleDefinition([root, sub, leaf])
        root.assemble([sub])
        sub.assemble([leaf])

        # Define callback which performs an operation on the given ModuleDefinition
        def callback(md, params):
            level = params[0]
            level += 1
            params[0] = level

        # Apply callback
        level = 0
        params = [level]
        flattened_module_tree = root.applyToModuleHierarchy(callback, params)
        level = params[0]
        flattened_module_tree = [md.identity for md in flattened_module_tree]
        expected_module_tree = [md.identity for md in [root, sub, leaf]]
        self.assertSequenceEqual(flattened_module_tree, expected_module_tree)
        self.assertEqual(level, 3)

    def testAssemble(self):
        # Assemble module hierarchy
        doc = sbol.Document()
        root = sbol.ModuleDefinition('root')
        sub = sbol.ModuleDefinition('sub')
        doc.addModuleDefinition([root, sub])
        root.assemble([sub])


if __name__ == '__main__':
    unittest.main()
