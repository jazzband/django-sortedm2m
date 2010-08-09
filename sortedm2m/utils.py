from uuid import uuid4
from django.db.models import get_model
from django.db.models.signals import class_prepared


def get_model_label(model, app):
    if isinstance(model, basestring):
        if u'.' not in model:
            return u'%s.%s' % (app, model)
        return model
    return u'%s.%s' % (model._meta.app_label, model._meta.object_name)


def execute_after_model_is_loaded(model, func, args=None, kwargs=None, signal=class_prepared):
    '''
    Execute ``func`` after ``class_prepared`` signal for ``model`` was fired.
    ``model`` is a string referencing a model like: ``Eauth.user"``. If the
    signal was already fired the function is executed right now.

    ``func`` gets passed the model class as first argument.
    '''
    args = args or ()
    kwargs = kwargs or {}
    model_class = get_model(*model.split('.'))

    if model_class is None:
        def signal_receiver(sender, **signal_args):
            model_label = '%s.%s' % (sender._meta.app_label, sender._meta.object_name)
            if model_label == model:
                func(sender, *args, **kwargs)
        signal.connect(signal_receiver, weak=False)
    else:
        func(model_class, *args, **kwargs)
