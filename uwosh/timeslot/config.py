"""Common configuration constants
"""

from Products.Archetypes.atapi import DisplayList

PROJECTNAME = 'uwosh.timeslot'

EHS_BOOKING_DB_CONNECTOR = 'jcu.studentbooking.ehs_booking'
EHS_BOOKING_DB_CONNECTION_STRING = 'oracle+cx_oracle://ehs:ehs@corp1db.jcu.edu.au:1729/corp'
EHS_BOOKING_DB_SCHEMA = 'IF_SM'
EHS_BOOKING_TABLE_NAME = 'EHS_BOOKING'
EHS_BOOKING_ABSOLUTE_NAME = EHS_BOOKING_TABLE_NAME+'.'+EHS_BOOKING_DB_SCHEMA

EHS_BOOKING_COURSE_IDENTIFIER = "EHS_BOOKING_COURSE_IDENTIFIER"

#We may want to calculate these from an SQL call...
FACULTY_LIST = DisplayList((
    ("6100", "Faculty of Law, Business and the Creative Arts"),
    ("6200", "Faculty of Medicine, Health and Molecular Sciences"),
    ("6600", "Faculty of Science and Engineering"),
    ("6700", "Faculty of Arts, Education and Social Sciences"),
    ("6000", "Non-faculty"),
))
CAMPUS_LIST = DisplayList((
    ("TSV", "Townsville"),
    ("CNS", "Cairns"),
    ("MKY", "Mackay"),
    ("ISA", "Mt Isa"),
    ("TIS", "Thursday Island"),
))

ADD_PERMISSIONS = {
    'Person': 'uwosh.timeslot: Add Person',
    'Time Slot': 'uwosh.timeslot: Add Time Slot',
    'Day': 'uwosh.timeslot: Add Day',
    'Signup Sheet': 'uwosh.timeslot: Add Signup Sheet',
}
