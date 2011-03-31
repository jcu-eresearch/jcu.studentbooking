import csv
from datetime import datetime

from five import grok
from zope.component.interfaces import ObjectEvent

from uwosh.timeslot import config, util
from uwosh.timeslot.interfaces import IPerson, IPersonCancelledEvent

class PersonCancelledEvent(ObjectEvent):
    """A person cancelled their session"""
    grok.implements(IPersonCancelledEvent)


@grok.subscribe(IPerson, IPersonCancelledEvent)
def personCancelled(person, event):
    csv_log = open(config.EHS_CANCELLATION_LOG, 'a')
    writer = csv.writer(csv_log,
                        quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)

    now = datetime.now()
    session = person.aq_parent
    day = session.aq_parent

    record = [
        now.date().strftime('%Y/%m/%d'),
        now.time().strftime('%H:%M:%S'),
    ]
    record += util.buildCSVRow(day,
                               session,
                               person)
    writer.writerow(record)
    csv_log.close()

