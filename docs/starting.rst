Getting Started
===============

Installation
------------

#. Add ``django-healthvault`` to the requirements of your Django project,
   and install it.  Soon it will be installable from PyPI.

#. Add ``healthvaultapp`` to your :py:data:`INSTALLED_APPS` setting.

#. Add the *django-healthvault* URLs to your URL configuration::

    url(r'^healthvault/', include('healthvaultapp.urls')

#. Add the  *django-healthvault* :ref:`required settings <required-settings>`.

#. Customize *django-healthvault* with :ref:`optional settings
   <optional-settings>`.


Usage Overview
--------------

A HealthVault account holder can maintain one or many data stores (herein
called Records). For example, a parent with a HealthVault account may maintain
a personal Record as well as other Records for each of their children. To get
data from a Record, your application must explicitly request access from the
HealthVault account holder. *django-healthvault* helps you retrieve and store
access credentials for your site's users. Each user can be associated with no
more than one HealthVault Record at a time.

To begin the authorization process, direct your user to the
:py:func:`authorize <healthvaultapp.views.authorize>` view. This view will
redirect your user to a HealthVault page at which they can grant your
application access to their HealthVault record.

Once the user grants us access to a HealthVault record, HealthVault redirects
the user back to your application's Action URL, which is defined at the
`Application Configuration Center
<http://msdn.microsoft.com/en-us/healthvault/jj127439>`_. You should configure
your application's Action URL to use the full path to the
:py:func:`complete <healthvaultapp.views.complete>` view. (If
:py:data:`~healthvaultapp.defaults.HEALTHVAULT_IN_DEVELOPMENT` is True, then
we can direct HealthVault to send callbacks this URL. However, in production
HealthVault will always send callbacks to the stored Action URL.) Upon
receiving this confirmation, we complete the authorization process by saving
the access credentials that HealthVault sent us.

Once you have authorization credentials for a user's HealthVault Record, you
can use these credentials to create a
:py:class:`~healthvaultlib.healthvault.HealthVaultConn` to access data from
that user's Record. A :py:class:`~healthvaultlib.healthvault.HealthVaultConn`
requires many configuration parameters, but we provide a shortcut for
providing these in :py:func:`~healthvaultapp.utils.create_connection`. You
need only pass in the `wctoken` and `record_id` associated with your user.
Once you have a :py:class:`~healthvaultlib.healthvault.HealthVaultConn`, you
can call the :py:func:`~healthvaultlib.healthvault.HealthVaultConn.get_things`
method to retrieve data from HealthVault. For more information, see the
documentation for `python-healthvault
<https://github.com/orcasgit/python-healthvault>`_.

When you no longer need access to a particular user's HealthVault Record,
use the :py:class:`deauthorize <healthvaultapp.views.deauthorize>` view to
revoke your application's access credentials to the user's Record.
