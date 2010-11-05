"""Main product initializer
"""

from zope.i18nmessageid import MessageFactory
from uwosh.timeslot import config

from Products.Archetypes import atapi
from Products.CMFCore import utils
from Products.CMFCore.permissions import setDefaultRoles


from Products.validation import validation
from uwosh.timeslot.validators import sanerValidators
for sanerValidator in sanerValidators:
    validation.register(sanerValidator)

#Open up our connection to the database and do it early
from z3c.sqlalchemy import createSAWrapper, Model
from z3c.sqlalchemy.mapper import MappedClassBase
from sqlalchemy.orm import mapper, synonym
from sqlalchemy import Table

class EhsBookingMapper(MappedClassBase): pass

#We're creating our SQLAlchemy wrapper and mapping our table here to the 
#class above.  All fields are our primary key because the view doesn't have
#a primary key defined.  Go Oracle!
wrapper = createSAWrapper(config.EHS_BOOKING_DB_CONNECTION_STRING, name=config.EHS_BOOKING_DB_CONNECTOR)
table = Table(config.EHS_BOOKING_TABLE_NAME, wrapper.metadata, schema=config.EHS_BOOKING_DB_SCHEMA, autoload=True, )
ehs_mapper = mapper(EhsBookingMapper, table, primary_key=table.c._data.values(), properties={
    'stu_id':     synonym('studentNumber', map_column=True),
    'login_id':	  synonym('studentLoginId', map_column=True),
    'crs_cd':     synonym('courseCode', map_column=True),
    'crs_year':   synonym('courseYear', map_column=True),
    'crs_nm':     synonym('abbrevCourseTitle', map_column=True),
    'crs_full_nm':     synonym('courseFullName', map_column=True),
    'faculty_code':    synonym('facultyCode', map_column=True),
    'faculty_name':    synonym('facultyName', map_column=True),
    'campus':     synonym('defaultCampus', map_column=True),
    'surname':    synonym('studentSurname', map_column=True),
    'gvn_name':   synonym('studentGivenName', map_column=True),
    'home_ph':    synonym('daytimeContactNumber', map_column=True),
    'mob_ph':     synonym('mobilePhoneNumber', map_column=True),
    "jcu_email":  synonym("email", map_column=True),
    'pers_email': synonym('personalEmail', map_column=True),
    'intnl_stu':  synonym('isInternational', map_column=True),
    'sanctions':  synonym('sanction', map_column=True),
    'adv_std':    synonym('advancedStanding', map_column=True),
    'no_subjects_enr':synonym('numberSubjectsEnrolled', map_column=True),
})
wrapper.registerMapper(ehs_mapper, name=config.EHS_BOOKING_ABSOLUTE_NAME)


# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

timeslotMessageFactory = MessageFactory('uwosh.timeslot')

def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """

    setDefaultRoles('uwosh.timeslot: Manage Schedule', ())
    setDefaultRoles('uwosh.timeslot: View Schedule', ())

    # Retrieve the content types that have been registered with Archetypes
    # This happens when the content type is imported and the registerType()
    # call in the content type's module is invoked. Actually, this happens
    # during ZCML processing, but we do it here again to be explicit. Of
    # course, even if we import the module several times, it is only run
    # once.

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    # Now initialize all these content types. The initialization process takes
    # care of registering low-level Zope 2 factories, including the relevant
    # add-permission. These are listed in config.py. We use different
    # permissions for each content type to allow maximum flexibility of who
    # can add which content types, where. The roles are set up in rolemap.xml
    # in the GenericSetup profile.

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit('%s: %s' % (config.PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)

    
