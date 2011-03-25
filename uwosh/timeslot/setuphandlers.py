import logging

from Products.CMFCore.utils import getToolByName
from plone.app.workflow.remap import remap_workflow

from uwosh.timeslot.config import PROJECTNAME

PROFILE_ID = 'profile-uwosh.timeslot:default'

def setupVarious(context):
    """Import step for configuration that is not handled in xml files.
    """

    # Only run step if a flag file is present
    if context.readDataFile(PROJECTNAME+'_various.txt') is None:
        return

    logger = context.getLogger(PROJECTNAME)
    site = context.getSite()
    fields = ['getDate',
              'getStartTime',
              'getEndTime',
              'getFaculty',
              ]
    site.portal_catalog.manage_reindexIndex(ids=fields)
    logger.info("Reindexing EHS booking session content.")

def upgrade_timeslot_workflow(context, logger=None):

    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('uwosh.timeslot')

    #Run the workflow setup
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'workflow')

    remap_workflow(context,
                   type_ids=('Day', 'Time Slot'),
                   chain='(Default)',
                   state_map={'hidden': 'private'}
                  )

    remap_workflow(context,
                   type_ids=('Day', 'Time Slot'),
                   chain=('uwosh_timeslot_hidden_workflow',),
                   state_map={'private': 'open',
                              'pending': 'open',
                              'published': 'open'}
                  )
    return
