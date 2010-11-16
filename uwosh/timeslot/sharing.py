from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole
from Products.CMFPlone import PloneMessageFactory as _

class BookingViewerRole(object):
   implements(ISharingPageRole)
   title = _(u"title_can_view_schedule", default=u"EHS: View all bookings")
   required_permission = "jcu.booking: Manage bookings"

class BookingStaffRole(object):
   implements(ISharingPageRole)
   title = _(u"title_can_book_another_user_in", default=u"EHS: Book as another user")
   required_permission = "jcu.booking: Manage bookings"

class BookingManagerRole(object):
   implements(ISharingPageRole)
   title = _(u"title_can_manage_schedule", default=u"EHS: Manage bookings")
   required_permission = "jcu.booking: Manage bookings"
