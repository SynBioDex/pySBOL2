import unittest

import sbol2


class TestProvo(unittest.TestCase):

    def test_activity_agent(self):
        # Verify that the agent attribute is a ReferencedObject
        doc = sbol2.Document()
        agent = doc.agents.create('007')
        activity = doc.activities.create('spying')
        activity.agent = agent
        self.assertEqual(activity.agent, agent.identity)


class TestAssociation(unittest.TestCase):

    def test_add_remove_role(self):
        a = sbol2.Association('a1')
        self.assertEqual([], a.roles)
        a.addRole(sbol2.SO_PROMOTER)
        self.assertEqual([sbol2.SO_PROMOTER], a.roles)
        a.addRole(sbol2.SO_MISC)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC], a.roles)
        a.addRole(sbol2.SO_CDS)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC, sbol2.SO_CDS], a.roles)
        a.removeRole(1)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_CDS], a.roles)


class TestUsage(unittest.TestCase):

    def test_add_remove_role(self):
        usage = sbol2.Usage('a1')
        self.assertEqual([], usage.roles)
        usage.addRole(sbol2.SO_PROMOTER)
        self.assertEqual([sbol2.SO_PROMOTER], usage.roles)
        usage.addRole(sbol2.SO_MISC)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC], usage.roles)
        usage.addRole(sbol2.SO_CDS)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_MISC, sbol2.SO_CDS], usage.roles)
        usage.removeRole(1)
        self.assertEqual([sbol2.SO_PROMOTER, sbol2.SO_CDS], usage.roles)
