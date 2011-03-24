from zope.interface import implements, Interface
from Products.CMFCore.utils import getToolByName

from uwosh.timeslot import config
from uwosh.timeslot.browser.base import BaseBrowserView

class IAutoCloseSessionsView(Interface):
    pass


class AutoCloseSessionsView(BaseBrowserView):
    implements(IAutoCloseSessionsView)

    def __call__(self):
        '''This script is to be run once every 15 minutes and automatically
           closes off sessions according to their auto-closure time.
        '''
        catalog = getToolByName(self.context, 'portal_catalog')
        workflow_tool = getToolByName(self.context, 'portal_workflow')

        sessions = catalog.unrestrictedSearchResults(path=self.context.getPath(), portal_type='Time Slot')

        session_closure_counter = 0
        for session in sessions:
            the_session = session.getObject()
            if the_session.isPastAutoClosureTime() \
               and not the_session.isFull() \
               and not the_session.isClosed():
                workflow_tool.doActionFor(the_session, \
                                          config.SESSION_CLOSE_WF_ACTION)
                session_closure_counter += 1;

        #Log how many sessions were auto-closed
        self.context.plone_log("EHS Auto-Closure:  We just automatically closed %s sessions." % (session_closure_counter))
        return



