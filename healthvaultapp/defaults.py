from django.conf import settings


HEALTHVAULT_APP_ID = None
"""HEALTHVAULT_APP_ID = None
The UUID of your application, assigned by HealthVault when you create your
account at the `Application Configuration Center
<http://msdn.microsoft.com/en-us/healthvault/jj127439>`.
"""


HEALTHVAULT_PUBLIC_KEY = None
"""
Your application's public key (of type ``long``). In order to communicate with
HealthVault, you need a signed certificate (it can be self-signed) uploaded to
HealthVault for your application.

See the `python-healthvault <https://github.com/orcasgit/python-fitbit>`
documentation for information on creating public and private keys.
"""


HEALTHVAULT_PRIVATE_KEY = None
"""
Your application's private key (of type ``long``). In order to communicate
with HealthVault, you need a signed certificate (it can be self-signed)
uploaded to HealthVault for your application.

See the `python-healthvault <https://github.com/orcasgit/python-fitbit>`
documentation for information on creating public and private keys.
"""


HEALTHVAULT_THUMBPRINT = None
"""
Your public key's thumbprint - the Application Configuration Center will
display this after you upload your public certificate.
"""


HEALTHVAULT_SERVER = None
"""
The server address at which to reach HealthVault. For example, the
pre-production server is "platform.healthvault-ppe.com" in the United States
and "platform.healthvault-ppe.co.uk" in Europe. For production, drop the "ppe".
"""


HEALTHVAULT_SHELL_SERVER = None
"""
The host name of the HealthVault shell server. For example, the pre-production
shell server is "account.healthvault-ppe.com" in the United States.
"""


HEALTHVAULT_IN_DEVELOPMENT = getattr(settings, 'DEBUG', True)
"""
Set this to False when your HealthVault project is operating in production. It
defaults to :py:data:`settings.DEBUG`.

This setting determines whether to pass a test callback URL to HealthVault. In
production, the shell server will always redirect to the application's
configured ActionURL. For ease of development, this requirement is relaxed in
the pre-production environment.
"""


HEALTHVAULT_AUTHORIZE_REDIRECT = '/'
"""
Where to redirect to after successful completion of HealthVault integration.
"""


HEALTHVAULT_DEAUTHORIZE_REDIRECT = '/'
"""
Where to redirect to after removal of HealthVault credentials.
"""


HEALTHVAULT_DENIED_REDIRECT = '/'
"""
Where to redirect to if user denies us access to their HealthVault account.
"""


HEALTHVAULT_ERROR_TEMPLATE = 'healthvaultapp/error.html'
"""
The template to use when an unavoidable error occurs during HealthVault
integration. This is rendered by the :py:func:`error <healthvaultapp.views.error>`
view.
"""
