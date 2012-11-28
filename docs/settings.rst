Settings
========

django-healthvault uses Django settings for both optional and required
configuration. Default values are provided in :py:mod:`healthvaultapp.defaults`
but can be overridden in your project's settings.

.. _required-settings:

Required Settings
-----------------

.. warning::
    You must provide non-null/non-empty values for these settings in your
    Django project.

.. autodata:: healthvaultapp.defaults.HEALTHVAULT_APP_ID

.. autodata:: healthvaultapp.defaults.HEALTHVAULT_PUBLIC_KEY

.. autodata:: healthvaultapp.defaults.HEALTHVAULT_PRIVATE_KEY

.. autodata:: healthvaultapp.defaults.HEALTHVAULT_THUMBPRINT

.. autodata:: healthvaultapp.defaults.HEALTHVAULT_SERVER

.. autodata:: healthvaultapp.defaults.HEALTHVAULT_SHELL_SERVER

.. _optional-settings:

Optional Settings
-----------------

.. autodata:: healthvaultapp.defaults.HEALTHVAULT_IN_DEVELOPMENT

.. autodata:: healthvaultapp.defaults.HEALTHVAULT_AUTHORIZE_REDIRECT

.. autodata:: healthvaultapp.defaults.HEALTHVAULT_DEAUTHORIZE_REDIRECT

.. autodata:: healthvaultapp.defaults.HEALTHVAULT_DENIED_REDIRECT

.. autodata:: healthvaultapp.defaults.HEALTHVAULT_ERROR_TEMPLATE
