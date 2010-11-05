from Products.Five import BrowserView

from uwosh.timeslot import timeslotMessageFactory as _

from uwosh.timeslot.browser.base import BaseBrowserView

class CancelReservation(BaseBrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def cancelReservation(self):
    	selectedSlots = self.request.get('selectedSlot', None)
    	if type(selectedSlots) != list:
            selectedSlots = [selectedSlots]

        if selectedSlots != [None]:
            for slot in selectedSlots:
                self.deleteCurrentUserFromSlot(slot)

        self.request.response.redirect(self.context.absolute_url() + '/@@show-reservations')

    def deleteCurrentUserFromSlot(self, slot):
        username = self.getAuthenticatedMember().getId()

        (date, time) = slot.split(' @ ')
        day = self.context.getDay(date)
        timeSlot = day.getTimeSlot(time)
        timeSlot.manage_delObjects([username,])
