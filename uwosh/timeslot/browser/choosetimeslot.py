from zope.interface import implements, Interface

from uwosh.timeslot.browser.base import BaseBrowserView
from Products.CMFCore.utils import getToolByName
from plone.memoize import instance

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot import config
from uwosh.timeslot.util import explodeCourseIdentifier
from uwosh.timeslot.content.person import ExposedPersonSchema

class IChooseTimeSlot(Interface):
    pass


class ChooseTimeSlot(BaseBrowserView):
    implements(IChooseTimeSlot)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}


    def selectCourse(self):
        self.courses = self.queryStudentDetails(self.getAuthenticatedMember().getId(), as_dict=True)

        selectCourse = self.request.form.get('selectCourse')
        if self.request.form.get('form.submitted') == '1' and \
           self.request.form.get('form.button.submit') == 'Next' and \
           selectCourse is not None:

           course_identifier = explodeCourseIdentifier(selectCourse)
           course_identifier_values = course_identifier.values()
           marker_value = True
           valid_courses = [len([i for i in course_identifier_values if i not in result.values()]) or marker_value
                            for result in self.courses]

           if marker_value in valid_courses:
               #We're now sure the user is doing this course, then we can
               #save it now.  They might have been trying to haxx0r by
               #changing the input values.
               session = self.getSdmSession()
               session.set(config.EHS_BOOKING_COURSE_IDENTIFIER, self.courses[valid_courses.index(marker_value)])

               self.request.response.redirect(self.context.absolute_url())
               return

           else:
              self.errors['selectCourse'] = "The course you selected could not be found.  Please select a valid course."


        self.courseCount = len(self.courses)
        view = ViewPageTemplateFile("selectcourse.pt")
        return view.__of__(self)()

    def bookUser(self):
        return "book user"

    def submitForm(self):
        self.errors['personalEmail'] = "EEEEEEEEKKK!"
        self.context.request.response.redirect(self.context.absolute_url() + '/@@choose-timeslot-view')


    def __call__(self, *args, **kwargs):
        #Recall our user's course selection from their session.
        #We should clear their session details when they log out.
        session = self.getSdmSession()
        self.student_details = session.get(config.EHS_BOOKING_COURSE_IDENTIFIER)

        member = self.getAuthenticatedMember()

        #If a user hasn't selected a course yet, then get them to.
        #Administrators are special -- they don't get bumped.
        if self.student_details is None and not self.showEditLinks():
            self.context.request.response.redirect(self.context.absolute_url()+'/@@select-course')
            return

        #When submitting our form, do the following for validation/processing
        if self.request.form.get('form.submitted') == '1' and \
           self.request.form.get('form.button.submit') == 'Submit':

           #Validate our fields from the page
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
               self.getSlotAndSignUserUpForIt(timeSlotUid)

        #We're just loading the form, not submitting
        else:
            #Copy selected exposed schema attributes into the request.form
            #object to inject them onto the page.
            if self.student_details is not None:
                for field_key in ExposedPersonSchema.keys():
                    if field_key == "confirmPersonalEmail":
                        self.request.form.setdefault(field_key, self.student_details.get('personalEmail'))
                    else:
                        self.request.form.setdefault(field_key, self.student_details.get(field_key))
          
        
        if self.student_details is not None:
            self.faculty_code = self.student_details['faculty_code'] 
            self.faculty_name = config.FACULTY_LIST.getValue(self.faculty_code)
        else:
            self.faculty_code = ''
            self.faculty_name = "Administrative overview (all sessions)"

        #print self.request.form
        return super(ChooseTimeSlot,self).__call__(args, kwargs)

    #Helper methods for our views
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
    
    def getSdmSession(self):
       '''Get the Session Data Manager's session for our current user'''
       sdm = getToolByName(self.context, 'session_data_manager')
       return sdm.getSessionData(create=True)

    @instance.memoize
    def showEditLinks(self):
        '''Check permissions to see the administrative management links'''
        member = self.getAuthenticatedMember()
        if member and 'Authenticated' in member.getRoles():
            return member.checkPermission("uwosh.timeslot: Manage Schedule", self.context)
        else:
            return False

    @instance.memoize
    def showInputFields(self):
        member = self.getAuthenticatedMember()
        if self.isBookingStaff() or self.context.isUserSignedUpForAnySlot(member.getId()):
            return False
        else:
            return True

    @instance.memoize
    def isBookingStaff(self):
        #XXX This needs to be corrected to handle new 
        return self.showEditLinks()

    @instance.memoize
    def getExposedFields(self):
        '''Return the fields that should be publicly exposed to the user'''
        return ExposedPersonSchema.fields()

    def checkTimeSlot(self, timeSlot):
        '''Check to see if the incoming slot should be pre-selected'''
        slotSelection = self.request.form.get('slotSelection')
        return slotSelection == timeSlot.UID() and 'checked' or None

    def getSlotAndSignUserUpForIt(self, timeSlot): 
        '''We should create our Person object now, and drop in all our 
           form submission details.  Validation should have sanitised 
           things for us. '''

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

