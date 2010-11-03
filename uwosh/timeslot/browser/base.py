from Products.Five import BrowserView
from plone.memoize import instance
from Products.CMFCore.utils import getToolByName
from uwosh.timeslot import config

from z3c.sqlalchemy import getSAWrapper


class BaseBrowserView(BrowserView):

    wrapper = getSAWrapper(config.EHS_BOOKING_DB_CONNECTOR)
    ehs_mapper = wrapper.getMapper(config.EHS_BOOKING_ABSOLUTE_NAME)

    @property
    def absolute_url(self):
       return "%s/@@%s" % (self.context.absolute_url(), self.__name__)

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
    def queryStudentDetails(self, member_id, first=False, as_dict=True, use_student_id=False):
        '''Query student information from our database connection.
           By default, we search purely on their JCU ID and return all
           results as dictionaries.'''
        mapper_class = self.ehs_mapper.class_

        attribute = use_student_id and mapper_class.studentNumber or mapper_class.studentLoginId
        query = self.wrapper.session.query(self.ehs_mapper.class_).filter(attribute == member_id)

        #if conditions:
        #    for condition in conditions:
        #        query = query.filter( getattr(mapper_class, condition) == conditions[condition])

        results = None
        if first:
            results = query.first()
            results = results and [results]  #wrap in a list
        else:
            results = query.all();

        if as_dict and results and len(results) > 0:
            results = [result.asDict() for result in results]

        return results
