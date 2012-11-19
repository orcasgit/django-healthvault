import random
import string

from django.contrib.auth.models import User
from django.test import TestCase


class HealthVaultTestBase(TestCase):

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
