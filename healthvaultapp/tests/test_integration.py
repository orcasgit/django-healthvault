from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse

from healthvaultapp.models import HealthVaultUser
from healthvaultapp import utils

from .base import HealthVaultTestBase


class TestIntegrationUtility(HealthVaultTestBase):
    """Tests for healthvaultapp.utils.is_integrated"""

    def test_is_integrated(self):
        """Users with stored authentication data are integrated."""
        self.assertTrue(utils.is_integrated(self.user))

    def test_is_not_integrated(self):
        """Integration requires user authentication data."""
        HealthVaultUser.objects.all().delete()
        self.assertFalse(utils.is_integrated(self.user))

    def test_unauthenticated(self):
        """Only logged-in users can be integrated."""
        user = AnonymousUser()
        self.assertFalse(utils.is_integrated(user))


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
        self.assertRedirectsNoFollow(response, '/test')
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_integrated(self):
        """Should be able to access view even if already authorized."""
        hvuser = self.create_healthvault_user(user=self.user)
        response = self._mock_connection_get()
        self.assertRedirectsNoFollow(response, '/test')
        self.assertEqual(HealthVaultUser.objects.count(), 1)
        self.assertEqual(HealthVaultUser.objects.get(), hvuser)

    def test_next(self):
        """Authorize view should save the 'next' parameter."""
        response = self._mock_connection_get(get_params={'next': '/next'})
        self.assertRedirectsNoFollow(response, '/test')
        self.assertEqual(self.client.session.get('healthvault_next', None),
                '/next')
        self.assertEqual(HealthVaultUser.objects.count(), 0)


class TestCompleteView(HealthVaultTestBase):
    """Tests for healthvaultapp.views.complete"""
    url_name = 'healthvault-complete'

    def setUp(self):
        super(TestCompleteView, self).setUp()
        self.token = 'testtoken'
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
        response = self._get()
        redirect_url = utils.get_setting('HEALTHVAULT_AUTHORIZE_REDIRECT')
        self.assertRedirectsNoFollow(response, redirect_url)
        self.assertEqual(HealthVaultUser.objects.count(), 1)
        hvuser = HealthVaultUser.objects.get()
        self.assertEqual(hvuser.token, self.token)

    def test_integrated(self):
        """Complete view should overwrite any existing credentials."""
        hvuser = self.create_healthvault_user(user=self.user, token='oldtoken')
        response = self._get()
        redirect_url = utils.get_setting('HEALTHVAULT_AUTHORIZE_REDIRECT')
        self.assertRedirectsNoFollow(response, redirect_url)
        self.assertEqual(HealthVaultUser.objects.count(), 1)
        hvuser = HealthVaultUser.objects.get()
        self.assertEqual(hvuser.token, self.token)

    def test_next(self):
        """Complete view should redirect to specified URL, if available."""
        self._set_session_vars(healthvault_next='/next')
        response = self._get()
        self.assertRedirectsNoFollow(response, '/next')
        self.assertEqual(HealthVaultUser.objects.count(), 1)
        hvuser = HealthVaultUser.objects.get()
        self.assertEqual(hvuser.token, self.token)

    def test_no_token(self):
        """Complete view should redirect to error if wctoken is not given."""
        response = self._get(get_params={})
        self.assertRedirectsNoFollow(response, reverse('healthvault-error'))
        self.assertEqual(HealthVaultUser.objects.count(), 0)


class TestErrorView(HealthVaultTestBase):
    """Tests for healthvaultapp.views.error"""
    url_name = 'healthvault-error'

    def test_anonymous(self):
        """User must be logged in to access Error view."""
        self.client.logout()
        response = self._get()
        login_url = utils.get_setting('LOGIN_URL')
        self.assertRedirectsNoFollow(response, login_url, use_params=False)

    def test_integrated(self):
        """Should be able to retrieve error page."""
        response = self._get()
        self.assertEqual(response.status_code, 200)

    def test_unintegrated(self):
        """HealthVault credentials aren't required to access Error view."""
        HealthVaultUser.objects.all().delete()
        response = self._get()
        self.assertEqual(response.status_code, 200)


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
        response = self._get(get_params={'next': '/next'})
        self.assertRedirectsNoFollow(response, '/next')
        self.assertEqual(HealthVaultUser.objects.count(), 0)
