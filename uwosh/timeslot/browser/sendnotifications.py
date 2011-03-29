from zope import schema
from zope.interface import Invalid
from zope.component import getMultiAdapter
from five import grok
from z3c.form import button
from z3c.form.interfaces import ActionExecutionError, IErrorViewSnippet
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.formwidget.contenttree import MultiContentTreeFieldWidget

from uwosh.timeslot import config, mail, util
from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import ISignupSheet
from uwosh.timeslot.validators import hasValue

grok.templatedir('templates')


class ISendNotificationsSchema(form.Schema):

    form.widget(bookings=MultiContentTreeFieldWidget)
    bookings = RelationList(
        title=_(u"Bookings"),
        description=_(u"Select bookings to send email notifications.  If you want to test sending an email, please manually create a test session and booking."),
        value_type = RelationChoice(
            title=_(u"Locate booking"),
            source=ObjPathSourceBinder(
                {
                    'portal_type': {'query': ['Signup Sheet','Day','Time Slot', 'Person'],
                                    'operator':'or'},
                },
                portal_type='Person'),
        ),
        required=True,
        constraint=hasValue,
    )

    form.widget(notifications=CheckBoxFieldWidget)
    notifications = schema.List(
        title=_(u"Notifications"),
        description=_(u"Select which notification emails you would like to send."),
        required=True,
        value_type=schema.Choice(source=config.EHS_NOTIFICATION_VOCABULARY),
    )

    confirmation = schema.Bool(
        title=_(u"Confirmation"),
        description=_(u"Select this to confirm you wish to send emails to the selected bookings.  The send email operation is not reversible."),
        constraint=hasValue,
    )


class SendNotificationsForm(form.SchemaForm):
#    implements(IWrappedForm)
    grok.name('send-notifications')
    grok.require('uwosh.timeslot.ManageBookings')
    grok.context(ISignupSheet)
    grok.template('sendnotifications')

    schema = ISendNotificationsSchema
    ignoreContext = True
    label = _(u"Notifications: Send Emails")
    a_description = _(u"Select options below to send emails relating to EHS bookings.  You can check emails by sending to test bookings, or otherwise send actual notifications to users.")

    @button.buttonAndHandler(_(u'Check Syntax'))
    @button.buttonAndHandler(_(u'Send'))
    def handleSend(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        #Otherwise, if no errors on the form, then send our emails
        templating_errors = []
        mail_counter = 0
        for person in data['bookings']:
            for notification in data['notifications']:
                try:
                    if action.value == 'Check Syntax':
                        #Just do the templating, don't send mail
                        mail.performTemplating(self.context,
                                               person,
                                               notification)
                    else:
                        #Actually send the mail and run the whole process
                        mail.sendNotificationEmail(
                            context=self.context,
                            person=person,
                            email_type=notification,
                            log=True,
                        )
                    mail_counter += 1
                except mail.EmailTemplatingException as exception:
                    messages = []
                    for err in exception.error:
                        wrapped = err.getException()[1]

                        #Some errors mightn't have line numbers.
                        pretty_line_output = ''
                        if hasattr(wrapped, 'lineno'):
                            pretty_line_output = ', Line %d' % wrapped.lineno

                        #Produce our nicely formatted template error output
                        pretty_output = "%s error (%s%s): %s" % (
                            exception.type,
                            notification,
                            pretty_line_output,
                            repr(wrapped),
                        )
                        templating_errors += [pretty_output,]


        #Display the errors for the user to peruse
        if templating_errors:
            visual_error = Invalid('<br />\n'.join(templating_errors))
            error = getMultiAdapter((visual_error, self.request, None,
                                     None, self, self.context),
                                    IErrorViewSnippet)
            error.render = lambda: util.render_html(error)
            error.update()
            self.widgets.errors += (error,)
            self.status = self.formErrorsMessage
        else:
            if action.value == 'Check Syntax':
                self.successMessage = u'No errors detected in templates!'
            else:
                self.successMessage = \
                        u'Successfully sent %d mail messages.' % \
                        mail_counter
            self.status = self.successMessage


    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)

