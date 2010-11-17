from uwosh.timeslot import config

def explodeCourseIdentifier(course_str, delimiter='-'):
    course = course_str.split(delimiter)
    return { 'courseCode': course[0], 
             'courseYear': course[1],
             'defaultCampus': course[2] }

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

