from zope import schema
from zope.interface import Interface
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from five.formlib import formbase

from uwosh.timeslot.interfaces import *

# Begin ugly hack. It works around a ContentProviderLookupError: plone.htmlhead error caused by Zope 2 permissions.
#
# Source: http://athenageek.wordpress.com/2008/01/08/contentproviderlookuperror-plonehtmlhead/
# Bug report: https://bugs.launchpad.net/zope2/+bug/176566
#

def _getContext(self):
    self = self.aq_parent
    while getattr(self, '_is_wrapperish', None):
        self = self.aq_parent
    return self    
            
ZopeTwoPageTemplateFile._getContext = _getContext

# End ugly hack.

class IRemoveAllPeople(Interface):
    heading = schema.Text(title=u'Would you really like to remove all the people from this signup sheet?',
                          description=u'Doing so will remove anyone who is signed up or on the waiting list for \
                                        this signup sheet.', required=False, readonly=True)

class RemoveAllPeopleForm(formbase.PageForm):
    form_fields = form.FormFields(IRemoveAllPeople)
    
    @form.action('Remove All People')
    def action_remove_all_people(self, action, data):
        self.context.removeAllPeople()
        self.request.response.redirect(self.context.absolute_url())
   
    @form.action('Cancel')
    def action_cancel(self, action, data):
        self.request.response.redirect(self.context.absolute_url())
