
def explodeCourseIdentifier(course_str, delimiter='-'):
    course = course_str.split(delimiter)
    return { 'courseCode': course[0], 
             'courseYear': course[1],
             'defaultCampus': course[2] }
