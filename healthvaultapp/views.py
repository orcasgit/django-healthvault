import logging
from urllib import urlencode

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render

from healthvaultlib.healthvault import HealthVaultException

from . import utils
from .models import HealthVaultUser


NEXT_SESSION_KEY = 'healthvault_next'
NEXT_GET_PARAM = 'next'


@login_required
def authorize(request):
    """
    Begins the HealthVault authentication process by redirecting the user to
    a URL at which they can authorize us to access their HealthVault account.

    When the user has finished at the HealthVault site, they will be
    redirected to the :py:func:`healthvaultapp.views.complete` view.

    If NEXT_GET_PARAM is provided in the GET data, it is saved in
    NEXT_SESSION_KEY so the :py:func:`healthvaultapp.views.complete` view can
    redirect the user to that URL after successful authorization.

    URL name:
        `healthvault-authorize`
    """
    # Store redirect URL in the session for after authorization completion.
    next_url = request.GET.get(NEXT_GET_PARAM, None)
    if next_url:
        request.session[NEXT_SESSION_KEY] = next_url
    else:
        request.session.pop(NEXT_SESSION_KEY, None)

    # Microsoft will send a callback to this URL so that we can store
    # authorization credentials.
    callback_url = request.build_absolute_uri(reverse('healthvault-complete'))

    # Build the authorization URL.
    conn = utils.create_connection()
    authorization_url = conn.authorization_url(callback_url)

    return redirect(authorization_url)


@login_required
def complete(request):
    """
    After the user authorizes us, HealthVault sends a callback to this URL so
    that we can complete integration.

    If there was an error, the user is redirected again to the
    :py:func:`healthvaultapp.views.error` view.

    If the authorization was successful, the credentials are stored in a
    HealthVaultUser object, and the user is redirected. If NEXT_SESSION_KEY is
    in the session, the user is redirected to that URL. Otherwise, they are
    redirected to the URL specified by the
    :ref:`HEALTHVAULT_AUTHORIZE_REDIRECT` setting.

    URL name:
        `healthvault-complete`
    """
    logger = logging.getLogger('healthvaultapp.views.complete')

    # Break down the request to get the authorization token.
    token = request.GET.get('wctoken', None)
    if not token:
        logger.error('request.GET = ' + str(request.GET))
        logger.error('wctoken was not provided in the URL.')
        return redirect(reverse('healthvault-error'))

    # Create a connection to retrieve the person_id and record_id.
    conn = utils.create_connection(wctoken=token)
    if not conn.record_id:
        logger.error('Connection did not find a record_id.')
        return redirect(reverse('healthvault-error'))

    # Save the user's authorization information.
    hvuser, created = HealthVaultUser.objects.get_or_create(user=request.user)
    hvuser.record_id = conn.record_id
    hvuser.token = token
    try:
        hvuser.full_clean()
    except ValidationError as e:
        if created:  # Don't create an object, but keep old info if available
            hvuser.delete()
        logger.exception(e)
        return redirect(reverse('healthvault-error'))
    else:
        hvuser.save()

    # Redirect the user to the stored redirect URL or default.
    next_url = request.session.pop(NEXT_SESSION_KEY, None)
    next_url = next_url or utils.get_setting('HEALTHVAULT_AUTHORIZE_REDIRECT')
    return redirect(next_url)


@login_required
def error(request, extra_context=None):
    """
    The user is redirected to this view if we encounter an error while
    acquiring their HealthVault credentials. It removes NEXT_SESSION_KEY from
    the session if it exists, and renders the template defined in the setting
    :ref:`HEALTHVAULT_ERROR_TEMPLATE`. The default template, located at
    *healthvaultapp/error.html*, simply informs the user of the error::

        <html>
            <head>
                <title>HealthVault Authentication Error</title>
            </head>
            <body>
                <h1>HealthVault Authentication Error</h1>

                <p>We encountered an error while attempting to authenticate
                you through HealthVault.</p>
            </body>
        </html>

    You may optionally provide extra context when rendering this view.

    URL name:
        `healthvault-error`
    """
    request.session.pop(NEXT_SESSION_KEY, None)
    return render(request, utils.get_setting('HEALTHVAULT_ERROR_TEMPLATE'),
            extra_context or {})


@login_required
def deauthorize(request):
    """Forget the user's HealthVault credentials.

    If NEXT_GET_PARAM is in the GET data, the user is redirected to that URL.
    Otherwise, they are redirected to the URL defined by the
    :ref:`HEALTHVAULT_DEAUTHORIZE_REDIRECT` setting.

    URL name:
        `healthvault-deauthorize`
    """
    # TODO: is there a way to self-deauthorize from healthvault?
    HealthVaultUser.objects.filter(user=request.user).delete()
    next_url = request.GET.get(NEXT_GET_PARAM, None)
    if not next_url:
        next_url = utils.get_setting('HEALTHVAULT_DEAUTHORIZE_REDIRECT')
    return redirect(next_url)
