import logging
from urllib import urlencode

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, render

from healthvaultlib.healthvault import HealthVaultException

from . import utils
from .models import HealthVaultUser


NEXT_SESSION_KEY = 'healthvault_next'
NEXT_GET_PARAM = 'next'

# TODO - should these be constants in python-healthvault?
# TODO - I don't think these are all-inclusive; need to check the docs
DEAUTHORIZE_TARGET = 'SIGNOUT'
AUTHORIZE_TARGET = 'APPAUTH'


@login_required
def authorize(request):
    """
    Begins the HealthVault authentication process by redirecting the user to
    a URL at which they can authorize us to access their HealthVault account.

    When the user has finished at the HealthVault site, they will be
    redirected to the :py:func:`healthvaultapp.views.complete` view so that we
    can complete the authorization process & redirect the user to the next
    view.

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

    # HealthVault will send a callback to this URL with target=APPAUTH so that
    # we can complete the authorization process.
    callback_url = utils.get_callback_url(request)

    # Get the record id from the existing HealthVaultUser (if it exists) so
    # that we can request authorization for a specific record.
    try:
        hvuser = HealthVaultUser.objects.get(user=request.user)
    except HealthVaultUser.DoesNotExist:
        record_id = None
    else:
        record_id = hvuser.record_id

    # Build the authorization URL.
    conn = utils.create_connection()
    authorization_url = conn.authorization_url(callback_url, record_id)

    return redirect(authorization_url)


@login_required
def deauthorize(request):
    """Removes the user's HealthVault credentials, and redirects them to a
    HealthVault URL that deauthorizes us from accessing HealthVault on the
    user's behalf.

    After the deauthorization is complete, HealthVault will redirect to the
    :py:func:`healthvaultapp.views.complete` view so that we can complete the
    deauthorization process & redirect the user to the next view.

    If NEXT_GET_PARAM is provided in the GET data, it is saved in
    NEXT_SESSION_KEY so  the :py:func:`healthvaultapp.views.complete` view can
    redirect the user to that URL after successful deauthorization.

    If we don't have HealthVault credentials for this user, we short-circuit
    and redirect to either the URL defined in NEXT_GET_PARAM or the
    :ref:`HEALTHVAULT_DEAUTHORIZE_REDIRECT` setting.

    URL name:
        `healthvault-deauthorize`
    """
    next_url = request.GET.get(NEXT_GET_PARAM, None)

    # If the user isn't integrated, shortcut & redirect.
    try:
        hvuser = HealthVaultUser.objects.get(user=request.user)
    except HealthVaultUser.DoesNotExist:
        if not next_url:
            next_url = utils.get_setting('HEALTHVAULT_DEAUTHORIZE_REDIRECT')
        return redirect(next_url)

    # Store redirect URL in the session for after deauthorization completion.
    if next_url:
        request.session[NEXT_SESSION_KEY] = next_url
    else:
        request.session.pop(NEXT_SESSION_KEY, None)

    # HealthVault will send a callback to this URL with target=SIGNOUT so that
    # we can complete the deauthorization process.
    callback_url = utils.get_callback_url(request)

    # Build the deauthorization URL.
    conn = utils.create_connection(wctoken=hvuser.token)
    deauthorization_url = conn.deauthorization_url(callback_url)

    # Delete our copy of the user's data.
    HealthVaultUser.objects.filter(user=request.user).delete()

    return redirect(deauthorization_url)


@login_required
def complete(request):
    """
    URL called by HealthVault after user changes this application's permissions.

    The action that was taken is described by the 'target' get parameter.
    If target == AUTHORIZATION_TARGET, we complete the user's authorization
    and redirect.  If target == DEAUTHORIZATION_TARGET, we complete the user's
    deauthorization and redirect. If the target is not recognized, this view
    returns a 404 response.

    If there was an error, the user is redirected again to the
    :py:func:`healthvaultapp.views.error` view.

    Otherwise, the user is redirected to another view. If NEXT_SESSION_KEY is
    in the session, the user is redirected to that URL. Otherwise, they are
    redirected to the URL specified by the
    :ref:`HEALTHVAULT_AUTHORIZE_REDIRECT` setting.

    URL name:
        `healthvault-complete`
    """
    logger = logging.getLogger('healthvaultapp.views.complete')
    target = request.GET.get('target', None)

    if target == DEAUTHORIZE_TARGET:
        # Re-delete our copy of the user's data, just in case.
        HealthVaultUser.objects.filter(user=request.user).delete()

        # Redirect the user to the stored redirect URL or default.
        next_url = request.session.pop(NEXT_SESSION_KEY, None)
        if not next_url:
            next_url = utils.get_setting('HEALTHVAULT_DEAUTHORIZE_REDIRECT')
        return redirect(next_url)

    elif target == AUTHORIZE_TARGET:
        # Break down the request to get the authorization token.
        token = request.GET.get('wctoken', None)
        if not token:
            logger.error('request.GET = {0}'.format(request.GET))
            logger.error('wctoken was not provided in the URL.')
            return redirect(reverse('healthvault-error'))

        # Create a connection to retrieve the record_id.
        try:
            conn = utils.create_connection(wctoken=token)
        except HealthVaultException as e:
            logger.exception('Error in creating a HealthVault connection: ')
            return redirect(reverse('healthvault-error'))

        # Save the user's authorization information.
        hvuser, created = HealthVaultUser.objects.get_or_create(
                user=request.user)
        hvuser.record_id = conn.record_id
        hvuser.token = token
        try:
            hvuser.full_clean()
        except ValidationError as e:
            if created:  # Keep old info if it is available
                hvuser.delete()
            logger.exception('Error while saving to the database: ')
            return redirect(reverse('healthvault-error'))
        else:
            hvuser.save()

        # Redirect the user to the stored redirect URL or default.
        next_url = request.session.pop(NEXT_SESSION_KEY, None)
        if not next_url:
            next_url = utils.get_setting('HEALTHVAULT_AUTHORIZE_REDIRECT')
        return redirect(next_url)

    else:
        logger.error('Unknown target: {0}'.format(target))
        request.session.pop(NEXT_SESSION_KEY, None)
        raise Http404


@login_required
def error(request, extra_context=None):
    """
    The user is redirected to this view if we encounter an error during
    :py:func:`healthvaultapp.views.complete`. It removes NEXT_SESSION_KEY from
    the session if it exists, and renders the template defined in the setting
    :ref:`HEALTHVAULT_ERROR_TEMPLATE`. The default template, located at
    *healthvaultapp/error.html*, simply informs the user of the error::

        <html>
            <head>
                <title>HealthVault Integration Error</title>
            </head>
            <body>
                <h1>HealthVault Integration Error</h1>

                <p>We encountered an error while processing your HealthVault
                integration.</p>
            </body>
        </html>

    You may optionally provide extra context when rendering this view.

    URL name:
        `healthvault-error`
    """
    request.session.pop(NEXT_SESSION_KEY, None)
    return render(request, utils.get_setting('HEALTHVAULT_ERROR_TEMPLATE'),
            extra_context or {})
