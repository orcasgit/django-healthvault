Settings
========

.. _HEALTHVAULT_APP_ID:

HEALTHVAULT_APP_ID
------------------

You must specify a non-null value for this setting.

.. _HEALTHVAULT_THUMBPRINT:

HEALTHVAULT_THUMBPRINT
----------------------

You must specify a non-null value for this setting.

.. _HEALTHVAULT_PUBLIC_KEY:

HEALTHVAULT_PUBLIC_KEY
----------------------

You must specify a non-null value for this setting.

.. _HEALTHVAULT_PRIVATE_KEY:

HEALTHVAULT_PRIVATE_KEY
-----------------------

You must specify a non-null value for this setting.

.. _HEALTHVAULT_SHELL_SERVER:

HEALTHVAULT_SHELL_SERVER
------------------------

You  must specify a non-null value for this setting.

.. _HEALTHVAULT_AUTHORIZE_REDIRECT:

HEALTHVAULT_AUTHORIZE_REDIRECT
------------------------------

:Default: ``'/'``

The URL which to redirect the user to after successful HealthVault
integration, if no forwarding URL is given in the 'healthvault_next' session
variable.

.. _HEALTHVAULT_DEAUTHORIZE_REDIRECT:

HEATHVAULT_DEAUTHORIZE_REDIRECT
-------------------------------

:Default: ``'/'``

.. _HEALTHVAULT_DENIED_REDIRECT:

HEALTHVAULT_DENIED_REDIRECT
---------------------------

:Default: ``'/'``

.. _HEALTHVAULT_ERROR_TEMPLATE:

HEALTHVAULT_ERROR_TEMPLATE
--------------------------

:Default: ``'healthvaultapp/error.html'``

The template used to report an error integrating the user's account with
HealthVault.
