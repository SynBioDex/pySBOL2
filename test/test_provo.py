import datetime
import unittest

import dateutil.parser

import sbol2
from sbol2 import Activity


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


class TestActivity(unittest.TestCase):

    def test_started_at_time(self):
        activity = Activity('activity1')
        self.assertIsNone(activity.startedAtTime)
        # Test setting via datetime.datetime
        my_start = datetime.datetime.now()
        activity.startedAtTime = my_start
        self.assertEqual(my_start, activity.startedAtTime)
        # Test setting via string
        start_string = '2016-03-16T20:12:00Z'
        activity.startedAtTime = start_string
        start_dt = dateutil.parser.parse(start_string)
        self.assertEqual(start_dt, activity.startedAtTime)

    def test_ended_at_time(self):
        activity = Activity('activity2')
        self.assertIsNone(activity.endedAtTime)
        # Test setting via datetime.datetime
        my_end = datetime.datetime.now()
        activity.endedAtTime = my_end
        self.assertEqual(my_end, activity.endedAtTime)
        # Test setting via string
        end_string = '2016-03-16T20:12:00Z'
        activity.endedAtTime = end_string
        end_dt = dateutil.parser.parse(end_string)
        self.assertEqual(end_dt, activity.endedAtTime)
