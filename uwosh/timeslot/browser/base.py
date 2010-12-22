from Products.Five import BrowserView
from plone.memoize import instance
from uwosh.timeslot import config

from z3c.sqlalchemy import getSAWrapper
from sqlalchemy import or_, and_

from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

from AccessControl import Unauthorized


class BaseBrowserView(BrowserView):

    wrapper = getSAWrapper(config.EHS_BOOKING_DB_CONNECTOR)
    ehs_mapper = wrapper.getMapper(config.EHS_BOOKING_ABSOLUTE_NAME)

    @property
    def absolute_url(self):
       return "%s/@@%s" % (self.context.absolute_url(), self.__name__)

    @property
    def logout_url(self):
       plone_view = getMultiAdapter((self.context, self.request), name='plone')
       return plone_view.navigationRootUrl()+'/logout'

    def authenticateForm(self):
       authenticator = getMultiAdapter((self.context, self.request), name=u"authenticator")
       if not authenticator.verify(): raise Unauthorized('Your form submission did not authenticate correctly.') 

    @instance.memoize
    def isCurrentUserLoggedIn(self):
        member = self.getAuthenticatedMember()
        return 'Authenticated' in member.getRoles()

    @instance.memoize
    def getAuthenticatedMember(self):
        '''Get the current authenticated member on the site'''
        portal_membership = getToolByName(self.context, 'portal_membership')
        return portal_membership.getAuthenticatedMember()

    @instance.memoize
    def queryStudentDetails(self, member_id, first=False, as_dict=True, search_student_id=True, search_login_id=False):
        '''Query student information from our database connection.
           By default, we search purely on their JCU ID and return all
           results as dictionaries. We can search on both JCU ID and
           student ID by changing the last parameter.'''
        mapper_class = self.ehs_mapper.class_

        query = self.wrapper.session.query(mapper_class)
        if search_student_id:
            query = query.filter(mapper_class.stu_id == member_id)
        elif search_login_id:
            query = query.filter(mapper_class.login_id == member_id)
        else:
            #Bail.  We clearly don't want to search anything.
            query = None

        results = None
        if query:
            if first:
                results = query.first()
                results = results and [results]  #wrap in a list
            else:
                results = query.all();

        if as_dict and results and len(results) > 0:
            results = [result.asDict() for result in results]

        return results
