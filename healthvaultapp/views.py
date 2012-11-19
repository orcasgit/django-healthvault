from urllib import urlencode

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render

from . import utils
from .models import HealthVaultUser


@login_required
def authorize(request):
    """
    Begins the HealthVault authentication process by redirecting the user to
    a URL at which they can authorize us to access their HealthVault account.

    When the user has finished at the HealthVault site, they will be
    redirected to the :py:func:`healthvaultapp.views.complete` view.

    If 'next' is provided in the GET data, it is saved in the session so the
    :py:func:`healthvaultapp.views.complete` view can redirect the user to
    that URL upon successful authorization.

    URL name:
        `healthvault-authorize`
    """
    # Store the redirect URL in the session for after authorization completion.
    next_url = request.GET.get('next', None)
    if next_url:
        request.session['healthvault_next'] = next_url
    else:
        request.session.pop('healthvault_next', None)

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
    `healthvault-error` view.

    If the authorization was successful, the credentials are stored for us to
    use later, and the user is redirected. If 'healthvault_next' is in the
    request session, the user is redirected to that URL. Otherwise, they are
    redirected to the URL specified by the setting
    :ref:`HEALTHVAULT_AUTHORIZE_REDIRECT`.

    URL name:
        `healthvault-complete`
    """
    # Break down the request to get authorization data.
    token = request.GET.get('wctoken', None)
    if not token:
        request.session.pop('healthvault_next', None)
        return redirect(reverse('healthvault-error'))

    # Save the user's authorization information.
    hvuser, _ = HealthVaultUser.objects.get_or_create(user=request.user)
    hvuser.token = token
    hvuser.save()

    # Redirect the user to the stored redirect URL or default.
    next_url = request.session.pop('healthvault_next', None)
    if not next_url:
        next_url = utils.get_setting('HEALTHVAULT_AUTHORIZE_REDIRECT')
    return redirect(next_url)


@login_required
def error(request, extra_context=None):
    """
    The user is redirected to this view if we encounter an error while
    acquiring their HealthVault credentials. It renders the template defined
    in the setting :ref:`HEALTHVAULT_ERROR_TEMPLATE`. The default template,
    located at *healthvaultapp/error.html*, simply informs the user of the
    error::

        <html>
            <head>
                <title>HealthVault Authentication Error</title>
            </head>
            <body>
                <h1>HealthVault Authentication Error</h1>

                <p>We encountered an error while attempting to authenticate you
                through HealthVault.</p>
            </body>
        </html>

    You may optionally provide extra context when rendering this view.

    URL name:
        `healthvault-error`
    """
    return render(request, utils.get_setting('HEALTHVAULT_ERROR_TEMPLATE'),
            extra_context or {})


@login_required
def deauthorize(request):
    """Forget the user's HealthVault credentials.

    If the request has a `next` parameter, the user is redirected to that URL.
    Otherwise, they are redirected to the URL defined by the setting
    :ref:`HEALTHVAULT_DEAUTHORIZE_REDIRECT`.

    URL name:
        `healthvault-deauthorize`
    """
    # TODO: is there a way to self-deauthorize from healthvault?
    HealthVaultUser.objects.filter(user=request.user).delete()
    next_url = request.GET.get('next', None) or utils.get_setting(
            'HEALTHVAULT_DEAUTHORIZE_REDIRECT')
    return redirect(next_url)
