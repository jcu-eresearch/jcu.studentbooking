from datetime import datetime

from zExceptions import BadRequest
from zope import schema
from five import grok
from zope.interface import Interface, implements
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from plone.app.form.widgets.multicheckboxwidget import MultiCheckBoxWidget
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from z3c.form import field, button
from plone.directives import form
from plone.i18n.normalizer.interfaces import IURLNormalizer
from Products.Archetypes.utils import contentDispositionHeader
from collective.z3cform.datetimewidget import DateFieldWidget as datewidget
#from collective.z3cform.datepicker.widget import DatePickerFieldWidget as datewidget
from z3c.form.browser.checkbox import CheckBoxWidget

from uwosh.timeslot import config
from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.content.timeslot import TimeSlotSpecialSchema
from uwosh.timeslot.interfaces import ISignupSheet
from uwosh.timeslot.util import getFacultyAbbreviation

from plone.z3cform.interfaces import IWrappedForm

class IManagerReportExportFormSchema(form.Schema):
    
    form.widget(faculty=CheckBoxFieldWidget)
    faculty = schema.List(title=_(u"Faculty"),
                    description=_(u"Select faculties you would like records for. Selecting nothing implies all faculties."),
                    required=False, default=[],
                    value_type=schema.Choice( \
                                         source=config.FACULTY_VOCABULARY),
                )

    form.widget(campus=CheckBoxFieldWidget)
    campus = schema.List(title=_(u"Campus"),
                    description=_(u"Select campuses you would like records for. Selecting nothing implies all campuses."),
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
    grok.name('manager-summary')
    grok.require('uwosh.timeslot.ViewBookings')
    grok.context(ISignupSheet)
 
    schema = IManagerReportExportFormSchema
    ignoreContext = True
    label = _(u"Manager Summary: Report Export")
    description = _(u"Select options below to output a report of session sign ups")
    output = None

    def render(self):
        if self.output:
            return self.output
        return super(ManagerReportExportForm,self).render() 
    
    @button.buttonAndHandler(_(u'Generate'))
    def handleGenerate(self, action):
        data, errors = self.extractData()
 
        currentDateTime = datetime.now().strftime('%Y%m%d%H%M')
        filename = '%s-%s.csv' % (self.context.Title().replace(' ', ''),
                                   currentDateTime)

        self.request.response.setHeader('Content-Type', 'text/csv')
	self.request.response.setHeader('Content-Disposition', 'attachment; filename="%s"' % filename)

        self.output = self.context.exportToCSV(**data)
 
    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)
 
