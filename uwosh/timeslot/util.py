from zope.component import getMultiAdapter
from zope.pagetemplate.interfaces import IPageTemplate

from uwosh.timeslot import config

def explodeCourseIdentifier(course_str, delimiter='-'):
    course = course_str.split(delimiter)
    return dict((config.EHS_UNIQUE_FIELD_COMBO[i],course[i]) for i in range(len(course)))

def buildCourseIdentifier(selection, delimiter='-'):
    '''Our course identifier is used within pages to distinctly
       identify a course based on code, year, and campus.  Other
       factors may need to be included here'''
    return delimiter.join([str(selection[field]) for field in config.EHS_UNIQUE_FIELD_COMBO])

def getFacultyList():
    #Should this come from SMS?
    return config.FACULTY_LIST

def getCampusList():
    #Should this come from SMS?
    return config.CAMPUS_LIST

def getFacultyName(faculty_orgu):
    return getFacultyList().getValue(faculty_orgu)

def getFacultyAbbreviation(faculty_orgu):
    facultyName = getFacultyName(faculty_orgu)
    return facultyName[facultyName.find('(')+1:facultyName.rfind(')')]

def getCampusName(campus):
    return getCampusList().getValue(campus)

def buildCSVRow(day, session, person):
    row = [session.getFacultyAbbreviation(),
           day.getDate(),
           session.getName(),
           session.getTimeRange(),
           session.campus,
           person.crs_status,
           person.stu_id,
           person.crs_cd,
           person.crs_nm,
           person.sprd_code,
           person.crs_year,
           person.campus,
           person.surname,
           person.gvn_name,
           person.home_ph,
           person.mob_ph or '',
           person.jcu_email or '',
           person.pers_email or '',
           person.getSubjectInfo() != '0' and 'Yes' or 'No',
           person.getDifficultyWithEStudent() != '0' and 'Yes' or 'No',
           person.getIntendToApplyForAdvancedStanding() != '0' and 'Yes' or 'No',
           person.getSubmittedApplicationForAdvancedStanding() and 'Yes' \
                                                               or 'No',
           person.adv_std == 'Y' and 'Yes' or 'No',
           person.intnl_stu == 'Y' and 'Yes' or 'No',
           person.sanctions,
           person.no_subjects_enr,
          ]
    return row

#XXX This is a quick workaround for the issue of rendering a custom error
#message on the z3c form and getting the error in the right location.
#By doing this, we don't need to store errors or manually manage them on the
#form.
def render_html(self):
    """Override the default error message renderer to render as raw HTML
    """
    template = getMultiAdapter(
        (self, self.request), IPageTemplate)
    return template(self).replace('&lt;', '<').replace('&gt;', '>')
