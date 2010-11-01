from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import IPerson
from uwosh.timeslot.config import PROJECTNAME

from Products.CMFCore.utils import getToolByName

ExposedPersonSchema = atapi.Schema((

    atapi.StringField('daytimeContactNumber',
        storage=atapi.AnnotationStorage(),
        required=True,
        widget=atapi.StringWidget(label=_(u'Daytime Contact Number'),
                                  description=_(u'Enter your daytime contact number we can reach you on.')), 
        validators = ('saneIsPhoneNumber')
    ),

    atapi.StringField('mobilePhoneNumber',
        storage=atapi.AnnotationStorage(),
        required=True,
        widget=atapi.StringWidget(label=_(u'Mobile Phone Number'),
                                  description=_(u'Enter your mobile phone number.')), 
        validators = ('saneIsPhoneNumber')
    ),

    atapi.StringField('personalEmail',
        storage=atapi.AnnotationStorage(),
        required=True,
        widget=atapi.StringWidget(label=_(u'Personal E-Mail'),
                                  description=_(u'Your personal email address.  We will send you notifications to both your personal and JCU email addresses.')),
        validators = ('saneIsEmail')
    ),

    atapi.StringField('confirmPersonalEmail',
        storage=atapi.AnnotationStorage(),
        required=True,
        widget=atapi.StringWidget(label=_(u'Confirm Personal E-Mail'),),
                                  description=_(u'Re-enter your email address to avoid typing errors.'),
        validators = ('saneIsEmail')
    ),

    atapi.StringField('chosenAllSubjects',
        storage=atapi.AnnotationStorage(),
        required=True,
        vocabulary=[('1', 'Yes'), ('0', 'No')],
        enforceVocabulary=True,
        widget=atapi.SelectionWidget(label=_(u'Have you chosen all the subjects you want to study this year yet?'),),
    ),

    atapi.BooleanField('difficultyWithEStudent',
        storage=atapi.AnnotationStorage(),
        required=True,
        vocabulary=[('1', 'Yes'), ('0', 'No')],
        enforceVocabulary=True,
        widget=atapi.SelectionWidget(label=_(u'Have you had difficulty trying to enrol through eStudent?'),),
    ),

    atapi.BooleanField('intendToApplyForAdvancedStanding',
        storage=atapi.AnnotationStorage(),
        required=True,
        vocabulary=[('1', 'Yes'), ('0', 'No')],
        enforceVocabulary=True,
        widget=atapi.SelectionWidget(label=_(u'Do you intend to apply for Advanced Standing (credit for previous studies)?'),),
    ),

    atapi.BooleanField('submittedApplicationForAdvancedStanding',
        storage=atapi.AnnotationStorage(),
        required=True,
        vocabulary=[('1', 'Yes'), ('0', 'No')],
        enforceVocabulary=True,
        widget=atapi.SelectionWidget(label=_(u'Have you submitted your Application for Advanced Standing and supporting documents?'),),
    ),

))

PersonSchema = schemata.ATContentTypeSchema.copy() + \
               ExposedPersonSchema + atapi.Schema((

    atapi.StringField('studentNumber',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Student Number'),),
    ),

    atapi.StringField('courseCode',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Course Code'),),
    ),

    atapi.StringField('abbrevCourseTitle',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Abbreviated Course Title'),),
    ),

    atapi.StringField('defaultCampus',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Default Campus'),),
    ),

    atapi.StringField('studentSurname',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Surname'),),
    ),

    atapi.StringField('studentGivenName',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Given Name'),),
    ),


    atapi.StringField('email',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'E-Mail'),
                                  description=_(u'Your JCU email address')),
        validators = ('isEmail')
    ),



))

PersonSchema['title'].required = False
PersonSchema['title'].storage = atapi.AnnotationStorage()
PersonSchema['title'].widget.visible = {'view':'invisible', 'edit':'invisible'}
PersonSchema['description'].storage = atapi.AnnotationStorage()
PersonSchema['description'].widget.visible = {'view':'invisible', 'edit':'invisible'}

schemata.finalizeATCTSchema(PersonSchema, moveDiscussion=False)

class Person(base.ATCTContent):
    implements(IPerson)

    portal_type = 'Person'
    schema = PersonSchema

    title = atapi.ATFieldProperty('title')

    studentNumber = atapi.ATFieldProperty('studentNumber')
    courseCode = atapi.ATFieldProperty('courseCode')
    abbrevCourseTitle = atapi.ATFieldProperty('abbrevCourseTitle')
    defaultCampus = atapi.ATFieldProperty('defaultCampus')
    studentSurname = atapi.ATFieldProperty('studentSurname')
    studentGivenName = atapi.ATFieldProperty('studentGivenName')
    daytimeContactNumber = atapi.ATFieldProperty('daytimeContactNumber')
    mobilePhoneNumber = atapi.ATFieldProperty('mobilePhoneNumber')
    email = atapi.ATFieldProperty('email')
    personalEmail = atapi.ATFieldProperty('personalEmail')
    confirmPersonalEmail = atapi.ATFieldProperty('confirmPersonalEmail')
    chosenAllSubjects = atapi.ATFieldProperty('chosenAllSubjects')
    difficultyWithEStudent = atapi.ATFieldProperty('difficultyWithEStudent')
    intendToApplyForAdvancedStanding = atapi.ATFieldProperty('intendToApplyForAdvancedStanding')
    submittedApplicationForAdvancedStanding = atapi.ATFieldProperty('submittedApplicationForAdvancedStanding')

    def Title(self):
        if self.studentGivenName is None or self.studentSurname is None:
            return self.id
        else:
            return self.studentGivenName + ' ' + self.studentSurname
    
    def getReviewState(self):
        portal_workflow = getToolByName(self, 'portal_workflow')
        return portal_workflow.getInfoFor(self, 'review_state')
    
    def getReviewStateTitle(self):
    	reviewState = self.getReviewState()
    	return self.portal_workflow.getTitleForStateOnType(reviewState, 'Person')
    
    def getExtraInfo(self):
        extraInfo = []
        if self.phone != '':
            extraInfo.append('Phone: ' + self.phone)
        if self.classification != '':
            extraInfo.append('Class: ' + self.classification)
        if self.department != '':
            extraInfo.append('Dept: ' + self.department)
        return ', '.join(extraInfo)
    
atapi.registerType(Person, PROJECTNAME)
