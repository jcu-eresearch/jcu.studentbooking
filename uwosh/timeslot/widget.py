from Products.Archetypes.Widget import CalendarWidget

class TimeWidget(CalendarWidget):
    _properties = CalendarWidget._properties.copy()
    _properties.update({
        'show_ymd' : False,
        'show_hm' : True,
        'format' : '%I:%M %P'
        })
    
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Basic impl for form processing in a widget"""

        fname = field.getName()
        value = form.get(fname, empty_marker)
        if value is empty_marker:
            return empty_marker
        # If JS support is unavailable, the value
        # in the request may be missing or incorrect
        # since it won't have been assembled from the
        # input components. Instead of relying on it,
        # assemble the date/time from its input components.
        hour = form.get('%s_hour' % fname, '--')
        minute = form.get('%s_minute' % fname, '--')
        ampm = form.get('%s_ampm' % fname, '')
        if (hour != '--') and (minute != '--'):
            value = "%s-%s-%s %s:%s" % ('2000', '01', '01', hour, minute)
            if ampm:
                value = '%s %s' % (value, ampm)
        else:
            value = ''
        if emptyReturnsMarker and value == '':
            return empty_marker
        # stick it back in request.form
        form[fname] = value
        return value, {}
