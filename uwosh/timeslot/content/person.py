from five import grok
from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import IPerson
from uwosh.timeslot import config

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View

ExposedPersonSchema = atapi.Schema((

    atapi.StringField('home_ph',
        storage=atapi.AnnotationStorage(),
        required=True,
        widget=atapi.StringWidget(label=_(u'Daytime Contact Number'),
                                  description=_(u'Enter your daytime phone number.')),
        validators = ('saneIsPhoneNumber')
    ),

    atapi.StringField('mob_ph',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.StringWidget(label=_(u'Mobile Phone Number'),
                                  description=_(u'Enter your mobile phone number.')),
        validators = ('saneIsPhoneNumber')
    ),

    atapi.StringField('pers_email',
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

    atapi.StringField('stu_id',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Student Number'),),
    ),

    atapi.StringField('login_id',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Student Login ID'),),
    ),

    atapi.StringField('ssp_no',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(label=_(u'SSP Number'),),
    ),

    atapi.StringField('ssp_att_no',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(label=_(u'SSP ATT Number'),),
    ),

    atapi.StringField('crs_cd',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Course Code'),),
    ),

    atapi.StringField('sprd_code',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Study Period Code'),),
    ),

    atapi.IntegerField('crs_year',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(label=_(u'Course Year'),),
    ),

    atapi.StringField('crs_status',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Course Status'),),
    ),

    atapi.StringField('crs_full_nm',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Course Full Name'),),
    ),

    atapi.StringField('crs_nm',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Abbreviated Course Title'),),
    ),

    atapi.StringField('campus',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Default Campus'),),
    ),

    atapi.StringField('surname',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Surname'),),
    ),

    atapi.StringField('gvn_name',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Given Name'),),
    ),


    atapi.StringField('jcu_email',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'E-Mail'),
                                  description=_(u'Your JCU email address')),
        validators = ('isEmail')
    ),

    atapi.StringField('intnl_stu',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'International Student'),),
    ),

    atapi.StringField('sanctions',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Sanctions'),),
    ),

    atapi.StringField('adv_std',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Advanced Standing Approved?'),),
    ),

    atapi.IntegerField('no_subjects_enr',
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

    stu_id = atapi.ATFieldProperty('stu_id')
    login_id = atapi.ATFieldProperty('login_id')
    ssp_no = atapi.ATFieldProperty('ssp_no')
    ssp_att_no = atapi.ATFieldProperty('ssp_att_no')
    crs_cd = atapi.ATFieldProperty('crs_cd')
    sprd_code = atapi.ATFieldProperty('sprd_code')
    crs_year = atapi.ATFieldProperty('crs_year')
    crs_status = atapi.ATFieldProperty('crs_status')
    crs_full_nm = atapi.ATFieldProperty('crs_full_nm')
    crs_nm = atapi.ATFieldProperty('crs_nm')
    campus = atapi.ATFieldProperty('campus')
    surname = atapi.ATFieldProperty('surname')
    gvn_name = atapi.ATFieldProperty('gvn_name')
    home_ph = atapi.ATFieldProperty('home_ph')
    mob_ph = atapi.ATFieldProperty('mob_ph')
    jcu_email = atapi.ATFieldProperty('jcu_email')
    pers_email = atapi.ATFieldProperty('pers_email')
    confirmPersonalEmail = atapi.ATFieldProperty('confirmPersonalEmail')
    subjectInfo = atapi.ATFieldProperty('subjectInfo')
    difficultyWithEStudent = atapi.ATFieldProperty('difficultyWithEStudent')
    intendToApplyForAdvancedStanding = atapi.ATFieldProperty('intendToApplyForAdvancedStanding')
    submittedApplicationForAdvancedStanding = atapi.ATFieldProperty('submittedApplicationForAdvancedStanding')
    intnl_stu = atapi.ATFieldProperty('intnl_stu')
    sanctions = atapi.ATFieldProperty('sanctions')
    adv_std = atapi.ATFieldProperty('adv_std')
    no_subjects_enr = atapi.ATFieldProperty('no_subjects_enr')

    def __init__(self, oid, **kwargs):
        for field in OurPersonSchema.keys():
            setattr(self, field, kwargs.get(field))

        super(Person, self).__init__(oid, **kwargs)

    def Title(self):
        if self.gvn_name is None or self.surname is None:
            return self.id
        else:
            return self.gvn_name + ' ' + self.surname

    def getReviewState(self):
        portal_workflow = getToolByName(self, 'portal_workflow')
        return portal_workflow.getInfoFor(self, 'review_state')

    def getReviewStateTitle(self):
        reviewState = self.getReviewState()
        return self.portal_workflow.getTitleForStateOnType(reviewState, 'Person')

atapi.registerType(Person, config.PROJECTNAME)
