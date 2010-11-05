
def patched_EmptyValidator_call(self, value, *args, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        request = getattr(instance, 'REQUEST', None)
        if request and request.form:
            if 'kssValidateField' in request.steps:
                request.form[ request.form.get('fieldname') ] = request.form.get('value')

    return self._old___call__(value, *args, **kwargs)

