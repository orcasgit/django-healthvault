from mock import patch

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured

from healthvaultlib.healthvault import HealthVaultException

from healthvaultapp import utils
from healthvaultapp.models import HealthVaultUser

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


class TestConnectionUtility(HealthVaultTestBase):
    """Tests for healthvaultapp.utils.create_connection"""

    def test_from_settings(self):
        """Should return a connection object."""
        connection = self._create_mock_connection()
        self.assertTrue(connection is not None)

    def test_with_token(self):
        """Should return a connection object."""
        connection = self._create_mock_connection(wctoken=self.token)
        self.assertTrue(connection is not None)

    def test_null_param(self):
        """ImproperlyConfigured should be raised if any params are null."""
        with self.assertRaises(ImproperlyConfigured):
            connection = self._create_mock_connection(app_id=None)

    def test_blank_param(self):
        """ImproperlyConfigured should be raised if any params are blank."""
        with self.assertRaises(ImproperlyConfigured):
            connection = self._create_mock_connection(app_id='')

    def test_value_error(self):
        """
        ImproperlyConfigured should be raised if HealthVaultConn raises a
        ValueError.
        """
        with self.assertRaises(ImproperlyConfigured):
            connection = self._create_mock_connection(side_effect=ValueError)

    def test_healthvault_exception(self):
        """
        HealthVaultException should be propagated if it is thrown by
        HealthVaultConn.
        """
        with self.assertRaises(HealthVaultException):
            side_effect = HealthVaultException
            connection = self._create_mock_connection(side_effect=side_effect)
