#!/usr/bin/env python
import coverage
import optparse
import os
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
    parser.add_option('--coverage', dest='coverage', default='0',
                      help="coverage level, 0=no coverage, 1=without branches,"
                      " 2=with branches")
    options, tests = parser.parse_args()
    tests = tests or ['healthvaultapp']

    covlevel = int(options.coverage)
    if covlevel:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if covlevel == 2:
            branch = True
        else:
            branch = False
        cov = coverage.coverage(branch=branch, config_file='.coveragerc')
        cov.load()
        cov.start()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    exit_val = test_runner.run_tests(tests)

    if covlevel:
        cov.stop()
        cov.save()
        cov.html_report()

    sys.exit(exit_val)


import django
# In Django 1.7, we need to run setup first
if hasattr(django, 'setup'):
    django.setup()


if __name__ == '__main__':
    runtests()
