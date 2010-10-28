import unittest
from Testing import ZopeTestCase as ztc
from Products.CMFCore.utils import getToolByName

from base import TestCase

from DateTime import DateTime


class TestPerson(TestCase):

    def afterSetUp(self):
        self.becomeManager()
        sheet = self.createSignupSheet(self.folder)
        day = self.createDay(sheet)
        timeSlot = self.createTimeSlot(day)
        self.person = self.createPerson(timeSlot)

    def testGetExtraInfo(self):
        self.assertEqual(self.person.getExtraInfo(), '')
        self.person.setPhone('920-251-1234')
        self.assertEqual(self.person.getExtraInfo(), 'Phone: 920-251-1234')
        self.person.setClassification('Staff')
        self.assertEqual(self.person.getExtraInfo(), 'Phone: 920-251-1234, Class: Staff')
        self.person.setDepartment('Comp. Sci.')
        self.assertEqual(self.person.getExtraInfo(), 'Phone: 920-251-1234, Class: Staff, Dept: Comp. Sci.')
        self.person.setPhone('')
        self.assertEqual(self.person.getExtraInfo(), 'Class: Staff, Dept: Comp. Sci.')
        self.person.setDepartment('')
        self.assertEqual(self.person.getExtraInfo(), 'Class: Staff')
        self.person.setClassification('')
        self.person.setDepartment('Chemistry')
        self.assertEqual(self.person.getExtraInfo(), 'Dept: Chemistry')

    def testGetReviewStateTitle(self):
        portal_workflow = getToolByName(self.portal, 'portal_workflow')
        self.assertEqual(self.person.getReviewStateTitle(), 'Waiting List')
        portal_workflow.doActionFor(self.person, 'signup')
        self.assertEqual(self.person.getReviewStateTitle(), 'Signed Up')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPerson))
    return suite
