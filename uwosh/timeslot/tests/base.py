from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from AccessControl import Unauthorized
from mechanize._mechanize import LinkNotFoundError

from smtplib import SMTPRecipientsRefused
from Products.validation import validation

import uwosh.timeslot

@onsetup
def setup_uwosh_timeslot():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', uwosh.timeslot)
    fiveconfigure.debug_mode = False
    
    ztc.installPackage('uwosh.timeslot')
    
setup_uwosh_timeslot()
ptc.setupPloneSite(products=['uwosh.timeslot'])

class MockMailHost(object):
    """A mock mail host to avoid actually sending emails when testing."""

    def getId(self):
        return 'MailHost'

    def send(self, message, mto=None, mfrom=None, subject=None, encode=None):
        isEmail = validation.validatorFor('isEmail')
        if (isEmail(mto) == 1):
            return
        else:    
            raise SMTPRecipientsRefused
        
    def secureSend(self, message, mto=None, mfrom=None, subject=None, encode=None):
        isEmail = validation.validatorFor('isEmail')
        if (isEmail(mto) == 1):
            return
        else:    
            raise SMTPRecipientsRefused
        

class TestCase(ptc.PloneTestCase):
    """A base class for all the tests in this package."""
    
    def _setup(self):
        ptc.PloneTestCase._setup(self)
        self.portal.MailHost = MockMailHost()
    
    def becomeManager(self):
        self.setRoles(['Authenticated', 'Member', 'Manager'])

    def createSignupSheet(self, folder, id='test-sheet'):
        folder.invokeFactory('Signup Sheet', id)
        return folder[id]

    def createDay(self, folder, id='test-day'):
        folder.invokeFactory('Day', id)
        return folder[id]

    def createTimeSlot(self, folder, id='test-timeslot'):
        folder.invokeFactory('Time Slot', id)
        return folder[id]

    def createPerson(self, folder, id='test-person'):
        folder.invokeFactory('Person', id)
        return folder[id]


class FunctionalTestCase(TestCase, ptc.FunctionalTestCase):
    pass
