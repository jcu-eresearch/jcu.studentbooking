from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.browser.base import BaseBrowserView

class IShowReservations(Interface):
    pass


class ShowReservations(BaseBrowserView):
    implements(IShowReservations)

    pageTemplate = ZopeTwoPageTemplateFile('showreservations.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self):
        if self.isCurrentUserLoggedIn():
            return self.pageTemplate()
        else:
           self.request.response.redirect(self.context.absolute_url() + '/login_form?came_from=./@@show-reservations')

