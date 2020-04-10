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
