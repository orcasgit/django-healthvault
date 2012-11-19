from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from . import defaults


def get_setting(name, use_defaults=True):
    if hasattr(settings, name):
        return getattr(settings, name)
    if use_defaults:
        if hasattr(defaults, name):
            return getattr(defaults, name)
    msg = "{0} must be specified in your settings".format(name)
    raise ImproperlyConfigured(msg)
