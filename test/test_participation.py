import unittest
import sbol2


class TestParticipation(unittest.TestCase):

    def test_add_remove_role(self):
        p = sbol2.Participation('p')
        self.assertEqual([], p.roles)
        p.addRole(sbol2.SO_PROMOTER)
        self.assertEqual([sbol2.SO_PROMOTER], p.roles)
        p.addRole(sbol2.SO_MISC)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC], p.roles)
        p.addRole(sbol2.SO_CDS)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC, sbol2.SO_CDS], p.roles)
        p.removeRole(1)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_CDS], p.roles)


if __name__ == '__main__':
    unittest.main()
