"""Common configuration constants
"""

from App.config import getConfiguration
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.Archetypes.atapi import DisplayList
from collective.templateengines.backends.jinja import Engine

PROJECTNAME = 'uwosh.timeslot'

ehs_zope_config = getConfiguration().product_config[PROJECTNAME]

EHS_BOOKING_DB_USER = ehs_zope_config.get('ehs-booking-db-user', 'ehs')
EHS_BOOKING_DB_PASSWORD = ehs_zope_config.get('ehs-booking-db-password', 'ehs')
EHS_BOOKING_DB_CONNECTOR = 'jcu.studentbooking.ehs_booking'
EHS_BOOKING_DB_CONNECTION_STRING = \
        'oracle+cx_oracle://%s:%s@host.jcu.edu.au:1234/database' % \
        (EHS_BOOKING_DB_USER, EHS_BOOKING_DB_PASSWORD)
EHS_BOOKING_DB_SCHEMA = 'SCHEMA'
EHS_BOOKING_TABLE_NAME = 'EHS_BOOKING'
EHS_BOOKING_ABSOLUTE_NAME = EHS_BOOKING_TABLE_NAME+'.'+EHS_BOOKING_DB_SCHEMA

EHS_BOOKING_COURSE_IDENTIFIER = "EHS_BOOKING_COURSE_IDENTIFIER"

EHS_UNIQUE_FIELD_COMBO = ['stu_id',
                          'ssp_no',
                          'ssp_att_no',]

EHS_TEMPLATING_ENGINE = Engine()
SYNTAX_ERROR = 'Syntax'
EVALUATION_ERROR = 'Evaluation'

#We may want to calculate these from an SQL call...
FACULTIES = (
    ("6100", "Faculty of Law, Business and the Creative Arts (FLBCA)"),
    ("6200", "Faculty of Medicine, Health and Molecular Sciences (FMHMS)"),
    ("6600", "Faculty of Science and Engineering (FSE)"),
    ("6700", "Faculty of Arts, Education and Social Sciences (FAESS)"),
    ("6000", "Non-faculty (NF)"),
)
FACULTY_TERMS = [SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in FACULTIES]
FACULTY_LIST = DisplayList(FACULTIES)
FACULTY_VOCABULARY = SimpleVocabulary(FACULTY_TERMS)

CAMPUSES = (
    ("TSV", "Townsville"),
    ("CNS", "Cairns"),
#    ("MKY", "Mackay"),
#    ("ISA", "Mt Isa"),
#    ("TIS", "Thursday Island"),
)
CAMPUS_TERMS = [ SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in CAMPUSES]
CAMPUS_LIST = DisplayList(CAMPUSES)
CAMPUS_VOCABULARY = SimpleVocabulary(CAMPUS_TERMS)

SESSION_CLOSED_STATE = 'closed'
SESSION_CLOSE_WF_ACTION = 'close'
SESSION_OPEN_STATE = 'open'
SESSION_OPEN_WF_ACTION = 'open'


EHS_CONFIRMATION_EMAIL = 'CONFIRMATION_EMAIL'
EHS_REMINDER_EMAIL = 'REMINDER_EMAIL'
EHS_CANCELLATION_EMAIL = 'CANCELLATION_EMAIL'
EHS_EMAIL_TYPES = { EHS_CONFIRMATION_EMAIL:
                              { 'subject': 'Booking Confirmation',
                                'bodyField': 'confirmationEmailBody'},
                    EHS_REMINDER_EMAIL:
                              { 'subject': 'Enrolment Help Session Reminder',
                                'bodyField': 'reminderEmailBody'},
                    EHS_CANCELLATION_EMAIL:
                              { 'subject': 'Cancellation Confirmation',
                                'bodyField': 'cancellationEmailBody'},
                  }

#Convert our dictionary over to our common vocabulary format
_ehs_email_types = [(type, EHS_EMAIL_TYPES[type]['subject']) for type in EHS_EMAIL_TYPES]
#Turn our common vocab format into something suitable for zope forms
EHS_NOTIFICATION_TERMS = [SimpleTerm(value=pair[0], token=pair[0], title=pair[1]) for pair in _ehs_email_types]
EHS_NOTIFICATION_VOCABULARY = SimpleVocabulary(EHS_NOTIFICATION_TERMS)

EHS_CANCELLATION_LOG = ehs_zope_config.get('ehs-cancellation-log',
                                           '/tmp/cancellations.log')

EHS_CSV_EXPORT_FORMAT = \
    ['Faculty',
     'Day',
     'Session Name',
     'Time',
     'Session Campus',
     'Status',
     'Student Number',
     'Course Code',
     'Abbrev Course Title',
     'Study Period',
     'Commencement Year',
     'Default Campus',
     'Student Surname',
     'Student Given Name',
     'Daytime Contact',
     'Mobile Number',
     'Email',
     'Personal Email',
     'Subjects',
     'eStudent',
     'Advanced Standing?',
     'AS Submitted',
     'AS Approved?',
     'International',
     'Sanction',
     'Subjects Enrolled']

SORT_ORDER_VOCABULARY = SimpleVocabulary.fromValues(EHS_CSV_EXPORT_FORMAT)

EHS_CANCELLATION_LOG_CSV_FORMAT = \
    ['Cancellation Date',
     'Cancellation Time',
    ] + EHS_CSV_EXPORT_FORMAT

ADD_PERMISSIONS = {
    'Person': 'uwosh.timeslot: Add Person',
    'Time Slot': 'uwosh.timeslot: Add Time Slot',
    'Day': 'uwosh.timeslot: Add Day',
    'Signup Sheet': 'uwosh.timeslot: Add Signup Sheet',
}
