from django.core.urlresolvers import reverse

from healthvaultlib.healthvault import HealthVaultException
from healthvaultlib.targets import ApplicationTarget

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
        self.assertTrue(NEXT_SESSION_KEY in self.client.session)
        self.assertEqual(self.client.session[NEXT_SESSION_KEY], '/next')
        self.assertEqual(HealthVaultUser.objects.count(), 0)


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
        response = self._mock_connection_get()
        self.assertRedirectsNoFollow(response, self.deauthorization_url)
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_unintegrated(self):
        """Deauthorize view should short-circuit if user isn't integrated."""
        self.hvuser.delete()
        response = self._mock_connection_get()
        redirect_url = utils.get_setting('HEALTHVAULT_DEAUTHORIZE_REDIRECT')
        self.assertRedirectsNoFollow(response, redirect_url)
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_next(self):
        """
        Deauthorize view should redirect to specified URL if user isn't
        integrated.
        """
        self.hvuser.delete()
        get_params = {NEXT_GET_PARAM: '/next'}
        response = self._mock_connection_get(get_params=get_params)
        self.assertRedirectsNoFollow(response, '/next')
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_session_variable(self):
        """Deauthorize view should save NEXT_GET_PARAM in session."""
        get_params = {NEXT_GET_PARAM: '/next'}
        response = self._mock_connection_get(get_params=get_params)
        self.assertTrue(NEXT_SESSION_KEY in self.client.session)
        self.assertEqual(self.client.session[NEXT_SESSION_KEY], '/next')


class TestCompleteView(HealthVaultTestBase):
    """Tests for healthvaultapp.views.complete - General"""
    url_name = 'healthvault-complete'

    def test_anonymous(self):
        """User must be logged in to access Complete view."""
        self.client.logout()
        response = self._get()
        login_url = utils.get_setting('LOGIN_URL')
        self.assertRedirectsNoFollow(response, login_url, use_params=False)
        self.assertEqual(HealthVaultUser.objects.count(), 1)

    def test_no_target(self):
        """Complete view should throw Exception if target is not given."""
        with self.assertRaises(Exception) as e:
            response = self._get(get_params={'target': None})
            self.assertEqual(e.message, 'Unknown target: None')

    def test_bad_target(self):
        """Complete view should throw Exception if target is not recognized."""
        with self.assertRaises(Exception) as e:
            response = self._get(get_params={'target': 'bad'})
            self.assertEqual(e.message, 'Unknown target: bad')

    def test_unhandled_target(self):
        """Complete view should throw Exception if target is unhandled."""
        with self.assertRaises(Exception) as e:
            response = self._get(get_params={'target': 'EditRecordComplete'})
            correct = 'Unhandled target: EditRecordComplete'
            self.assertEqual(e.message, correct)


class TestCompleteView_APPAUTHREJECT(HealthVaultTestBase):
    """Tests for healthvaultapp.views.complete - APPAUTHREJECT"""
    url_name = 'healthvault-complete'
    target = ApplicationTarget.APPAUTHREJECT

    def _get(self, get_params=None, **kwargs):
        get_params = get_params or {'target': self.target}
        return super(TestCompleteView_APPAUTHREJECT, self)._get(
                get_params=get_params, **kwargs)

    def test_integrated(self):
        """Should delete credentials and redirect."""
        response = self._mock_connection_get()
        redirect_url = utils.get_setting('HEALTHVAULT_DENIED_REDIRECT')
        self.assertRedirectsNoFollow(response, redirect_url)
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_unintegrated(self):
        """Should redirect to denial URL."""
        response = self._mock_connection_get()
        redirect_url = utils.get_setting('HEALTHVAULT_DENIED_REDIRECT')
        self.assertRedirectsNoFollow(response, redirect_url)
        self.assertEqual(HealthVaultUser.objects.count(), 0)


class TestCompleteView_APPAUTHSUCCESS(HealthVaultTestBase):
    """Tests for healthvaultapp.views.complete - APPAUTHSUCCESS"""
    url_name = 'healthvault-complete'
    target = ApplicationTarget.APPAUTHSUCCESS

    def setUp(self):
        super(TestCompleteView_APPAUTHSUCCESS, self).setUp()
        self.hvuser.delete()

    def _get(self, get_params=None, **kwargs):
        if get_params is None:
            get_params = {'wctoken': self.token, 'target': self.target}
        return super(TestCompleteView_APPAUTHSUCCESS, self)._get(
                get_params=get_params, **kwargs)

    def test_unintegrated(self):
        """Complete view should store user's access credentials."""
        response = self._mock_connection_get()
        redirect_url = utils.get_setting('HEALTHVAULT_AUTHORIZE_REDIRECT')
        self.assertRedirectsNoFollow(response, redirect_url)
        self.assertEqual(HealthVaultUser.objects.count(), 1)
        hvuser = HealthVaultUser.objects.get()
        self.assertEqual(hvuser.token, self.token)
        self.assertEqual(hvuser.record_id, self.record_id)

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
        self.assertEqual(hvuser.record_id, self.record_id)

    def test_no_token(self):
        """Complete view should redirect to error if wctoken is not given."""
        get_params = {'target': 'AppAuthSuccess'}
        response = self._mock_connection_get(get_params=get_params)
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


class TestCompleteView_SELECTEDRECORDCHANGED(TestCompleteView_APPAUTHSUCCESS):
    """Tests for healthvaultapp.views.complete - SELECTEDRECORDCHANGED

    Should behave the same way as APPAUTHSUCCESS.
    """
    target = ApplicationTarget.SELECTEDRECORDCHANGED


class TestCompleteView_SIGNOUT(HealthVaultTestBase):
    """Tests for healthvaultapp.views.complete - Deauthorization completion"""
    url_name = 'healthvault-complete'
    target = ApplicationTarget.SIGNOUT

    def _get(self, get_params=None, **kwargs):
        get_params = get_params or {'target': self.target}
        return super(TestCompleteView_SIGNOUT, self)._get(
                get_params=get_params, **kwargs)

    def test_unintegrated(self):
        """Complete view should redirect."""
        self.hvuser.delete()
        response = self._mock_connection_get()
        redirect_url = utils.get_setting('HEALTHVAULT_DEAUTHORIZE_REDIRECT')
        self.assertRedirectsNoFollow(response, redirect_url)
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_integrated(self):
        """Complete view should redirect."""
        response = self._mock_connection_get()
        redirect_url = utils.get_setting('HEALTHVAULT_DEAUTHORIZE_REDIRECT')
        self.assertRedirectsNoFollow(response, redirect_url)
        self.assertEqual(HealthVaultUser.objects.count(), 0)

    def test_next(self):
        """Complete view should redirect to NEXT_SESSION_KEY, if available."""
        self._set_session_vars(**{NEXT_SESSION_KEY: '/next'})
        response = self._mock_connection_get()
        self.assertRedirectsNoFollow(response, '/next')
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
