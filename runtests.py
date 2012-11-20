#!/usr/bin/env python
import optparse
import sys

from django.conf import settings


if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.messages',
            'django.contrib.sessions',
            'healthvaultapp',
        ),
        ROOT_URLCONF='healthvaultapp.urls',
        SECRET_KEY='this-is-just-for-tests-so-not-that-secret',
        SITE_ID=1,

        HEALTHVAULT_APP_ID='test_app_id',
        HEALTHVAULT_THUMBPRINT='test_thumbprint',
        HEALTHVAULT_PUBLIC_KEY=12345678L,
        HEALTHVAULT_PRIVATE_KEY=12345678L,
        HEALTHVAULT_SERVER='test_server',
        HEALTHVAULT_SHELL_SERVER='test_shell_server',
    )


from django.test.utils import get_runner


def runtests():
    parser = optparse.OptionParser()
    _, tests = parser.parse_args()
    tests = tests or ['healthvaultapp']

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    sys.exit(test_runner.run_tests(tests))


if __name__ == '__main__':
    runtests()

