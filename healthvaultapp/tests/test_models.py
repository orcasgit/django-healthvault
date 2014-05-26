from .base import HealthVaultTestBase


class TestModels(HealthVaultTestBase):
    """ Tests for healthvaultapp.models """

    def test_healthvaultuser(self):
        self.assertEqual(self.user, self.hvuser.user)
        self.assertEqual(self.hvuser.__unicode__(),
                         self.user.__unicode__())
