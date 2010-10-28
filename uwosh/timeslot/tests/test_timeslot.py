import unittest
from Testing import ZopeTestCase as ztc
from Products.CMFCore.utils import getToolByName

from base import TestCase

from DateTime import DateTime


class TestTimeSlot(TestCase):

    def afterSetUp(self):
        self.becomeManager()
        sheet = self.createSignupSheet(self.folder)
        day = self.createDay(sheet)
        self.timeSlot = self.createTimeSlot(day)

    def testTitle(self):
        self.assertEqual(self.timeSlot.Title(), 'test-timeslot')

        self.timeSlot.setStartTime(DateTime('2:00 PM'))
        self.timeSlot.setEndTime(DateTime('4:00 PM'))
        self.assertEqual(self.timeSlot.Title(), '02:00 PM - 04:00 PM')

        self.timeSlot.setName('Army Training')
        self.assertEqual(self.timeSlot.Title(), 'Army Training: 02:00 PM - 04:00 PM')

    def testGetTimeRange(self):
        self.assertEqual(self.timeSlot.getTimeRange(), '')
        
        self.timeSlot.setStartTime(DateTime('2:00 PM'))
        self.timeSlot.setEndTime(DateTime('4:00 PM'))
        self.assertEqual(self.timeSlot.Title(), '02:00 PM - 04:00 PM')
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTimeSlot))
    return suite
