"""Main product initializer
"""
import os, csv
from zope.i18nmessageid import MessageFactory
from Products.Archetypes import atapi
from Products.CMFCore import utils
from Products.CMFCore.permissions import setDefaultRoles
from Products.validation import validation

from uwosh.timeslot.validators import sanerValidators
from uwosh.timeslot import config

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
ehs_mapper = mapper(EhsBookingMapper, table, primary_key=table.c._data.values(), properties={})
wrapper.registerMapper(ehs_mapper, name=config.EHS_BOOKING_ABSOLUTE_NAME)

#Create our cancellations file with headings if it doesn't exist already
if not os.path.exists(config.EHS_CANCELLATION_LOG):
    csv_log = open(config.EHS_CANCELLATION_LOG, 'a')
    writer = csv.writer(csv_log,
                        quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)
    writer.writerow(config.EHS_CANCELLATION_LOG_CSV_FORMAT)
    csv_log.close()


#
## Define a message factory for when this product is internationalised.
## This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

timeslotMessageFactory = MessageFactory('uwosh.timeslot')

def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """

    setDefaultRoles('jcu.booking: Manage bookings', ())
    setDefaultRoles('jcu.booking: Book another user in', ())
    setDefaultRoles('jcu.booking: View all bookings', ())

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


