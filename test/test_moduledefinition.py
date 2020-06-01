import unittest
import sbol2


class TestModuleDefinition(unittest.TestCase):

    def setUp(self):
        # All tests in this file use the default homespace
        sbol2.setHomespace('http://examples.org')
        # All tests in this file use SBOL compliant URIs
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_COMPLIANT_URIS.value, True)
        sbol2.Config.setOption(sbol2.ConfigOptions.SBOL_TYPED_URIS.value, True)

    # Borrowed from libSBOL/wrapper/unit_tests.py
    def testApplyCallbackRecursively(self):
        # Assemble module hierarchy
        doc = sbol2.Document()
        root = sbol2.ModuleDefinition('root')
        sub = sbol2.ModuleDefinition('sub')
        leaf = sbol2.ModuleDefinition('leaf')
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
        doc = sbol2.Document()
        root = sbol2.ModuleDefinition('root')
        sub = sbol2.ModuleDefinition('sub')
        doc.addModuleDefinition([root, sub])
        root.assemble([sub])

    def testAttachments(self):
        # All TopLevels can have attachments
        # TODO: There's a better test here involving a Document
        attachment = sbol2.Attachment('attachment')
        md = sbol2.ModuleDefinition('md')
        md.attachments = attachment.identity
        self.assertEqual([attachment.identity], md.attachments)

    def test_add_remove_role(self):
        md = sbol2.ModuleDefinition('c1')
        self.assertEqual([], md.roles)
        md.addRole(sbol2.SO_PROMOTER)
        self.assertEqual([sbol2.SO_PROMOTER], md.roles)
        md.addRole(sbol2.SO_MISC)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC], md.roles)
        md.addRole(sbol2.SO_CDS)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC, sbol2.SO_CDS], md.roles)
        md.removeRole(1)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_CDS], md.roles)


if __name__ == '__main__':
    unittest.main()
