from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.memoize import instance

from uwosh.timeslot import timeslotMessageFactory as _

from uwosh.timeslot.content.person import ExposedPersonSchema

class IChooseTimeSlot(Interface):
    pass


class ChooseTimeSlot(BrowserView):
    implements(IChooseTimeSlot)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self, *args, **kwargs):
        print "called"
        if self.request.form.get('form.submitted') == '1' and \
           self.request.form.get('form.button.submit') == 'Submit':

           for field in ExposedPersonSchema.fields():
               field_validation = field.validate(self.request.form.get(field.getName()), self.context)
               if field_validation: self.errors[field.getName()] = field_validation


           #Special case for personal email address
           if "confirmPersonalEmail" not in self.errors and self.request.form.get('personalEmail') != self.request.form.get('confirmPersonalEmail'):
               self.errors['confirmPersonalEmail'] = "Confirmation email address does not match.  Please check your input."

           #Special checks for our slotSelection; it's not a real field
           timeSlotUid = self.request.form.get('slotSelection')
           timeSlotUid = isinstance(timeSlotUid, basestring) and [timeSlotUid,] or timeSlotUid
           timeSlot = None
           if not timeSlotUid or len(timeSlotUid) != 1:
               self.errors['slotSelection'] = "Please select one enrolment session to book into."
           else:           
               ref_catalog = getToolByName(self.context, 'reference_catalog')
               timeSlot = ref_catalog.lookupObject(timeSlotUid[0])

               #XXX Need one more check here to make sure the student
               #can sign up for the given slot...
               if not timeSlot or timeSlot.getPortalTypeName() != 'Time Slot':
                   self.errors['slotSelection'] = "Your selected session could not be found; it may have been cancelled.  Please select another."

           #If we don't have any errors, we're good.  Otherwise, we just fall through to displaying the form.
           if len(self.errors) == 0:
               self.getSlotAndSignUserUpForIt(slotLabel)

        print self.request.form
        return super(ChooseTimeSlot,self).__call__(args, kwargs)

    @instance.memoize
    def areAnyExtraFieldsRequired(self):
        return len(self.context.getExtraFields()) > 0

    @instance.memoize
    def isFieldRequired(self, field):
    	extraFields = self.context.getExtraFields()
        if field in extraFields:
            return True
        else:
            return False
    
    @instance.memoize
    def isCurrentUserLoggedIn(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return 'Authenticated' in member.getRoles()

    @instance.memoize
    def showEditLinks(self):
        if self.isCurrentUserLoggedIn():
            portal_membership = getToolByName(self, 'portal_membership')
            member = portal_membership.getAuthenticatedMember()
            return member.checkPermission("uwosh.timeslot: Manage Schedule", self.context)
        else:
            return False

    @instance.memoize
    def getExposedFields(self):
        return ExposedPersonSchema.fields()

    def checkTimeSlot(self, timeSlot):
        slotSelection = self.request.form.get('slotSelection')
        return slotSelection == timeSlot.UID() and 'checked' or None


    def getSlotAndSignUserUpForIt(self, timeSlot): 
        '''We should create our Person object now, and drop in all our 
           form submission details.  Validation should have sanitised 
           things for us. '''

        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()

        username = member.getUserName()
        fullname = member.getProperty('fullname')
        if fullname == '':
            fullname = self.username
        email = member.getProperty('email')

        numberOfAvailableSpots = timeSlot.getNumberOfAvailableSpots()
        
        if self.context.isCurrentUserSignedUpForAnySlot():
            self.errors['slotSelection'] = 'You are already signed up for an enrolment booking session.  You need to cancel your existing booking before booking another.'
        elif timeSlot.isCurrentUserSignedUpForThisSlot():
            self.errors['slotSelection'] = 'You are already signed up for this session.'

        elif numberOfAvailableSpots > 0:
            person = timeSlot.invokeFactory('Person', username, personProperties)
            #XXX need to send confirmation email here
        else:
            self.errors['slotSelection'] = 'The slot you selected is already full. Please select a different one'

        return 'slotSelection' in self.errors

