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
            
            self.student_id = self.request.form.get('studentIdSearch')

            if self.request.form.get('form.button.submit') == 'Search':

                if self.student_id:
                    self.student_records = self.queryStudentDetails(self.student_id, first=False, as_dict=True, use_student_id=True)
                    if self.student_records:
                        self.first_student_record = self.student_records[0]
                
                if not self.student_records:
                    self.errors['studentIdSearch'] = "This student ID could not be found.  Please search for another."

            elif self.request.form.get('form.button.submit') == 'Book as this student':
                #Check the selection is actually a student.  We wouldn't want
                #the user attempting to su to an Administrator!
                student_id = self.request.form.get('form.input.studentNumber')
                student_records = self.queryStudentDetails(student_id, first=True, as_dict=True, use_student_id=True)

                if student_records and len(student_records) == 1:
                    #Become that user
                    studentLoginId = student_records[0].studentLoginId
                    getToolByName(self.context, 'acl_users').session.setupSession(str(studentLoginId), self.context.REQUEST.RESPONSE)      

                    #Redirect back to the booking page
                    self.request.response.redirect(self.context.absolute_url())
                    return

        #Otherwise, we fall through to the default page rendering 
        return super(BookUserForm,self).__call__(args, kwargs)

