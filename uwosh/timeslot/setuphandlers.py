import logging
from uwosh.timeslot.config import PROJECTNAME 

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

