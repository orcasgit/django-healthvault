from urllib import urlencode

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render

from . import utils
from .models import HealthVaultUser


@login_required
def login(request):
    next_url = request.GET.get('next', None)
    if next_url:
        request.session['healthvault_next'] = next_url
    else:
        request.session.pop('healthvault_next', None)

    server = utils.get_setting('HEALTHVAULT_SHELL_SERVER')
    app_id = utils.get_setting('HEALTHVAULT_APP_ID')
    callback_url = request.build_absolute_uri(reverse('healthvault-complete'))
    target = 'APPAUTH'
    targetqs = urlencode({'appid': app_id, 'redirect': callback_url})
    parameters = urlencode({'target': target, 'targetqs': targetqs})
    url = 'https://{0}/redirect.aspx?{1}'.format(server, parameters)
    return redirect(url)


@login_required
def complete(request):
    token = request.GET.get('wctoken', None)
    if not token:
        return redirect(reverse('healthvault_error'))
    hvuser, _ = HealthVaultUser.objects.get_or_create(user=request.user)
    hvuser.token = token
    hvuser.save()
    next_url = request.session.pop('healthvault_next', None)
    if not next_url:
        next_url = utils.get_setting('HEALTHVAULT_LOGIN_REDIRECT')
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
def logout(request):
    pass
