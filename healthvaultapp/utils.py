import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from healthvaultlib.healthvault import HealthVaultConn, HealthVaultException

from . import defaults
from .models import HealthVaultUser


logger = logging.getLogger(__name__)


def create_connection(wctoken=None, **kwargs):
    """Shortcut to create a HealthVault connection instance.

    Configuration parameters default to those defined in the project settings.

    :raises: :py:exc:`django.core.exceptions.ImproperlyConfigured` if settings
        are unspecified, null/blank, or incorrect.
    :raises: :py:exc:`healthvaultlib.healthvault.HealthVaultException` if
        there is any problem connecting to HealthVault or getting authorized.
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

    for key, value in config.items():
        if not value:
            msg = 'Your {0} cannot be null, and must be explicitly ' \
                    'specified or set in your Django settings.'.format(key)
            raise ImproperlyConfigured(msg)

    try:
        conn = HealthVaultConn(wctoken=wctoken, **config)
    except ValueError as e:
        logger.error(e)
        msg = 'Public and private keys should be long values: ' \
                '{0}'.format(e.message)
        raise ImproperlyConfigured(msg)
    except HealthVaultException as e:
        logger.error(e)
        raise e
    return conn


def get_setting(name, use_defaults=True):
    """Retrieves the specified setting from the project settings file.

    If the setting is not found and ``use_defaults`` is ``True``, then the
    default value specified in ``defaults.py`` is used.

    :raises: :py:exc:`django.core.exceptions.ImproperlyConfigured` if the
        setting is not found.
    """
    if hasattr(settings, name):
        return getattr(settings, name)
    elif use_defaults:
        if hasattr(defaults, name):
            return getattr(defaults, name)
    msg = '{0} must be specified in your settings'.format(name)
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


def get_callback_url(request):
    """
    Returns the callback url that HealthVault should use after the user makes
    changes to this application's permissions.

    If this project is running in production, HealthVault will always callback
    to the URL defined in the application's ActionURL. Since an error may
    occur if an alternative callback is provided, we return None.
    """
    if get_setting('HEALTHVAULT_IN_DEVELOPMENT'):
        return request.build_absolute_uri(reverse('healthvault-complete'))
    return None
