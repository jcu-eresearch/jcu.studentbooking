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

#XXX Remove this when we go to Python 2.5+
def all(iterable):
    for element in iterable:
        if not element:
            return False
    return True
