from AccessControl import Unauthorized
from Acquisition import aq_inner

from zope.component import getMultiAdapter
from zope.interface import implements, Interface
from plone.memoize import instance
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot import config, mail
from uwosh.timeslot.browser.base import BaseBrowserView
from uwosh.timeslot.content.person import ExposedPersonSchema, DummyExposedPersonSchema
from uwosh.timeslot import util

class IChooseTimeSlot(Interface):
    pass


class ChooseTimeSlot(BaseBrowserView):
    implements(IChooseTimeSlot)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self, *args, **kwargs):
        #Recall our user's course selection from their session.
        plone_utils = getToolByName(self.context, 'plone_utils')
        self.student_details = self.getStudentDetailsFromSdm()
        self.booked_session_uid = None

        member = self.getAuthenticatedMember()

        #If a user hasn't selected a course yet, then get them to.
        #Administrators are special -- they don't get bumped.
        if self.student_details is None and not self.showEditLinks() and not self.isBookingStaff():
            self.context.request.response.redirect(self.context.absolute_url()+'/@@select-course')
            return

        #When submitting our form, do the following for validation/processing
        if self.request.form.get('form.submitted') == '1' and \
           self.request.form.get('form.button.Submit') == 'Submit Form':

           self.authenticateForm()

           #Validate our fields from the page
           for field in ExposedPersonSchema.fields():
               field_validation = field.validate(self.request.form.get(field.getName()), self.context)
               if field_validation: self.errors[field.getName()] = field_validation

           #Special case for personal email address
           if "confirmPersonalEmail" not in self.errors and self.request.form.get('personalEmail') != self.request.form.get('confirmPersonalEmail'):
               self.errors['confirmPersonalEmail'] = "Confirmation email address does not match.  Please check your input."
           #Special case for advanced standing
           if self.request.form.get('intendToApplyForAdvancedStanding') is '1' and self.request.form.get('submittedApplicationForAdvancedStanding') is None:
               self.errors['submittedApplicationForAdvancedStanding'] = "This field is required."

           #Special checks for our slotSelection; it's not a real field
           timeSlotUid = self.request.form.get('slotSelection')
           timeSlotUid = isinstance(timeSlotUid, basestring) and [timeSlotUid,] or timeSlotUid
           timeSlot = None
           if not timeSlotUid or len(timeSlotUid) != 1:
               self.errors['slotSelection'] = "Please select one enrolment session to book into."
           else:           
               timeSlot = self.getBookingSessionByUid(timeSlotUid[0])
               existing = timeSlot.get(self.student_details['studentLoginId'])
               #XXX Need more checks here to make sure the student
               #can sign up for the given slot...
               if not timeSlot \
                  or timeSlot.isFull() \
                  or timeSlot.isInThePast() \
                  or timeSlot.getFaculty() != self.student_details['facultyCode'] \
                  or self.context.isUserSignedUpForAnySlot(self.student_details):
                   self.errors['slotSelection'] = "Your could not be signed up for your selected session.  It may have been cancelled or become full.  Please select a different session."
               elif existing:
                   self.errors['slotSelection'] = "You are already attending this enrolment session for %s.  Please choose another session." % existing.getCourseFullName()

           #If we don't have any errors, we're good.  Otherwise, we just fall through to displaying the form.
           if len(self.errors) == 0:
               try:
                   #need to add/merge request details with student details here
                   #They might have changed phone/email/etc and we need their
                   #responses included.
                   self.student_details.update(self.request.form)
                   person = timeSlot.invokeFactory('Person', self.student_details['studentLoginId'], **self.student_details)

                   try: 
                       #EMAIL: Send confirmation email to our user
                       mail.sendNotificationEmail(context=self.context,
                                      person=timeSlot[person],
                                      email_type=config.EHS_CONFIRMATION_EMAIL)
                       plone_utils.addPortalMessage(_(u'Your booking was processed successfully. Your selected session is highlighted below.'), 'success')
                   except:
                       raise
                       plone_utils.addPortalMessage(_(u'Your booking was processed successfully but a confirmation email could not be sent.'), 'warning')
 
                   self.booked_session_uid = timeSlot.UID()
               except:
                   raise
                   self.errors['slotSelection'] = "Your could not be signed up for your selected session.  The session may have been cancelled or become full.  Please select a different session."
               

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
          
        #Data reconfiguration before our page loads 
        if self.student_details is not None:
            self.faculty_code = self.student_details['facultyCode'] 
            self.faculty_name = config.FACULTY_LIST.getValue(self.faculty_code)
        else:
            self.faculty_code = ''
            self.faculty_name = "Administrative overview (all sessions)"

        #Inject our friendly error message if there's errors on the page
        if self.errors:
            plone_utils.addPortalMessage(_(u'Please correct the indicated errors before attempting to book a session.'), 'error')

        #print self.request.form
        return super(ChooseTimeSlot,self).__call__(args, kwargs)

    def selectCourse(self):
        '''Processing that happens when a user loads the select a course
           page.  It's similar to our normal booking page, but it gives
           the user the choice of their course rather than a session'''
        session = self.getSdmSession()
        self.courses = self.queryStudentDetails(self.getAuthenticatedMember().getId(), as_dict=True, search_student_id=False, search_login_id=True)
        self.has_selection = False

        selectCourse = self.request.form.get('selectCourse')
        if self.request.form.get('form.submitted') == '1' and \
           self.request.form.get('form.button.Submit') == 'Select' and \
           selectCourse is not None:

           self.authenticateForm()

           course_identifier = util.explodeCourseIdentifier(selectCourse)
           course_identifier_values = course_identifier.values()
           marker_value = True
           valid_courses = [len([i for i in course_identifier_values if i not in result.values()]) or marker_value
                            for result in self.courses]

           if marker_value in valid_courses:
               #We're now sure the user is doing this course, then we can
               #save it now.  They might have been trying to haxx0r by
               #changing the input values.
               session.set(config.EHS_BOOKING_COURSE_IDENTIFIER, self.courses[valid_courses.index(marker_value)])

               self.request.response.redirect(self.context.absolute_url())
               return

           else:
              self.errors['selectCourse'] = "The course you selected could not be found.  Please select a valid course."

        self.courseCount = len(self.courses)

        #If we're just loading the page, we should pre-select any existing
        #course selection the user has made.  Check our SDM session for one.
        if not selectCourse:
            selection = session.has_key(config.EHS_BOOKING_COURSE_IDENTIFIER) and session.get(config.EHS_BOOKING_COURSE_IDENTIFIER)
            if selection:
                self.request.form.setdefault('selectCourse', self.buildCourseIdentifier(selection) )
                self.has_selection = True 

        view = ViewPageTemplateFile("selectcourse.pt")
        return view.__of__(self)()

    def cancelBooking(self):
        '''Processing that happens when a user is cancelling a given
           booking for a session.'''
        if self.request.form.get('form.submitted') == '1' and \
           self.request.form.get('form.button.Submit') == \
           'Cancel selected session':

            self.authenticateForm()

            selectedSlots = self.request.get('selectedSlot', None)
            if type(selectedSlots) != list:
                selectedSlots = [selectedSlots]

            if selectedSlots != [None]:
                plone_utils = getToolByName(self.context, 'plone_utils')
                student_details = self.getStudentDetailsFromSdm()
                for slot in selectedSlots:
                    try:
                        booking_session = self.getBookingSessionByUid(slot)
                        login_id = student_details['studentLoginId']
                        person = booking_session[login_id]
                        booking_session.manage_delObjects([login_id,])
  
                        try:
                            #EMAIL: Send cancellation message to our user
                            mail.sendNotificationEmail(context=self.context,
                                      person=person,
                                      email_type=config.EHS_CANCELLATION_EMAIL)
                            plone_utils.addPortalMessage(_(u'Your selected booking was cancelled successfully.  You have been sent a confirmation email.'), 'info')
                        except:
                            raise
                            plone_utils.addPortalMessage(_(u'Your selected booking was cancelled successfully but a confirmation email could not be sent.'), 'warning')
                            
                        self.has_cancelled = True
                    except:
                        raise
                        plone_utils.addPortalMessage(_(u'Your booking could not be cancelled.  Please contact Enrolment Help.'), 'error')


        view = ViewPageTemplateFile("show-bookings.pt")
        return view.__of__(self)()


    #Helper methods for our views
    def getSessionsCurrentUserIsSignedUpFor(self):
        sessions = None
        student_details = self.getStudentDetailsFromSdm()
        if student_details:
            sessions = self.context.getSlotsUserIsSignedUpFor(student_details)
        return sessions

    def isCurrentUserSignedUpForSlot(self, session):
        result = False
        student_details = self.getStudentDetailsFromSdm()
        if student_details:
            person = session.get(student_details['studentLoginId'])
            if person:
                result = False not in [person[field] == student_details[field] \
                                for field in config.EHS_UNIQUE_FIELD_COMBO]

        return result

    def buildCourseIdentifier(self, selection, delimiter='-'):
        return util.buildCourseIdentifier(selection, delimiter)

    def getSdmSession(self):
       '''Get the Session Data Manager's session for our current user'''
       sdm = getToolByName(self.context,'session_data_manager')
       return sdm.getSessionData(create=True)

    def getStudentDetailsFromSdm(self):
       return self.getSdmSession().get(config.EHS_BOOKING_COURSE_IDENTIFIER)

    @instance.memoize
    def getBookingSessionByUid(self, uid):
        object = self.getObjectByUid(uid)
        return (object is not None and \
                object.getPortalTypeName() == 'Time Slot') and object or None
 
    @instance.memoize
    def getObjectByUid(self, uid):
       return getToolByName(self.context, 'reference_catalog').lookupObject(uid)
 
    @instance.memoize
    def getBookedSession(self):
       if hasattr(self, 'booked_session_uid') == False or self.booked_session_uid is None:
           booking_session_uid = self.request.form.get('session')
           if not booking_session_uid:
               return None
           else:
               self.booked_session_uid = booking_session_uid

       return self.getBookingSessionByUid(self.booked_session_uid)

    @instance.memoize
    def getBookedSessionChecked(self):
        '''Okay, we need to check whether the given user is actually signed
           up for the given session.  They could be: hacking, silly, or
           have tried to click the link after already cancelling.'''
        student_details = self.getStudentDetailsFromSdm()
        booked_session = self.getBookedSession()
        if not booked_session or \
           student_details['studentLoginId'] not in booked_session:
            booked_session = None
        return booked_session

    @instance.memoize
    def showEditLinks(self):
        '''Check permissions to see the administrative management links'''
        member = self.getAuthenticatedMember()
        if member and 'Authenticated' in member.getRoles():
            return member.checkPermission("jcu.booking: Manage bookings", self.context)
        else:
            return False

    @instance.memoize
    def showInputFields(self):
        '''Check to see whether we should be showing the form's input 
           fields to the given user.  If the user is a normal student,
           and not a booking staff member (or signed up for any slot),
           then they should see the fields'''
        member = self.getAuthenticatedMember()
        student_details = self.getStudentDetailsFromSdm()
        if self.isBookingStaff() or \
           (student_details is not None and \
            self.context.isUserSignedUpForAnySlot(student_details)):
            return False
        else:
            return True

    @instance.memoize
    def isBookingStaff(self):
        member = self.getAuthenticatedMember()
        if member and 'Authenticated' in member.getRoles():
            return member.checkPermission("jcu.booking: Book another user in", self.context)
        else:
            return False

    @instance.memoize
    def getExposedFields(self):
        '''Return the fields that should be publicly exposed to the user'''
        return DummyExposedPersonSchema.fields()

    def checkTimeSlot(self, timeSlot):
        '''Check to see if the incoming slot should be pre-selected'''
        slotSelection = self.request.form.get('slotSelection')
        return slotSelection == timeSlot.UID() and 'checked' or None

