from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole
from Products.CMFPlone import PloneMessageFactory as _

class ScheduleViewerRole(object):
   implements(ISharingPageRole)
   title = _(u"title_can_view_schedule", default=u"uwosh.timeslot: Can view schedule")
   required_permission = "uwosh.timeslot: Manage Schedule"

class ScheduleManagerRole(object):
   implements(ISharingPageRole)
   title = _(u"title_can_manage_schedule", default=u"uwosh.timeslot: Can manage schedule")
   required_permission = "uwosh.timeslot: Manage Schedule"
