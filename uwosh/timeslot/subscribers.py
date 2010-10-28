
from Products.validation import validation
from Products.CMFCore.utils import getToolByName

def sendSignupNotificationEmail(obj, event):
    isEmail = validation.validatorFor('isEmail')
    
    if event.transition and event.transition.id == 'signup':
        person = obj
        timeSlot = person.aq_parent
        day = timeSlot.aq_parent
        signupSheet = day.aq_parent

        if isEmail(person.getEmail()) == 1:      
            url = signupSheet.absolute_url()

            extraEmailContent = signupSheet.getExtraEmailContent()
            contactInfo = signupSheet.getContactInfo()
            toEmail = person.getEmail()
            fromEmail = "%s <%s>" % (obj.email_from_name, obj.email_from_address)
            subject = signupSheet.Title() + ' - Registration Confirmation'

            message = 'Hi ' + person.Title() + ',\n\n'
            message += 'This message is to confirm that you have been signed up for:\n'
            message += timeSlot.getLabel() + '\n\n'

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
            
            mailHost = obj.MailHost
            mailHost.secureSend(message, toEmail, fromEmail, subject)          


def attemptToFillEmptySpot(obj, event):
    if obj.getReviewState() == 'signedup':
        timeSlot = obj.aq_parent

        portal_membership = getToolByName(obj, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        user = member.getUser()

        if timeSlot.getNumberOfAvailableSpots() > 0 and hasattr(user, 'getName'):
            username = user.getName()
            timeSlot.manage_addLocalRoles(username, ['Manager'])

            portal_catalog = getToolByName(obj, 'portal_catalog')
            query = {'portal_type':'Person','review_state':'waiting', 'sort_on':'Date', 'sort_order':'ascending'}
            brains = portal_catalog.unrestrictedSearchResults(query, path=timeSlot.getPath())
            if len(brains) > 0:
                person = brains[0].getObject()
                portal_workflow = getToolByName(obj, 'portal_workflow')
                portal_workflow.doActionFor(person, 'signup')
                person.reindexObject()

            timeSlot.manage_delLocalRoles([username])
        
