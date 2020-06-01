import unittest

import sbol2


class TestComponent(unittest.TestCase):

    def test_role(self):
        c = sbol2.Component('c1')
        self.assertTrue(hasattr(c, 'identity'))
        self.assertEqual(None, c.roleIntegration)
        self.assertEqual([], c.roles)
        c.roles = [sbol2.SO_PROMOTER]
        # The SBOL 2.3.0 spec says that if a component has roles then
        # it MUST have a roleIntegration. There is a validator that should
        # set roleIntegration if not set
        self.assertNotEqual(None, c.roleIntegration)
        self.assertEqual(sbol2.SBOL_ROLE_INTEGRATION_MERGE,
                         c.roleIntegration)
        c.roleIntegration = sbol2.SBOL_ROLE_INTEGRATION_OVERRIDE
        c.roles = []
        # It is ok to have a roleIntegration even if there are no roles
        self.assertEqual(sbol2.SBOL_ROLE_INTEGRATION_OVERRIDE,
                         c.roleIntegration)

    def test_add_remove_role(self):
        c = sbol2.Component('c1')
        self.assertEqual([], c.roles)
        c.addRole(sbol2.SO_PROMOTER)
        self.assertEqual([sbol2.SO_PROMOTER], c.roles)
        c.addRole(sbol2.SO_MISC)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC], c.roles)
        c.addRole(sbol2.SO_CDS)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC, sbol2.SO_CDS], c.roles)
        c.removeRole(1)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_CDS], c.roles)


if __name__ == '__main__':
    unittest.main()
