import csv
import datetime
from StringIO import StringIO
from DateTime import DateTime

from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.configuration import zconf
from collective.easytemplate.fields import TemplatedTextField

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import ISignupSheet
from uwosh.timeslot import config 
from uwosh.timeslot.content.person import DummyExposedPersonSchema 


SignupSheetSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.BooleanField('allowSignupForMultipleSlots',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(label=_(u'Allow Signup For Multiple Slots'),
                                   description=_(u'Allow the user to signup for more than one slot.'))
    ),

    atapi.StringField('showSlotNames',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(label=_(u'Show Individual Time Slot Names'),
                                   description=_(u'Whether or not to show individual slot names.'))
    ),

    #This field exists for legacy reasons from original product.
    atapi.LinesField('extraFields',
        storage=atapi.AnnotationStorage(),
        vocabulary=[('phone','Phone'), ('department','Department'), ('classification','Employee Classification')],
        widget=atapi.MultiSelectionWidget(label=_(u'Extra Fields'),
                                          description=_(u'Information you want to collect from users besides just name and email.'),
                                          format=_(u'checkbox'))
    ),

    atapi.TextField('contactInfo',
        required=False,
        searchable=False,
        primary=False,
        storage = atapi.AnnotationStorage(),
        validators = ('isTidyHtmlWithCleanup',),
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(label=_(u'Contact information'),
                   description = _(u'Enter additional text to be displayed on the booking form.  This information appears at the top, underneath the title of the booking form.'),
                   rows = 5,
                   allow_file_upload = zconf.ATDocument.allow_document_upload),
    ),

    atapi.LinesField('extraEmailContent',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(label=_(u'Extra Email Content'),
                                 description=_(u'Any additional information that you want included in the notification emails. \
                                                 Note: Contact info., sheet, day, time, and a url are included by default.'))
    ),

    TemplatedTextField('confirmationEmailBody',
        required=True,
        searchable=False,
        primary=False,
        schemata='emails',
        storage = atapi.AnnotationStorage(),
        validators = ('isTidyHtmlWithCleanup',),
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(label=_(u'Confirmation Email (Templated)'),
                   description = _(u'Enter templated text to be sent out to students when they first sign up for an enrolment session.'),
                   rows = 5,
                   allow_file_upload = False),
    ),

    TemplatedTextField('reminderEmailBody',
        required=True,
        searchable=False,
        primary=False,
        schemata='emails',
        storage = atapi.AnnotationStorage(),
        validators = ('isTidyHtmlWithCleanup',),
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(label=_(u'Reminder Email (Templated)'),
                   description = _(u'Enter templated text to be sent out to students two days before their scheduled enrolment session.'),
                   rows = 5,
                   allow_file_upload = False),
    ),

    TemplatedTextField('cancellationEmailBody',
        required=True,
        searchable=False,
        primary=False,
        schemata='emails',
        storage = atapi.AnnotationStorage(),
        validators = ('isTidyHtmlWithCleanup',),
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(label=_(u'Cancellation Email (Templated)'),
                   description = _(u'Enter templated text to be sent out to students if they choose to cancel their scheduled enrolment session.'),
                   rows = 5,
                   allow_file_upload = False),
    ),

))

SignupSheetSchema['title'].storage = atapi.AnnotationStorage()
SignupSheetSchema['description'].storage = atapi.AnnotationStorage()
SignupSheetSchema['description'].widget.visible = {'view':'invisible', 'edit':'invisible'}
SignupSheetSchema['extraFields'].widget.visible = {'view':'invisible', 'edit':'invisible'}
SignupSheetSchema['extraEmailContent'].widget.visible = {'view':'invisible', 'edit':'invisible'}
SignupSheetSchema['confirmationEmailBody'].widget.visible = {'view':'invisible', 'edit':'visible'}
SignupSheetSchema['reminderEmailBody'].widget.visible = {'view':'invisible', 'edit':'visible'}
SignupSheetSchema['cancellationEmailBody'].widget.visible = {'view':'invisible', 'edit':'visible'}

schemata.finalizeATCTSchema(SignupSheetSchema, folderish=True, moveDiscussion=False)

class SignupSheet(folder.ATFolder):
    implements(ISignupSheet)

    portal_type = 'Signup Sheet'
    schema = SignupSheetSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    extraFields = atapi.ATFieldProperty('extraFields')
    contactInfo = atapi.ATFieldProperty('contactInfo')
    confirmationEmailBody = atapi.ATFieldProperty('confirmationEmailBody')
    reminderEmailBody = atapi.ATFieldProperty('reminderEmailBody')
    cancellationEmailBody = atapi.ATFieldProperty('cancellationEmailBody')
    extraEmailContent = atapi.ATFieldProperty('extraEmailContent')
    allowSignupForMultipleSlots = atapi.ATFieldProperty('allowSignupForMultipleSlots')
    showSlotNames = atapi.ATFieldProperty('showSlotNames')

    #KSS validation workaround since we're exposing a separate schema here publically
    def getField(self, key, wrapped=False):
        field = super(SignupSheet, self).getField(key)
        if not field:
            field = DummyExposedPersonSchema.get(key)
            if field:
                field.writeable = lambda context: True
                field.checkPermission = lambda mode, instance: True
        return field

    def getDay(self, date):
        clean_date = '"' + date + '"'
        brains = self.portal_catalog.unrestrictedSearchResults(path=self.getPath(), portal_type='Day', Title=clean_date)
        if len(brains) == 0:
            raise ValueError('The date %s was not found.' % date)
        return brains[0].getObject()
        
    def getDays(self, all=False):
        brains = self.portal_catalog.unrestrictedSearchResults(portal_type='Day', path=self.getPath(),
                                                               depth=1, sort_on='getDate', sort_order='ascending')
        if len(brains) == 0:
            return []
        else:
            today = DateTime().earliestTime()
            indexOfFirstUsefulObject = 0

            while (indexOfFirstUsefulObject < len(brains)) and (brains[indexOfFirstUsefulObject]['getDate'] < today):
                indexOfFirstUsefulObject += 1
            
            if all:
                return [i.getObject() for i in brains]
            else:
                return [brains[i].getObject() for i in range(indexOfFirstUsefulObject, len(brains))]


    def removeAllPeople(self):
        for (id, obj) in self.contentItems():
            obj.removeAllPeople()
        
    def exportToCSV(self, faculty=[], campus=[], startDate=None, endDate=None,
                    sortOrder=[]):
        buffer = StringIO()
        writer = csv.writer(buffer, quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(config.EHS_CSV_EXPORT_FORMAT)

        for day in self.getDays(all=True):
            thisDay = datetime.date.fromtimestamp(day.getRawDate().timeTime())
            #If either dates are None, then our check passes.  Both checks
            #of upper and lower bounds need to pass to check the Day.
            if (startDate is None or thisDay >= startDate) and \
               (endDate is None or thisDay <= endDate):
                for session in day.getTimeSlots(faculty or ''):
                    if campus == [] or session.campus in campus:
                        for person in session.getPeople():
                            writer.writerow(self.buildCSVRow(day, session, person))

        result = buffer.getvalue()
        buffer.close()

        return result

    def buildCSVRow(self, day, session, person):
        row = [session.getFacultyAbbreviation(),
                day.getDate(),
                session.getName(),
                session.getTimeRange(),
                person.getCourseStatus(),
                person.getStudentNumber(),
                person.getCourseCode(),
                person.getAbbrevCourseTitle(),
                person.getDefaultCampus(),
                person.getStudentSurname(),
                person.getStudentGivenName(),
                person.getDaytimeContactNumber(),
                person.getMobilePhoneNumber() or '',
                person.getEmail() or '',
                person.getPersonalEmail() or '',
                person.getSubjectInfo() != '0' and 'Yes' or 'No',
         person.getDifficultyWithEStudent() != '0' and 'Yes' or 'No',
         person.getIntendToApplyForAdvancedStanding() != '0' and 'Yes' or 'No',
         person.getSubmittedApplicationForAdvancedStanding() and 'Yes' \
                                                             or 'No',
                person.getAdvancedStandingApproved() == 'Y' and 'Yes' or 'No',
                person.getIsInternational() == 'Y' and 'Yes' or 'No',
                person.getSanctions(),
                person.getNumberSubjectsEnrolled(),
               ]
        return row
    
    def isCurrentUserSignedUpOrWaitingForAnySlot(self):
        username = self.getCurrentUsername()
        return self.isUserSignedUpOrWaitingForAnySlot(username)

    def isUserSignedUpOrWaitingForAnySlot(self, username):
        return (self.isUserSignedUpForAnySlot(username) or self.isUserWaitingForAnySlot(username))

    def isCurrentUserSignedUpForAnySlot(self):
        username = self.getCurrentUsername()
        return self.isUserSignedUpForAnySlot(username)
    
    def isUserSignedUpForAnySlot(self, student_details):
        return (len(self.getSlotsUserIsSignedUpFor(student_details)) > 0)

    def isCurrentUserWaitingForAnySlot(self):
        username = self.getCurrentUsername()
        return self.isUserWaitingForAnySlot(username)
    
    def isUserWaitingForAnySlot(self, username):
        return (len(self.getSlotsUserIsWaitingFor(username)) > 0)

    def getSlotsCurrentUserIsSignedUpFor(self):
        username = self.getCurrentUsername()
        return self.getSlotsUserIsSignedUpFor(username)

    def getSlotsUserIsSignedUpFor(self, student_details):
        brains = self.portal_catalog.unrestrictedSearchResults(
                                portal_type='Person', 
                                id=student_details['studentLoginId'],
                                review_state='signedup', 
                                path=self.getPath())

        slots = []
        for brain in brains:
            person = brain.getObject()
            if False not in [person[field] == student_details[field] \
                            for field in config.EHS_UNIQUE_FIELD_COMBO]:
                timeSlot = person.aq_parent
                if not timeSlot.isInThePast():
                    slots.append(timeSlot)
                
        return slots

    def getSlotsCurrentUserIsWaitingFor(self):
        username = self.getCurrentUsername()
        return self.getSlotsUserIsWaitingFor(username)

    def getSlotsUserIsWaitingFor(self, username):
        today = DateTime().earliestTime()
        brains = self.portal_catalog.unrestrictedSearchResults(portal_type='Person', id=username, review_state='waiting',
                                                               path=self.getPath())

        slots = []
        for brain in brains:
            person = brain.getObject()
            timeSlot = person.aq_parent
            day = timeSlot.aq_parent
            if day.getDate() >= today:
                slots.append(timeSlot)
                
        return slots

    def getCurrentUsername(self):
        member = self.portal_membership.getAuthenticatedMember()
        username = member.getUserName()
        return username

    # Return a path that is correct even when we are using virutual hosts
    def getPath(self):
        path = self.getPhysicalPath()
        return '/'.join(path)


atapi.registerType(SignupSheet, config.PROJECTNAME)
