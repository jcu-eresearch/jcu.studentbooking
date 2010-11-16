from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from collective.templateengines.backends.jinja import Template
from collective.easytemplate.engine import getTemplateContext

from uwosh.timeslot import config

def sendNotificationEmail(context, person, \
                          email_type=config.EHS_CONFIRMATION_EMAIL):
    '''Send email notification about something that has happened
       on the site.  Context should be the booking sheet.'''

    portal = getSite()

    #Get our email specifications from our configuration
    emailSpecs = config.EHS_EMAIL_TYPES[email_type]

    #Get the right type of email field's contents here
    email_body = context[emailSpecs['bodyField']].getRaw()

    try:
        templateContext = getTemplateContext(person)
        templated_body = Template(config.EHS_TEMPLATING_ENGINE, \
                                  email_body).evaluate(templateContext)[0]
    except:
        #We're in the poo here because someone broke the template,
        #probably.  They should really check their syntax.
        context.plone_log('Warning: problem with EHS email template.')
     
    mto = [person.getEmail(),'david@davidjb.com',]
    personalEmail = person.getPersonalEmail()
    if personalEmail:  mto.append(personalEmail)

    mfrom = "%s <%s>" % (portal.getProperty('email_from_name'),\
                         portal.getProperty('email_from_address'))
    msubject = emailSpecs['subject']  

    mh = getToolByName(context, 'MailHost')
    mh.secureSend(templated_body, mto=mto, mfrom=mfrom, \
            subject=msubject, subtype='html')

    #Oh Plone 4 where art thou?
    #mh.send(templated_body, mto=mto, mfrom=mfrom, \
    #        subject=msubject, encode=None, \
    #        immediate=True, charset='utf8', msg_type='text/html')
    print "Mail sent to "+str(mto)

def sendReminderEmails(context):
    '''This script is to be run once every day and sends a reminder
       email to each and every student with a booking on the next day.
       So, if we run Monday, we should be sending for Wednesday's sessions.'''
    portal = getSite()
    #Figure out which day we're sending for

    #DateTime()

    #Get all sessions on the given day
  
#   for session in sessions:
#       for person in session:
#           try:
#               mail.sendNotificationEmail(context=context,
#                                     person=person,
#                                     request=request,
#                                     email_type=config.EHS_REMINDER_EMAIL)     #           except:
#               pass
#   
#   plone_log('X reminder emails sent).