import logging
from urllib import urlencode

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, render

from healthvaultlib.exceptions import HealthVaultException
from healthvaultlib.targets import ApplicationTarget

from . import utils
from .models import HealthVaultUser


KEEP_GET_PARAM = 'keep'
NEXT_SESSION_KEY = 'healthvault_next'
NEXT_GET_PARAM = 'next'


@login_required
def authorize(request):
    """
    Begins the HealthVault integration process by redirecting the logged-in
    user to a HealthVault URL where they can authorize our application to
    access their HealthVault account data.

    Unless request.GET['keep'] = False, if we have pre-existing access
    credentials for the user we request access to the specific record that
    they previously granted us access to.

    After the user finishes at the HealthVault site, they will be redirected
    to the :py:func:`~healthvaultapp.views.complete` view so that we can
    complete the authorization process & redirect the user to the next page.
    If request.GET['next'] is provided, it is saved in the 'healthvault_next'
    session key so the :py:func:`~healthvaultapp.views.complete` view can
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

    # HealthVault will send a callback to this URL so that we can complete the
    # authorization process.
    callback_url = utils.get_callback_url(request)

    # Get the record_id from the existing HealthVaultUser (if it exists) so
    # that we can request authorization for a specific record.
    keep = request.GET.get(KEEP_GET_PARAM, True)
    record_id = None
    if keep:
        try:
            hvuser = HealthVaultUser.objects.get(user=request.user)
        except HealthVaultUser.DoesNotExist:
            pass
        else:
            record_id = hvuser.record_id

    # Build the authorization URL to which we redirect the user.
    conn = utils.create_connection(record_id=record_id)
    authorization_url = conn.authorization_url(callback_url)

    return redirect(authorization_url)


@login_required
def deauthorize(request):
    """
    Removes our record of the user's HealthVault credentials, and redirects
    them to a HealthVault URL that deauthorizes us from accessing HealthVault
    on the user's behalf.

    After the deauthorization is complete, HealthVault will redirect to the
    :py:func:`~healthvaultapp.views.complete` view so that we can complete the
    deauthorization process & redirect the user to the next page. If
    request.GET['next'] is provided, it is saved in the 'healthvault_next'
    session key so  the :py:func:`healthvaultapp.views.complete` view can
    redirect the user to that URL after successful deauthorization.

    If we don't have HealthVault credentials for this user, we short-circuit
    and redirect to either the URL defined in request.GET['next'] or the
    :py:data:`~healthvaultapp.defaults.HEALTHVAULT_DEAUTHORIZE_REDIRECT`
    setting.

    URL name:
        `healthvault-deauthorize`
    """
    next_url = request.GET.get(NEXT_GET_PARAM, None)

    # If the user isn't integrated, shortcut & redirect.
    if not utils.is_integrated(request.user):
        if not next_url:
            next_url = utils.get_setting('HEALTHVAULT_DEAUTHORIZE_REDIRECT')
        return redirect(next_url)

    # Store redirect URL in the session for after deauthorization completion.
    if next_url:
        request.session[NEXT_SESSION_KEY] = next_url
    else:
        request.session.pop(NEXT_SESSION_KEY, None)

    # HealthVault will send a callback to this URL so that we can complete the
    # deauthorization process.
    callback_url = utils.get_callback_url(request)

    # Build the deauthorization URL.
    conn = utils.create_connection()
    deauthorization_url = conn.deauthorization_url(callback_url)

    # Delete our copy of the user's data.
    HealthVaultUser.objects.filter(user=request.user).delete()

    return redirect(deauthorization_url)


@login_required
def complete(request):
    """
    Callback URL called by HealthVault's Shell Redirect interface. Your
    application's ActionURL must be set to this URL when your application is
    in production.

    The action that was taken is described by the request.GET['target'].
    We handle several possible targets:

        ApplicationTarget.APP_AUTH_REJECT
            The user declined to grant our application access to their data.
            We remove their HealthVault credentials and redirect them to the
            URL defined in the :py:data:`~healthvaultapp.defaults.HEALTHVAULT_DENIED_REDIRECT`
            setting.

        ApplicationTarget.APP_AUTH_SUCCESS, ApplicationTarget.SELECTED_RECORD_CHANGED
            The user successfully granted us access to their HealthVault
            record. SELECTEDRECORDCHANGED is the same as APPAUTHSUCCESS,
            except that the user granted us access to a different record than
            before. We overwrite any existing credentials with record and the
            access token received in the request, and redirect to the URL
            defined in the 'healthvault_next' session key, or the default URL
            defined in the :py:data:`~healthvaultapp.defaults.HEALTHVAULT_AUTHORIZE_REDIRECT`
            setting.

        ApplicationTarget.SIGN_OUT
            We no longer have access to the user's HealthVault record. We
            delete their HealthVault credentials, and redirect to the URL
            defined in the 'healthvault_next' session key, or the default URL
            defined in the :py:data:`~healthvaultapp.defaults.HEALTHVAULT_DEAUTHORIZE_REDIRECT`
            setting.

    If there is an unavoidable error during the completion process, the user
    is redirected to the :py:func:`~healthvaultapp.views.error` view.

    URL name:
        `healthvault-complete`
    """
    logger = logging.getLogger('healthvaultapp.views.complete')
    target = request.GET.get('target', None)

    # The user declined to grant our application access.
    if target == ApplicationTarget.APP_AUTH_REJECT:
        HealthVaultUser.objects.filter(user=request.user).delete()

        # Redirect the user to the default denial URL.
        request.session.pop(NEXT_SESSION_KEY, None)  # Clear the session key.
        return redirect(utils.get_setting('HEALTHVAULT_DENIED_REDIRECT'))

    # Complete the authorization process.
    elif (target == ApplicationTarget.APP_AUTH_SUCCESS or
            target == ApplicationTarget.SELECTED_RECORD_CHANGED):
        # Break down the request to get the authorization token.
        token = request.GET.get('wctoken', None)
        if not token:
            logger.error('request.GET = {0}'.format(request.GET))
            logger.error('wctoken was not provided in the URL.')
            return redirect(reverse('healthvault-error'))

        # Create a connection to retrieve the record_id.
        try:
            conn = utils.create_connection(wctoken=token)
        except HealthVaultException:
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

    # Complete the deauthorization process.
    if target == ApplicationTarget.SIGN_OUT:
        # Re-delete our copy of the user's data, just in case.
        HealthVaultUser.objects.filter(user=request.user).delete()

        # Redirect the user to the stored redirect URL or default.
        next_url = request.session.pop(NEXT_SESSION_KEY, None)
        if not next_url:
            next_url = utils.get_setting('HEALTHVAULT_DEAUTHORIZE_REDIRECT')
        return redirect(next_url)

    elif target in ApplicationTarget.all_targets():
        request.session.pop(NEXT_SESSION_KEY, None)
        raise Exception('Unhandled target: {0}'.format(target))

    else:
        request.session.pop(NEXT_SESSION_KEY, None)
        raise Exception('Unknown target: {0}'.format(target))


@login_required
def error(request, extra_context=None):
    """
    The user is redirected to this view if we encounter an error during
    :py:func:`~healthvaultapp.views.complete`. It removes NEXT_SESSION_KEY from
    the session if it exists, and renders the template defined in the
    :py:data:`~healthvaultapp.defaults.HEALTHVAULT_ERROR_TEMPLATE` setting.
    The default template, located at *healthvaultapp/error.html*, simply
    informs the user of the error::

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
