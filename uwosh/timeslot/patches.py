from Products.Archetypes.Field import TextField

def patched_EmptyValidator_call(self, value, *args, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        request = getattr(instance, 'REQUEST', None)
        if request and request.form:
            if 'kssValidateField' in request.steps:
                request.form[ request.form.get('fieldname') ] = request.form.get('value')

    return self._old___call__(value, *args, **kwargs)

def patched_TemplatedTextField_get(self, instance, **kwargs):
    text = TextField.get(self, instance, **kwargs)
    raw = kwargs.get("raw", True)

    if raw:
        return text
    else:
        return self._getCooked(instance, text)
