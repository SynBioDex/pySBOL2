import unittest
import sbol2


class TestSequenceAnnotation(unittest.TestCase):

    def test_add_remove_role(self):
        sa = sbol2.SequenceAnnotation()
        self.assertEqual([], sa.roles)
        sa.addRole(sbol2.SO_PROMOTER)
        self.assertEqual([sbol2.SO_PROMOTER], sa.roles)
        sa.addRole(sbol2.SO_MISC)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC], sa.roles)
        sa.addRole(sbol2.SO_CDS)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC, sbol2.SO_CDS], sa.roles)
        sa.removeRole(1)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_CDS], sa.roles)

    def test_component(self):
        cd = sbol2.ComponentDefinition('cd')
        sa = cd.sequenceAnnotations.create('sa')
        c = cd.components.create('c')
        sa.component = c
        self.assertEqual(sa.component, c.identity)


if __name__ == '__main__':
    unittest.main()
