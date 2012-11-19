from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from healthvaultlib.healthvault import HealthVaultConn

from . import defaults
from .models import HealthVaultUser


def create_connection(wctoken=None, **kwargs):
    """Shortcut to create a HealthVault connection instance.

    Configuration parameters default to those defined in the project settings.
    """
    config = {
        'app_id': get_setting('HEALTHVAULT_APP_ID'),
        'app_thumbprint': get_setting('HEALTHVAULT_THUMBPRINT'),
        'public_key': get_setting('HEALTHVAULT_PUBLIC_KEY'),
        'private_key': get_setting('HEALTHVAULT_PRIVATE_KEY'),
        'server': get_setting('HEALTHVAULT_SERVER'),
        'shell_server': get_setting('HEALTHVAULT_SHELL_SERVER'),
    }
    config.update(kwargs)
    return HealthVaultConn(wctoken=wctoken, **config)


def get_setting(name, use_defaults=True):
    """Retrieves the specified setting from the project settings file.

    If the setting is not found and ``use_defaults`` is ``True``, then the
    default value specified in ``defaults.py`` is used.

    :raises: ``ImproperlyConfigured`` if the setting is not found.
    """
    if hasattr(settings, name):
        return getattr(settings, name)
    if use_defaults:
        if hasattr(defaults, name):
            return getattr(defaults, name)
    msg = "{0} must be specified in your settings".format(name)
    raise ImproperlyConfigured(msg)


def is_integrated(user):
    """Returns ``True`` if we have HealthVault authentication data for the
    user.

    This does not require that the authentication data is valid.

    :param user: A Django user.
    """
    if user.is_authenticated() and user.is_active:
        return HealthVaultUser.objects.filter(user=user).exists()
    return False
