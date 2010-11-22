from zope import schema
from zope.interface import Interface
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.formlib import formbase
from zExceptions import BadRequest

from DateTime import DateTime
from uwosh.timeslot.interfaces import *

from zope.component import queryUtility
from plone.i18n.normalizer.interfaces import IURLNormalizer

from uwosh.timeslot.content.timeslot import TimeSlotSpecialSchema
from uwosh.timeslot.util import getFacultyAbbreviation

# Begin ugly hack. It works around a ContentProviderLookupError: plone.htmlhead error caused by Zope 2 permissions.
#
# Source: http://athenageek.wordpress.com/2008/01/08/contentproviderlookuperror-plonehtmlhead/
# Bug report: https://bugs.launchpad.net/zope2/+bug/176566
#

def _getContext(self):
    self = self.aq_parent
    while getattr(self, '_is_wrapperish', None):
        self = self.aq_parent
    return self    
            
ZopeTwoPageTemplateFile._getContext = _getContext

# End ugly hack.

class IClone(Interface):
    numToCreate = schema.Int(title=u'Number to Create', description=u'The number of clones to create', required=True)

class ICloneDay(IClone):
    includeWeekends = schema.Bool(title=u'Include Weekends', description=u'Do you want to include weekends?')

class ICloneTimeSlot(IClone):
    pass

class CloneForm(formbase.PageForm):
    result_template = ZopeTwoPageTemplateFile('cloning-results.pt')
    success = True
    errors = []
    form_fields = form.FormFields(IClone)
    
    def __init__(self, context, request):
        formbase.PageForm.__init__(self, context, request)

        if IDay.providedBy(context):
            self.form_fields = form.FormFields(ICloneDay)
        elif ITimeSlot.providedBy(context):
            self.form_fields = form.FormFields(ICloneTimeSlot)
        else:
            self.form_fields = form.FormFields(IClone)
            
    @form.action('Clone')
    def action_clone(self, action, data):
        self.parent = self.context.aq_inner.aq_parent 
        self.success = True
        self.errors = []
        self.numToCreate = data['numToCreate']
        if 'includeWeekends' in data:
            self.includeWeekends = data['includeWeekends']
        
        if IDay.providedBy(self.context):
            self.cloneDay()            
        elif ITimeSlot.providedBy(self.context):
            self.cloneTimeSlot()            
        else:
            self.success = False 
            self.errors.append('This is not a cloneable type')
        
        return self.result_template()
   
    def cloneDay(self):
        origDate = self.context.getDate()
        contents = self.context.manage_copyObjects(self.context.objectIds())
        numCreated = 0
        
        i = 1
        while numCreated < self.numToCreate:
            newDate = origDate + i
            if self.includeWeekends or (newDate.aDay() not in ['Sat', 'Sun']):
                try:
                    newDay = self.createNewDay(newDate, contents)
                except BadRequest:
                    self.success = False
                    self.errors.append("Operation failed because there is already an object named: %s" % newDate)
                else:
                    numCreated += 1
                    if numCreated == 1:
                        newDay.removeAllPeople()
                        contents = newDay.manage_copyObjects(newDay.objectIds())
            i += 1        
                
    def createNewDay(self, date, contents):
        #id = date.strftime('%a-%b.-%d-%Y')
        original_id = date.strftime('%a-%d-%B-%Y')
        original_id = queryUtility(IURLNormalizer).normalize(original_id)
        id = original_id

        counter = 1
        while id in self.parent:
            id = original_id + '-clone-' + str(counter)

        self.parent.invokeFactory('Day', id, date=date)            
        newDay = self.parent[id]
        newDay.manage_pasteObjects(contents)
        newDay.reindexObject()     
        return newDay
        
    def cloneTimeSlot(self):
        properties = {}
        for key in TimeSlotSpecialSchema._fields.keys():
            properties[key] = self.context[key]

        origStartTime = properties['startTime']
        origEndTime = properties['endTime']
        properties['emailBodyText'] = properties['emailBodyText'].getRaw()
        del properties['startTime']
        del properties['endTime']
        slotLength = (float(origEndTime) - float(origStartTime)) / 60 / 60 / 24
        
        numCreated = 0
        while numCreated < self.numToCreate:
            newStartTime = origStartTime + (slotLength * (numCreated + 1))
            newEndTime = origEndTime + (slotLength *  (numCreated + 1))
            newTimeSlot = self.createNewTimeSlot(newStartTime, newEndTime, **properties)
            numCreated += 1

    def createNewTimeSlot(self, startTime, endTime, **properties):
        id = (startTime.strftime('%I-%M-%P') + '-' + endTime.strftime('%I-%M-%P')).lower()
        name = properties.get('name') or '';
        faculty_abbr = getFacultyAbbreviation(properties['faculty'])
        campus = properties['campus']
        if name != '':
            id = id + '-' + name + '-' + faculty_abbr + '-' + campus
        original_id = queryUtility(IURLNormalizer).normalize(id)
        id = original_id

        counter = 1
        while id in self.parent:
            id = original_id + '-' + str(counter)

        try:
            self.parent.invokeFactory('Time Slot', id, startTime=startTime, endTime=endTime, **properties)
        except BadRequest:
            self.success = False
            self.errors.append("An object already exists with id: %s" % id)
            return None
            
        newTimeSlot = self.parent[id]
        return newTimeSlot
