from django.contrib.auth.models import AnonymousUser

from healthvaultapp.models import HealthVaultUser
from healthvaultapp.templatetags.healthvault import is_integrated_with_healthvault

from .base import HealthVaultTestBase


class TestIntegrationTag(HealthVaultTestBase):
    """Tests for healthvaultapp.templatetags.healthvault.is_integrated_with_healthvault"""

    def test_integrated(self):
        """Users with stored authentication data are integrated."""
        self.assertTrue(is_integrated_with_healthvault(self.user))

    def test_unintegrated(self):
        """Integration requires user authentication data."""
        HealthVaultUser.objects.all().delete()
        self.assertFalse(is_integrated_with_healthvault(self.user))

    def test_unauthenticated(self):
        """Only logged-in users can be integrated."""
        user = AnonymousUser()
        self.assertFalse(is_integrated_with_healthvault(user))
