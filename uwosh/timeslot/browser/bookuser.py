from zope.interface import implements, Interface

from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName


from uwosh.timeslot.browser.base import BaseBrowserView
from uwosh.timeslot import timeslotMessageFactory as _

class IBookUserForm(Interface):
    pass


class BookUserForm(BaseBrowserView):
    implements(IBookUserForm)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self, *args, **kwargs):
        self.student_id = None
        self.student_records = None
        self.first_student_record = None

        if self.request.form.get('form.submitted') == '1':

            self.authenticateForm()

            self.student_id = self.request.form.get('studentIdSearch')

            if self.request.form.get('form.button.Submit') == 'Search':

                if self.student_id:
                    self.student_records = self.queryStudentDetails(self.student_id, first=False, as_dict=True, search_student_id=True, search_login_id=True)
                    if self.student_records:
                        self.first_student_record = self.student_records[0]

                if not self.student_records:
                    self.errors['studentIdSearch'] = "A student with this identifier could not be found.  Please search for another."

            elif self.request.form.get('form.button.Submit') == 'Book as this student':
                #Check the selection is actually a student.  We wouldn't want
                #the user attempting to su to an Administrator!
                student_id = self.request.form.get('form.input.studentNumber')
                student_records = self.queryStudentDetails(student_id, first=True, as_dict=True, search_student_id=True, search_login_id=False)

                if student_records and len(student_records) == 1:
                    #Become that user
                    login_id = student_records[0].login_id
                    getToolByName(self.context, 'acl_users').session._setupSession(str(login_id), self.context.REQUEST.RESPONSE)

                    #Redirect back to the booking page
                    self.request.response.redirect(self.context.absolute_url())
                    return

        #Otherwise, we fall through to the default page rendering
        return super(BookUserForm,self).__call__(args, kwargs)

