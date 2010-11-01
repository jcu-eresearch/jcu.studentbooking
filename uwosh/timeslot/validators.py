from Products.validation.interfaces.IValidator import IValidator
from Products.validation.i18n import PloneMessageFactory as _
from Products.validation.i18n import recursiveTranslate
from Products.validation.i18n import safe_unicode
import re
from types import StringType

from Products.validation.validators.BaseValidators import EMAIL_RE
from Products.validation.validators.RegexValidator import ignoreRE, RegexValidator

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

sanerValidators = [
    SanerValidator('saneIsPhoneNumber', r'^\d+$', ignore='[\(\)\-\s\+]',
                   title='', description='',
                   errmsg=_(u'is not a valid phone number. Please check your input.')),
    SanerValidator('saneIsEmail', '^'+EMAIL_RE,
                   title='', description='',
                   errmsg=_(u'is not a valid email address. Please check you have entered a correct email.')),
]

