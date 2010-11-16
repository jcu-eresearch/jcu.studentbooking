from Products.validation.interfaces.IValidator import IValidator
from Products.validation.i18n import PloneMessageFactory as _
from Products.validation.i18n import recursiveTranslate
from Products.validation.i18n import safe_unicode
import re
from types import StringType

from Products.validation.validators.BaseValidators import EMAIL_RE
from Products.validation.validators.RegexValidator import ignoreRE, RegexValidator

from DateTime import DateTime

def patched_validate_required(self, instance, value, errors):
    if not value:
        return "This field is required"
    return None

class SanerValidator(RegexValidator):

    def __call__(self, value, *args, **kwargs):
        if type(value) != StringType:
            msg =  _(u"$value of type $type, expected a string.",
                     mapping = {
                        'name' : safe_unicode(self.name),
                        'value': safe_unicode(value),
                        'type' : safe_unicode(type(value))
                        })
            return recursiveTranslate(msg, **kwargs)

        ignore = kwargs.get('ignore', None)
        if ignore:
            value = ignoreRE(value, ignore)
        elif self.ignore:
            value = ignoreRE(value, self.ignore)


        for r in self.regex:
            m = r.match(value)
            if not m:
                msg =  _(u"'$value' $errmsg",
                         mapping={
                            'name' : safe_unicode(self.name),
                            'value': safe_unicode(value),
                            'errmsg' : safe_unicode(self.errmsg)
                            })

                return recursiveTranslate(msg, **kwargs)
        return 1 

class EndTimeAfterStartTimeValidator:
    __implements__ = IValidator

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        request = kwargs['REQUEST']
        if DateTime(request['startTime']) >= DateTime(request['endTime']):
            return """Your ending time needs to be after your starting time."""
        return 1

class SessionSizeIsOkayValidator:
    __implements__ = IValidator

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            session_count = len(instance.getFolderContents())
            value_int = int(value)
            if value_int < 1:
                return "Enter a valid capacity."
            elif value_int < session_count:
                return "You already have " + str(session_count) + " student" + \
                       (session_count == 1 and ' ' or 's ') + \
                       "signed up for this session.  You cannot reduce \
                         the capacity to less than this."

        return 1

sanerValidators = [
    EndTimeAfterStartTimeValidator('isEndTimeAfterStartTime'),
    SessionSizeIsOkayValidator('isSessionSizeOkay'),
    SanerValidator('saneIsPhoneNumber', r'^\d+$', ignore='[\(\)\-\s\+]',
                   title='', description='',
                   errmsg=_(u'is not a valid phone number. Please check your input.')),
    SanerValidator('saneIsEmail', '^'+EMAIL_RE,
                   title='', description='',
                   errmsg=_(u'is not a valid email address. Please check you have entered a correct email.')),
]

