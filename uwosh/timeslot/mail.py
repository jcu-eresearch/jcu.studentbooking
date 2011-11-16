from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from collective.templateengines.backends.jinja import Template
from collective.easytemplate.engine import getTemplateContext

from uwosh.timeslot import config

class EmailTemplatingException(Exception):

    def __init__(self, error, type):
        self.error = error
        self.type = type

    def __str__(self):
        return repr(self.error)

def performTemplating(signup_sheet, person, email_type):

    #Get our email specifications from our configuration
    emailSpecs = config.EHS_EMAIL_TYPES[email_type]

    #Get the right type of email field's contents here
    email_body = getattr(signup_sheet, emailSpecs['bodyField']).decode('utf-8')

    templateContext = getTemplateContext(person)

    #Load our body text into the templating engine
    template, syntax_errors = config.EHS_TEMPLATING_ENGINE.loadString(
        email_body, False)

    if syntax_errors:
        raise EmailTemplatingException(syntax_errors,
                                       config.SYNTAX_ERROR)

    #Evaluate our template based upon our selected context (person)
    result, evaluation_errors = template.evaluate(templateContext)

    if evaluation_errors:
        raise EmailTemplatingException(evaluation_errors,
                                       config.EVALUATION_ERROR)

    return result


def sendNotificationEmail(context, person, \
                          email_type=config.EHS_CONFIRMATION_EMAIL, \
                          immediate=False,
                          log=False):
    '''Send email notification about something that has happened
       on the site.  Context should be the booking sheet.'''

    portal = getSite()

    try:
        templated_body = performTemplating(signup_sheet=context,
                                           person=person,
                                           email_type=email_type)
    except:
        #We're in the poo here because someone broke the template,
        #probably.  They should really check their syntax.
        context.plone_log('Warning: problem with EHS email template %s.' %
                          email_type)
        raise

    #If no exceptions were raised, then we're fine to continue.
    mto = [person.jcu_email,]
    personalEmail = person.pers_email
    if personalEmail:  mto.append(personalEmail)

    mfrom = "%s <%s>" % (portal.getProperty('email_from_name'),\
                         portal.getProperty('email_from_address'))
    msubject = config.EHS_EMAIL_TYPES[email_type]['subject']

    mh = getToolByName(context, 'MailHost')

    mh.send(templated_body, mto=mto, mfrom=mfrom, \
            subject=msubject, encode=None, \
            immediate=immediate, charset='utf8', msg_type='text/html')

    if log:
        context.plone_log("Mail sent to "+str(mto))

