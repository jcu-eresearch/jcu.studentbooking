from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from uwosh.timeslot import timeslotMessageFactory as _


class IPerson(Interface):
    pass

class ITimeSlot(Interface):
    pass

class IDay(Interface):
    pass

class ISignupSheet(Interface):
    pass
        
class ICloneable(Interface):
    pass
