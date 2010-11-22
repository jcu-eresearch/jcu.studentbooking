from AccessControl import Unauthorized
from Acquisition import aq_inner
from DateTime import DateTime

from zope.component import getMultiAdapter
from zope.interface import implements, Interface
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot import config, mail
from uwosh.timeslot.browser.base import BaseBrowserView

class ISendRemindersView(Interface):
    pass


class SendRemindersView(BaseBrowserView):
    implements(ISendRemindersView)

    def __call__(self):
        '''This script is to be run once every day and sends a reminder
           email to each and every student with a booking on the next day.
           So, if we run Monday, we should be sending for Wednesday's sessions.'''
        catalog = getToolByName(self.context, 'portal_catalog')
 
        #We want the date two days from now.
        target_date = DateTime().earliestTime()+2

        days = catalog.unrestrictedSearchResults(path=self.context.getPath(),
                                                 portal_type='Day',
                                                 getDate=target_date)
        mail_counter = 0
        mail_error_counter = 0
        for day in days:
            the_day = day.getObject()
            for session in the_day.contentItems():
                for person in session[1].contentItems():
                    try:
                        mail.sendNotificationEmail(context=self.context,
                                         person=person[1],
                                         email_type=config.EHS_REMINDER_EMAIL)
                        mail_counter += 1;
                    except:
                        mail_error_counter += 1;
                        raise

        #Log how many emails were sent.
        self.context.plone_log("EHS Reminders Sent:  We just spammed %s students and had %s errors when sending mail." % (mail_counter, mail_error_counter))
        return



