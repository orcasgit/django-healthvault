from urllib import urlencode

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render

from . import utils
from .models import HealthVaultUser


@login_required
def authorize(request):
    # Store the redirect URL in the session for after authorization completion
    next_url = request.GET.get('next', None)
    if next_url:
        request.session['healthvault_next'] = next_url
    else:
        request.session.pop('healthvault_next', None)

    # Microsoft will send a callback to this URL so that we can store
    # authorization credentials.
    callback_url = request.build_absolute_uri(reverse('healthvault-complete'))

    # Build the authorization URL.
    server = utils.get_setting('HEALTHVAULT_SHELL_SERVER')
    app_id = utils.get_setting('HEALTHVAULT_APP_ID')
    target = 'APPAUTH'
    targetqs = urlencode({'appid': app_id, 'redirect': callback_url})
    params = urlencode({'target': target, 'targetqs': targetqs})
    authorization_url = 'https://{0}/redirect.aspx?{1}'.format(server, params)

    return redirect(authorization_url)


@login_required
def complete(request):
    token = request.GET.get('wctoken', None)
    if not token:
        request.session.pop('healthvault_next', None)
        return redirect(reverse('healthvault_error'))
    hvuser, _ = HealthVaultUser.objects.get_or_create(user=request.user)
    hvuser.token = token
    hvuser.save()
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
    # TODO: is there a way to self-deauthorize from healthvault?
    HealthVaultUser.objects.filter(user=request.user).delete()
    next_url = request.GET.get('next', None) or utils.get_setting(
            'HEALTHVAULT_DEAUTHORIZE_REDIRECT')
    return redirect(next_url)
