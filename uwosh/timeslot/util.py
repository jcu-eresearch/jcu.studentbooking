
def explodeCourseIdentifier(course_str, delimiter='-'):
    course = course_str.split(delimiter)
    return { 'courseCode': course[0], 
             'courseYear': course[1],
             'defaultCampus': course[2] }

xyz = '''Dear %s<Given name>,
Thank you, your booking has been successful!
Enrolment Help Session
When: 		%s<Date> at %s<Start Time>
Location: 	<a href="%s">%s<Room Number></a> %s<Location>
What to BRING to the session:
your JCU username and password, and
your Course Enrolment Planner printout (except Study Abroad students)
You will receive a reminder email prior to the session. If you need to change your booking or cancel please go to %s<Plone URL>  You will need to cancel your current session before booking a new time.
We look forward to helping you get started at JCU.
Regards
JCU Enrolment Help'''# % (givenName, sessionDateStr, sessionTimeStr, sessionRoomMapUrl, sessionRoomNumber, sessionLocation, bookingSys
