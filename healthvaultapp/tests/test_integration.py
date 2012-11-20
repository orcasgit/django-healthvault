from django.core.urlresolvers import reverse

from healthvaultlib.healthvault import HealthVaultException

from healthvaultapp import utils
from healthvaultapp.models import HealthVaultUser
from healthvaultapp.views import NEXT_GET_PARAM, NEXT_SESSION_KEY

from .base import HealthVaultTestBase


class TestAuthorizeView(HealthVaultTestBase):
    """Tests for healthvaultapp.views.authorize"""
    url_name = 'healthvault-authorize'

    def setUp(self):
        super(TestAuthorizeView, self).setUp()
        self.hvuser.delete()

    def test_anonymous(self):
        """User must be logged in to access Authorize view."""
        self.client.logout()
        response = self._get()
        login_url = utils.get_setting('LOGIN_URL')
        self.assertRedirectsNoFollow(response, login_url, use_params=False)
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_unintegrated(self):
        """Authorize view should redirect to an authorization URL."""
        response = self._mock_connection_get()
        self.assertRedirectsNoFollow(response, self.authorization_url)
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_integrated(self):
        """Should be able to access view even if already authorized."""
        hvuser = self.create_healthvault_user(user=self.user)
        response = self._mock_connection_get()
        self.assertRedirectsNoFollow(response, self.authorization_url)
        self.assertEqual(HealthVaultUser.objects.count(), 1)
        self.assertEqual(HealthVaultUser.objects.get(), hvuser)

    def test_next(self):
        """Authorize view should save the NEXT_GET_PARAM parameter."""
        get_params = {NEXT_GET_PARAM: '/next'}
        response = self._mock_connection_get(get_params=get_params)
        self.assertRedirectsNoFollow(response, self.authorization_url)
        self.assertEqual(self.client.session.get(NEXT_SESSION_KEY, None),
                '/next')
        self.assertEqual(HealthVaultUser.objects.count(), 0)


class TestCompleteView(HealthVaultTestBase):
    """Tests for healthvaultapp.views.complete"""
    url_name = 'healthvault-complete'

    def setUp(self):
        super(TestCompleteView, self).setUp()
        self.hvuser.delete()

    def _get(self, get_params=None, **kwargs):
        if get_params is None:
            get_params = {'wctoken': self.token}
        return super(TestCompleteView, self)._get(get_params=get_params,
                **kwargs)

    def test_anonymous(self):
        """User must be logged in to access Complete view."""
        self.client.logout()
        response = self._get()
        login_url = utils.get_setting('LOGIN_URL')
        self.assertRedirectsNoFollow(response, login_url, use_params=False)
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_unintegrated(self):
        """Complete view should store user's access credentials."""
        response = self._mock_connection_get()
        redirect_url = utils.get_setting('HEALTHVAULT_AUTHORIZE_REDIRECT')
        self.assertRedirectsNoFollow(response, redirect_url)
        self.assertEqual(HealthVaultUser.objects.count(), 1)
        hvuser = HealthVaultUser.objects.get()
        self.assertEqual(hvuser.token, self.token)

    def test_integrated(self):
        """Complete view should overwrite any existing credentials."""
        hvuser = self.create_healthvault_user(user=self.user)
        response = self._mock_connection_get()
        redirect_url = utils.get_setting('HEALTHVAULT_AUTHORIZE_REDIRECT')
        self.assertRedirectsNoFollow(response, redirect_url)
        self.assertEqual(HealthVaultUser.objects.count(), 1)
        hvuser = HealthVaultUser.objects.get()
        self.assertEqual(hvuser.token, self.token)
        self.assertEqual(hvuser.record_id, self.record_id)

    def test_next(self):
        """Complete view should redirect to specified URL, if available."""
        self._set_session_vars(**{NEXT_SESSION_KEY: '/next'})
        response = self._mock_connection_get()
        self.assertRedirectsNoFollow(response, '/next')
        self.assertEqual(HealthVaultUser.objects.count(), 1)
        hvuser = HealthVaultUser.objects.get()
        self.assertEqual(hvuser.token, self.token)

    def test_no_token(self):
        """Complete view should redirect to error if wctoken is not given."""
        response = self._mock_connection_get(get_params={})
        self.assertRedirectsNoFollow(response, reverse('healthvault-error'))
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_healthvault_exception(self):
        """Complete view should redirect to error if connection fails."""
        self.record_id = None
        response = self._mock_connection_get(side_effect=HealthVaultException)
        self.assertRedirectsNoFollow(response, reverse('healthvault-error'))
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_record_id_too_long(self):
        """Complete view should redirect to error if database save fails."""
        self.record_id = 'this_record_id_is_greater_than_thirty_six_chars'
        response = self._mock_connection_get()
        self.assertRedirectsNoFollow(response, reverse('healthvault-error'))
        self.assertEqual(HealthVaultUser.objects.count(), 0)


class TestErrorView(HealthVaultTestBase):
    """Tests for healthvaultapp.views.error"""
    url_name = 'healthvault-error'

    def setUp(self):
        super(TestErrorView, self).setUp()
        self._set_session_vars(**{NEXT_SESSION_KEY: '/next'})

    def test_anonymous(self):
        """User must be logged in to access Error view."""
        self.client.logout()
        response = self._get()
        login_url = utils.get_setting('LOGIN_URL')
        self.assertRedirectsNoFollow(response, login_url, use_params=False)
        self.assertFalse(NEXT_SESSION_KEY in self.client.session)

    def test_integrated(self):
        """Should be able to retrieve error page."""
        response = self._get()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(NEXT_SESSION_KEY in self.client.session)

    def test_unintegrated(self):
        """HealthVault credentials aren't required to access Error view."""
        HealthVaultUser.objects.all().delete()
        response = self._get()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(NEXT_SESSION_KEY in self.client.session)


class TestDeauthorizeView(HealthVaultTestBase):
    """Tests for healthvaultapp.views.deauthorize"""
    url_name = 'healthvault-deauthorize'

    def test_anonymous(self):
        """User must be logged in to access Deauthorize view."""
        self.client.logout()
        response = self._get()
        login_url = utils.get_setting('LOGIN_URL')
        self.assertRedirectsNoFollow(response, login_url, use_params=False)
        self.assertEqual(HealthVaultUser.objects.count(), 1)

    def test_integrated(self):
        """Deauthorize view should remove credentials & redirect."""
        response = self._get()
        redirect_url = utils.get_setting('HEALTHVAULT_DEAUTHORIZE_REDIRECT')
        self.assertRedirectsNoFollow(response, redirect_url)
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_unintegrated(self):
        """Deauthorize view should redirect if the user isn't integrated."""
        HealthVaultUser.objects.all().delete()
        response = self._get()
        redirect_url = utils.get_setting('HEALTHVAULT_DEAUTHORIZE_REDIRECT')
        self.assertRedirectsNoFollow(response, redirect_url)
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_next(self):
        """Deauthorize view should redirect to specified URL, if available."""
        response = self._get(get_params={NEXT_GET_PARAM: '/next'})
        self.assertRedirectsNoFollow(response, '/next')
        self.assertEqual(HealthVaultUser.objects.count(), 0)
