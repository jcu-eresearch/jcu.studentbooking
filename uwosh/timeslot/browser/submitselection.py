from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from uwosh.timeslot import timeslotMessageFactory as _

class ISubmitSelection(Interface):
    pass


class SubmitSelection(BrowserView):
    implements(ISubmitSelection)

    resultTemplate = ZopeTwoPageTemplateFile('signupresults.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def submitUserSelection(self):
        self.results = list()

    	self.getUserInput()
    	self.getMemberInfo()
        
        if not self.areAnyRequiredFieldsEmpty() and self.isAtLeastOneSlotSelected():
            for slotLabel in self.selectedSlots:
                self.getSlotAndSignUserUpForIt(slotLabel)

        return self.resultTemplate()

    def getUserInput(self):
        for (field, _) in self.context.schema['extraFields'].vocabulary:
            setattr(self, field, self.request.get(field, ''))

        self.selectedSlots = self.request.get('slotSelection', None)

        if type(self.selectedSlots) != list:
            self.selectedSlots = [self.selectedSlots]
		
    def getMemberInfo(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()

        self.username = member.getUserName()
        self.fullname = member.getProperty('fullname')
        if self.fullname == '':
            self.fullname = self.username
        self.email = member.getProperty('email')

    def isAtLeastOneSlotSelected(self):
        return self.selectedSlots != [None]

    def areAnyRequiredFieldsEmpty(self):
        return len(self.getListOfEmptyRequiredFields()) > 0

    def getListOfEmptyRequiredFields(self):
        fieldNames = dict(self.context.schema['extraFields'].vocabulary)
        emptyRequiredFields = []
    
        requiredExtraFields = self.context.getExtraFields()
        for field in requiredExtraFields:
            if (len(getattr(self, field)) < 1) and (field in fieldNames):
                emptyRequiredFields.append(fieldNames[field])

        return emptyRequiredFields

    def getSlotAndSignUserUpForIt(self, slotLabel):
        success = False
        waiting = True
        error = ''

        allowSignupForMultipleSlots = self.context.getAllowSignupForMultipleSlots()

        (date, time) = slotLabel.split(' @ ')
        day = self.context.getDay(date)
        timeSlot = day.getTimeSlot(time)
        allowWaitingList = timeSlot.getAllowWaitingList()
        numberOfAvailableSpots = timeSlot.getNumberOfAvailableSpots()
        
        if (not allowSignupForMultipleSlots) and self.context.isCurrentUserSignedUpOrWaitingForAnySlot():
            success = False
            error = 'You are already signed up for a slot in this signup sheet.'

        elif timeSlot.isCurrentUserSignedUpForThisSlot():
            sucess = False
            error = 'You are already signed up for this slot.'

        elif allowWaitingList or numberOfAvailableSpots > 0:
            person = self.createPersonObject(timeSlot)
                
            if numberOfAvailableSpots > 0:
                self.signupPerson(person)
                waiting = False
            elif self.isEmailValid():
                self.sendWaitingListConfirmationEmail(self.context, slotLabel)
                    
            success = True
            
        else:
            success = False
            error = 'The slot you selected is already full. Please select a different one'

        result = dict()
        result['slotLabel'] = slotLabel
        result['success'] = success
        result['waiting'] = waiting
        result['error'] = error
        self.results.append(result)

    def createPersonObject(self, container):
        container.invokeFactory('Person', self.username)
        newPerson = container[self.username]
        newPerson.setEmail(self.email)
        newPerson.setTitle(self.fullname)
        for (field, _) in self.context.schema['extraFields'].vocabulary:
            setattr(newPerson, field, getattr(self, field))
        newPerson.reindexObject()
        return newPerson

    def signupPerson(self, person):
        portal_workflow = getToolByName(self, 'portal_workflow')
        portal_workflow.doActionFor(person, 'signup')
        person.reindexObject()
  
    def isEmailValid(self):
        isEmail = validation.validatorFor('isEmail')
        return isEmail(self.email) == 1

    def sendWaitingListConfirmationEmail(self, signupSheet, slotLabel):
        url = signupSheet.absolute_url()

        extraEmailContent = signupSheet.getExtraEmailContent()
        contactInfo = signupSheet.getContactInfo()
        toEmail = self.email
        fromEmail = "%s <%s>" % (self.context.email_from_name, self.context.email_from_address)
        subject = signupSheet.Title() + ' - Waiting List Confirmation'
        
        message = 'Hi ' + self.fullname + ',\n\n'
        message += 'This message is to confirm that you have been added to the waiting list for:\n'
        message += slotLabel + '\n\n'

        if extraEmailContent != ():
            for line in extraEmailContent:
                message += line + '\n'
            message += '\n'

        message += url + '\n\n'
        
        if contactInfo != ():
            message += 'If you have any questions please contact:\n'
            for line in contactInfo:
                message += line + '\n'
            message += '\n'

        mailHost = self.context.MailHost
        mailHost.secureSend(message, toEmail, fromEmail, subject)
