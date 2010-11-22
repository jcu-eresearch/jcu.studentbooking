from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import IPerson
from uwosh.timeslot.config import PROJECTNAME

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View

ExposedPersonSchema = atapi.Schema((

    atapi.StringField('daytimeContactNumber',
        storage=atapi.AnnotationStorage(),
        required=True,
        widget=atapi.StringWidget(label=_(u'Daytime Contact Number'),
                                  description=_(u'Enter your daytime phone number.')), 
        validators = ('saneIsPhoneNumber')
    ),

    atapi.StringField('mobilePhoneNumber',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.StringWidget(label=_(u'Mobile Phone Number'),
                                  description=_(u'Enter your mobile phone number.')), 
        validators = ('saneIsPhoneNumber')
    ),

    atapi.StringField('personalEmail',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.StringWidget(label=_(u'Personal E-Mail'),
                                  description=_(u'We will send confirmation and reminder emails to your JCU address, and your personal address if you enter it here.')),
        validators = ('saneIsEmail')
    ),

    atapi.StringField('confirmPersonalEmail',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.StringWidget(label=_(u'Confirm Personal E-Mail'),),
                                  description=_(u'Re-enter your email address to avoid typing errors.'),
        validators = ('saneIsEmail')
    ),

    atapi.StringField('subjectInfo',
        storage=atapi.AnnotationStorage(),
        required=True,
        vocabulary=[('1', 'Yes'), ('0', 'No')],
        enforceVocabulary=True,
        widget=atapi.SelectionWidget(label=_(u'Are you having difficulty choosing your subjects?'),),
    ),

    atapi.StringField('difficultyWithEStudent',
        storage=atapi.AnnotationStorage(),
        required=True,
        vocabulary=[('1', 'Yes'), ('0', 'No')],
        enforceVocabulary=True,
        widget=atapi.SelectionWidget(label=_(u'Are you having difficulty enrolling through eStudent?'),),
    ),

    atapi.StringField('intendToApplyForAdvancedStanding',
        storage=atapi.AnnotationStorage(),
        required=True,
        vocabulary=[('1', 'Yes'), ('0', 'No')],
        enforceVocabulary=True,
        widget=atapi.SelectionWidget(label=_(u'Do you intend to apply for Advanced Standing (credit for previous studies)?'),),
    ),

    atapi.StringField('submittedApplicationForAdvancedStanding',
        storage=atapi.AnnotationStorage(),
        required=False,
        vocabulary=[('1', 'Yes'), ('0', 'No')],
        enforceVocabulary=True,
        widget=atapi.SelectionWidget(label=_(u'Have you submitted your Application for Advanced Standing and supporting documents?'),),
    ),

))

HiddenPersonSchema = atapi.Schema((

    atapi.StringField('studentNumber',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Student Number'),),
    ),

    atapi.StringField('studentLoginId',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Student Login ID'),),
    ),

    atapi.StringField('courseCode',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Course Code'),),
    ),

    atapi.IntegerField('courseYear',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(label=_(u'Course Year'),),
    ),

    atapi.StringField('courseStatus',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Course Status'),),
    ),

    atapi.StringField('courseFullName',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Course Full Name'),),
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

    atapi.StringField('isInternational',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'International Student'),),
    ),

    atapi.StringField('sanctions',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Sanctions'),),
    ),

    atapi.StringField('advancedStandingApproved',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Advanced Standing Approved?'),),
    ),

    atapi.IntegerField('numberSubjectsEnrolled',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(label=_(u'Number of Subjects Enrolled In'),),
    ),



))

DummyExposedPersonSchema = ExposedPersonSchema.copy()
OurPersonSchema = ExposedPersonSchema + HiddenPersonSchema
PersonSchema = schemata.ATContentTypeSchema.copy() + \
               OurPersonSchema

PersonSchema['title'].required = False
PersonSchema['title'].storage = atapi.AnnotationStorage()
PersonSchema['title'].widget.visible = {'view':'invisible', 'edit':'invisible'}
PersonSchema['description'].storage = atapi.AnnotationStorage()
PersonSchema['description'].widget.visible = {'view':'invisible', 'edit':'invisible'}

schemata.finalizeATCTSchema(PersonSchema, moveDiscussion=False)

def addPerson(self, id, **kw):
    o = Person(id, **kw)
    self._setObject(id,o)

class Person(base.ATCTContent):
    implements(IPerson)

    portal_type = 'Person'
    schema = PersonSchema

    title = atapi.ATFieldProperty('title')

    studentNumber = atapi.ATFieldProperty('studentNumber')
    studentLoginId = atapi.ATFieldProperty('studentLoginId') 
    courseCode = atapi.ATFieldProperty('courseCode')
    courseYear = atapi.ATFieldProperty('courseYear')
    courseStatus = atapi.ATFieldProperty('courseStatus')
    courseFullName = atapi.ATFieldProperty('courseFullName')
    abbrevCourseTitle = atapi.ATFieldProperty('abbrevCourseTitle')
    defaultCampus = atapi.ATFieldProperty('defaultCampus')
    studentSurname = atapi.ATFieldProperty('studentSurname')
    studentGivenName = atapi.ATFieldProperty('studentGivenName')
    daytimeContactNumber = atapi.ATFieldProperty('daytimeContactNumber')
    mobilePhoneNumber = atapi.ATFieldProperty('mobilePhoneNumber')
    email = atapi.ATFieldProperty('email')
    personalEmail = atapi.ATFieldProperty('personalEmail')
    confirmPersonalEmail = atapi.ATFieldProperty('confirmPersonalEmail')
    subjectInfo = atapi.ATFieldProperty('subjectInfo')
    difficultyWithEStudent = atapi.ATFieldProperty('difficultyWithEStudent')
    intendToApplyForAdvancedStanding = atapi.ATFieldProperty('intendToApplyForAdvancedStanding')
    submittedApplicationForAdvancedStanding = atapi.ATFieldProperty('submittedApplicationForAdvancedStanding')
    isInternational = atapi.ATFieldProperty('isInternational')
    sanctions = atapi.ATFieldProperty('sanctions')
    advancedStandingApproved = atapi.ATFieldProperty('advancedStandingApproved')
    numberSubjectsEnrolled = atapi.ATFieldProperty('numberSubjectsEnrolled')

    def __init__(self, oid, **kwargs):
        for field in OurPersonSchema.keys():
            setattr(self, field, kwargs.get(field))

        super(Person, self).__init__(oid, **kwargs)

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
    
atapi.registerType(Person, PROJECTNAME)
