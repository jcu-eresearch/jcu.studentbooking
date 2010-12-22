from zope.interface import implements, Interface

from uwosh.timeslot.browser.base import BaseBrowserView

class IBookingDebugView(Interface):
    pass

class BookingDebugView(BaseBrowserView):
    implements(IBookingDebugView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, *args, **kwargs):
        import ipdb; ipdb.set_trace()
        self.student_records = self.queryStudentDetails(self.student_id, first=False, as_dict=True, search_student_id=True, search_login_id=True)
        print 'foobar'
        return output

