from datetime import datetime

from zope import schema
from five import grok
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from plone.directives import form
from collective.z3cform.datetimewidget import DateFieldWidget as datewidget
#from collective.z3cform.datepicker.widget import DatePickerFieldWidget as datewidget

from uwosh.timeslot import config
from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import ISignupSheet

class IManagerReportExportFormSchema(form.Schema):

    form.widget(faculty=CheckBoxFieldWidget)
    faculty = schema.List(title=_(u"Faculty"),
                    description=_(u"Select faculties you would like records for. Selecting nothing implies all faculties."),
                    required=False, default=[],
                    value_type=schema.Choice( \
                                         source=config.FACULTY_VOCABULARY),
                )

    form.widget(session_campus=CheckBoxFieldWidget)
    session_campus = schema.List(title=_(u"Session Campus"),
                    description=_(u"Show bookings for sessions occurring at these selected campuses. Selecting nothing implies all campuses."),
                    required=False, default=[],
                    value_type=schema.Choice( \
                                         source=config.CAMPUS_VOCABULARY),
                )

    form.widget(student_default_campus=CheckBoxFieldWidget)
    student_default_campus = schema.List(title=_(u"Student Default Campus"),
                    description=_(u"Show bookings for students associated with these default campuses. Selecting nothing implies all campuses."),
                    required=False, default=[],
                    value_type=schema.Choice( \
                                         source=config.CAMPUS_VOCABULARY),
                )

    form.widget(startDate=datewidget)
    startDate = schema.Date(title=_(u"Start date"),
                    description=_(u"Select the starting date for your report. Not selecting a date implies you want all records from the end date backward."),
                    required=False,
                )

    form.widget(endDate=datewidget)
    endDate = schema.Date(title=_(u"End date"),
                    description=_(u"Select the ending date for your report.  Not selecting a date implies you want all records from the start date onward."),
                    required=False,
                )

    #sortOrder = schema.List(title=_(u"Sort Order"),
    #                description=_(u"Specify how you would like your report sorted.  Use the controls to select fields, and then use the up and down arrows to specify order. Making no change here accepts default ordering."),
    #                required=False, default=[],
    #                value_type=schema.Choice( \
    #                                     source=config.SORT_ORDER_VOCABULARY),
    #            )

class ManagerReportExportForm(form.SchemaForm):
#    implements(IWrappedForm)
    grok.name('reporting')
    grok.require('uwosh.timeslot.ViewBookings')
    grok.context(ISignupSheet)

    schema = IManagerReportExportFormSchema
    ignoreContext = True
    label = _(u"Reporting: Record Export")
    description = _(u"Select options below to output a report of session registrations.")
    output = None

    def render(self):
        if self.output:
            return self.output
        return super(ManagerReportExportForm,self).render()

    def responseAsCSV(self, file_prefix):
        currentDateTime = datetime.now().strftime('%Y%m%d%H%M')
        filename = '%s-%s-%s.csv' % (file_prefix,
                                     self.context.Title().replace(' ', ''),
                                     currentDateTime)
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader('Content-Disposition', \
                                        'attachment; filename="%s"' % filename)


    @button.buttonAndHandler(_(u'Generate Report'))
    def handleGenerate(self, action):
        data, errors = self.extractData()
        self.responseAsCSV('ehsreport')
        self.output = self.context.exportToCSV(**data)

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)

    @button.buttonAndHandler(_(u"Get Cancellations Log"))
    def handleGetCancellations(self, action):
        self.responseAsCSV('ehscancellations')
        file = open(config.EHS_CANCELLATION_LOG, 'rb')
        self.output = file.read()
        file.close()


