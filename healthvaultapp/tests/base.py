from mock import patch
import random
import string
from urllib import urlencode, splitquery

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from healthvaultapp.models import HealthVaultUser


class MockHealthVaultConnection(object):

    def __init__(self, record_id=None, auth_url=None, **kwargs):
        self.record_id = record_id
        self.auth_url = auth_url

    def authorization_url(self, callback_url):
        return self.auth_url


class HealthVaultTestBase(TestCase):
    TEST_SERVER = 'http://testserver'

    def setUp(self):
        self.record_id = '12345678-1234-1234-1234-123456789012'
        self.authorization_url = '/test'
        self.token = 'testtoken'

        self.username = self.random_string(25)
        self.password = self.random_string(25)
        self.user = self.create_user(username=self.username,
                password=self.password)
        self.hvuser = self.create_healthvault_user(user=self.user)

        self.client.login(username=self.username, password=self.password)

    def random_string(self, length=255, extra_chars=''):
        chars = string.letters + extra_chars
        return ''.join([random.choice(chars) for i in range(length)])

    def random_email(self, length=25, domain=None):
        username = self.random_string(length)
        domain = domain or self.random_string(10) + '.com'
        return '{0}@{1}'.format(username, domain)

    def create_user(self, username=None, email=None, password=None, **kwargs):
        username = username or self.random_string(25)
        email = email or self.random_email()
        password = password or self.random_string(25)
        user = User.objects.create_user(username, email, password)
        User.objects.filter(pk=user.pk).update(**kwargs)
        return User.objects.get(pk=user.pk)

    def create_healthvault_user(self, **kwargs):
        defaults = {
            'user': kwargs.pop('user', self.create_user()),
            'record_id': self.random_string(25),
            'token': self.random_string(25),
        }
        defaults.update(kwargs)
        return HealthVaultUser.objects.create(**defaults)

    def assertRedirectsNoFollow(self, response, url, use_params=True,
            status_code=302):
        """
        Workaround to test whether a response redirects to another URL,
        without loading the page at that URL.

        If the URL starts with '/', the test server name will be prepended to
        the URL before checking for redirect.

        If use_params=False, the method will strip the GET parameters from
        response location before checking whether it was redirected to the
        specified URL.
        """
        self.assertEqual(response.status_code, status_code)
        if url.startswith('/'):
            url = self.TEST_SERVER + url
        response_url = response['location']
        if not use_params:
            response_url = splitquery(response_url)[0]
        self.assertEqual(response_url, url)

    def _get(self, url_name=None, url_kwargs=None, get_params=None, **kwargs):
        """
        Retrieves a URL built using a name and URL kwargs, plus GET parameters
        if provided.
        """
        url_name = url_name or self.url_name
        url = reverse(url_name, kwargs=url_kwargs)  # Base URL.
        if get_params:
            url += '?' + urlencode(get_params)  # Add GET parameters.
        return self.client.get(url, **kwargs)

    def _set_session_vars(self, **kwargs):
        session = self.client.session
        for key, value in kwargs.items():
            session[key] = value
        try:
            session.save()  # Only available on authenticated sessions.
        except AttributeError:
            pass

    def _del_session_vars(self, *args):
        session = self.client.session
        for arg in args:
            session.pop(arg, None)

    @patch('healthvaultapp.utils.HealthVaultConn')
    def _mock_connection_get(self, conn=None, conn_kwargs=None, **kwargs):
        """
        Retrieves the requested information, using a mock object in place of
        healthvaultlib.HealthVaultConnection.
        """
        defaults = {
            'record_id': self.record_id,
            'auth_url': self.authorization_url,
        }
        defaults.update(conn_kwargs or {})
        conn.return_value = MockHealthVaultConnection(**defaults)
        return self._get(**kwargs)
