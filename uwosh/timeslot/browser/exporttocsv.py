from Products.Five import BrowserView
from Products.Archetypes.utils import contentDispositionHeader

from uwosh.timeslot import timeslotMessageFactory as _

import time

class ExportToCSV(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def exportToCSV(self):
        currentDateTime = time.strftime('%Y%m%d%H%M', time.localtime())
        filename = '%s-%s.csv' % (self.context.Title(), currentDateTime)
        header_value = contentDispositionHeader('attachment', self.context.getCharset(), filename=filename)
        
        self.request.response.setHeader('Content-Disposition', header_value)
        self.request.response.setHeader('Content-Type', 
                                        'text/comma-separated-values;charset=%s' % self.context.getCharset())
        
        return self.context.exportToCSV()
