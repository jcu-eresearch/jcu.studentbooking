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
    email_body = context[emailSpecs['bodyField']].decode('utf-8')

    try:
        templateContext = getTemplateContext(person)
        templated_body = Template(config.EHS_TEMPLATING_ENGINE, \
                                  email_body).evaluate(templateContext)[0]
    except:
        #We're in the poo here because someone broke the template,
        #probably.  They should really check their syntax.
        context.plone_log('Warning: problem with EHS email template.')
        raise

    mto = [person.jcu_email,]
    personalEmail = person.pers_email
    if personalEmail:  mto.append(personalEmail)

    mfrom = "%s <%s>" % (portal.getProperty('email_from_name'),\
                         portal.getProperty('email_from_address'))
    msubject = emailSpecs['subject']

    mh = getToolByName(context, 'MailHost')

    mh.send(templated_body, mto=mto, mfrom=mfrom, \
            subject=msubject, encode=None, \
            immediate=False, charset='utf8', msg_type='text/html')
    context.plone_log("Mail sent to "+str(mto))

