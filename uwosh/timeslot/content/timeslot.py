from zope.interface import implements

from Products.ATContentTypes.configuration import zconf
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import ITimeSlot, ICloneable
from uwosh.timeslot import config
from uwosh.timeslot.widget import TimeWidget
from uwosh.timeslot import util 

from DateTime import DateTime
from Acquisition import aq_parent

TimeSlotSpecialSchema = atapi.Schema((                    

    atapi.DateTimeField('startTime',
        storage=atapi.AnnotationStorage(),
        required=True,
        widget=TimeWidget(label=_('Start Time'),
                          format='%I:%M %P')
    ),
    
    atapi.DateTimeField('endTime',
        storage=atapi.AnnotationStorage(),
        required=True,
        validators = ('isEndTimeAfterStartTime',),
        widget=TimeWidget(label=_('End Time'),
                          show_ymd=False,
                          format='%I:%M %P')
    ),

    atapi.StringField('name',
        storage=atapi.AnnotationStorage(),
        required=True,
        widget=atapi.StringWidget(label=_('Name'),
                            description=_(u'Enter a name for this session.'))
    ),

    atapi.StringField('faculty',
        storage=atapi.AnnotationStorage(),
        required=True,
        vocabulary='getFacultyList',
        enforceVocabulary=1,
        widget=atapi.SelectionWidget(label=_('Faculty'),
                            description=_(u'Select the faculty this session relates to.'))
    ),

    atapi.StringField('campus',
        storage=atapi.AnnotationStorage(),
        required=True,
        vocabulary='getCampusList',
        enforceVocabulary=True,
        widget=atapi.SelectionWidget(label=_('Campus'),
                            description=_(u'Select the campus this session is located at.'))
    ),

    atapi.StringField('roomNumber',
        storage=atapi.AnnotationStorage(),
        required=True,
        widget=atapi.StringWidget(label=_('Room Number'),
                            description=_(u'Enter the room number where this session will be held (for example, 17-028B).'))
    ),

    atapi.StringField('slotLocation',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.StringWidget(label=_('Location'),
                            description=_(u'Enter additional information to describe the location (such as "eResearch Centre Office, ground floor, building 17").'))
    ),

    atapi.IntegerField('maxCapacity',
        storage=atapi.AnnotationStorage(),
        default=10,
        required=True,
        validators = ('isSessionSizeOkay',),
        widget=atapi.IntegerWidget(label=_(u'Session Capacity'),
                                   description=_(u'The maximum number of people who can booking into this session.'))
    ),

    atapi.TextField('emailBodyText',
        required=False,
        searchable=False,
        primary=False,
        storage = atapi.AnnotationStorage(),
        validators = ('isTidyHtmlWithCleanup',),
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(label=_(u'Extra Email Body Text'),
                   description = _(u'Enter additional text to be appended in notification emails to attendees.  This text will appear at the end of the email, on its own line, just before the closing salution. Make sure all links you input here are <strong>absolute (external)</strong> as they will go out via email.'),
                   rows = 5,
                   allow_file_upload = zconf.ATDocument.allow_document_upload),
    ),

    atapi.BooleanField('allowWaitingList',
        storage=atapi.AnnotationStorage(),
        default=False,
        widget=atapi.BooleanWidget(label=_(u'Allow Waiting List'),
                                   description=_(u'Check if you want to allow signups to waiting list once \
                                                   max capacity is reached'))
    ),     

))

TimeSlotSchema = folder.ATFolderSchema.copy() + TimeSlotSpecialSchema

TimeSlotSchema['title'].required = False
TimeSlotSchema['title'].widget.visible = {'view':'invisible', 'edit':'invisible'}
TimeSlotSchema['title'].storage = atapi.AnnotationStorage()
TimeSlotSchema['description'].widget.visible = {'view':'invisible', 'edit':'invisible'}
TimeSlotSchema['description'].storage = atapi.AnnotationStorage()
TimeSlotSchema['allowWaitingList'].widget.visible = {'view':'invisible', 'edit':'invisible'}

TimeSlotSchema['nextPreviousEnabled'].defaultMethod = True
TimeSlotSchema['nextPreviousEnabled'].default_method = lambda: True
TimeSlotSchema['nextPreviousEnabled'].default = True

schemata.finalizeATCTSchema(TimeSlotSchema, folderish=True, moveDiscussion=False)


class TimeSlot(folder.ATFolder):
    implements(ITimeSlot, ICloneable)
	
    portal_type = 'Time Slot'
    schema = TimeSlotSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    startTime = atapi.ATFieldProperty('startTime')
    endTime = atapi.ATFieldProperty('endTime')
    name = atapi.ATFieldProperty('name')
    faculty = atapi.ATFieldProperty('faculty')
    campus = atapi.ATFieldProperty('campus')
    roomNumber = atapi.ATFieldProperty('roomNumber')
    slotLocation = atapi.ATFieldProperty('slotLocation')
    maxCapacity = atapi.ATFieldProperty('maxCapacity')
    emailBodyText = atapi.ATFieldProperty('emailBodyText')

    #Maintained from the original product
    allowWaitingList = atapi.ATFieldProperty('allowWaitingList')



    def Title(self):
        timerange = self.getTimeRange()
        if self.name != '':
            return '%s (%s; %s; %s)' % (timerange,
                                      self.name,
                                      util.getFacultyAbbreviation(self.faculty),
                                      self.campus)
        elif timerange != '':
            return timerange
        else:
            return self.id

    def getTimeRange(self):
        if self.startTime is None or self.endTime is None:
            return ''
        else:
            return '%s - %s' % (self.startTime.strftime('%I:%M %P'), self.endTime.strftime('%I:%M %P'))

    def getDate(self):
        return aq_parent(self).Title()

    def getTimeAndDate(self):
        return '%s: %s' % (self.getTimeRange(), self.getDate())

    def getLabel(self):
        return '%s (%s)' % (self.getTimeAndDate(), self.name)

    def getNumberOfAvailableSpots(self):
        brains = self.portal_catalog.unrestrictedSearchResults(portal_type='Person', review_state='signedup', 
                                                               path=self.getPath())
        numberOfPeopleSignedUp = len(brains)
        return max(0, self.maxCapacity - numberOfPeopleSignedUp)

    def isCurrentUserSignedUpForThisSlot(self):
        member = self.portal_membership.getAuthenticatedMember()
        username = member.getUserName()
        return self.isUserSignedUpForThisSlot(username)

    def isUserSignedUpForThisSlot(self, username):
        brains = self.portal_catalog.unrestrictedSearchResults(portal_type='Person', id=username, 
                                                               path=self.getPath())
        return len(brains) != 0

    def isFull(self):
        return (self.getNumberOfAvailableSpots() == 0) # and not self.allowWaitingList)

    def isInThePast(self):
        return DateTime(aq_parent(self).getDate().Date()+' '+self.getStartTime().Time()).isPast()

    def getPeople(self):
        brains = self.portal_catalog.unrestrictedSearchResults(portal_type='Person', path=self.getPath(), 
                                                               depth=1)
        people = [brain.getObject() for brain in brains]
        return people
        
    def removeAllPeople(self):
        idsToRemove = [person.id for person in self.getPeople()]
        self.manage_delObjects(idsToRemove)

    # Return a path that is correct even when we are using virutual hosts
    def getPath(self):
        path = self.getPhysicalPath()
        return '/'.join(path)

    def getFacultyList(self):
        return util.getFacultyList()

    def getCampusList(self):
        return util.getCampusList()

    def getFacultyName(self):
        return util.getFacultyName(self.faculty)

    def getFacultyAbbreviation(self):
        return util.getFacultyAbbreviation(self.faculty) 

    def getCampusName(self):
        return util.getCampusName(self.campus)

    def showRoomUrl(self):
        return self.campus in ['TSV', 'CNS']

    def getRoomUrl(self):
        map = (self.campus == 'CNS') and 'cairns' or 'townsville'
        url = 'http://www.jcu.edu.au/maps/%s/interactive/?location=%s' % \
                                                  (map, self.roomNumber)
        return url
            

    def getStyleClass(self):
        #We need relevant classes to help our drop-downs distinguish faculty etc
        return 'timeslot' \
               +' campus-'+self.campus \
               +' faculty-'+self.faculty \
               +' room-'+self.roomNumber \
               +' isfull-'+str(self.isFull())
        

atapi.registerType(TimeSlot, config.PROJECTNAME)

