from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import IDay, ICloneable
from uwosh.timeslot.config import PROJECTNAME

DaySchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.DateTimeField('date',
        storage=atapi.AnnotationStorage(),
        required=True,
        widget=atapi.CalendarWidget(label=_('Date'),
                                    show_hm=False,
                                    format='%A, %d %B %Y',
                                    starting_year=2009)
    ),

))

DaySchema['title'].required = False
DaySchema['title'].widget.visible = {'view':'invisible', 'edit':'invisible'}
DaySchema['title'].storage = atapi.AnnotationStorage()
DaySchema['description'].widget.visible = {'view':'invisible', 'edit':'invisible'}
DaySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(DaySchema, folderish=True, moveDiscussion=False)

class Day(folder.ATFolder):
    implements(IDay, ICloneable)

    portal_type = 'Day'
    schema = DaySchema

    title = atapi.ATFieldProperty('title')
    date = atapi.ATFieldProperty('date')
    description = atapi.ATFieldProperty('description')
    
    def Title(self):
    	if self.date is None:
            return self.id
    	else:
    	    return self.date.strftime('%A, %d %B %Y')
    
    def getTimeSlots(self):
        brains = self.portal_catalog.unrestrictedSearchResults(portal_type='Time Slot', path=self.getPath(), depth=1,
                                                               sort_on='getStartTime', sort_order='ascending')
        timeSlots = [brain.getObject() for brain in brains]
        return timeSlots
        
    def getTimeSlot(self, title):
        clean_title = '"' + title + '"'
        brains = self.portal_catalog.unrestrictedSearchResults(portal_type='Time Slot', Title=clean_title, 
                                                               path=self.getPath(), depth=1)
        if len(brains) == 0:
            raise ValueError('The TimeSlot %s was not found.' % title)

        timeSlot = brains[0].getObject()
        return timeSlot

    def removeAllPeople(self):
        timeSlots = self.getTimeSlots()
        for timeSlot in timeSlots:
            timeSlot.removeAllPeople()

    # Return a path that is correct even when we are using virtual hosts
    def getPath(self):
        path = self.getPhysicalPath()
        return '/'.join(path)
        

atapi.registerType(Day, PROJECTNAME)
