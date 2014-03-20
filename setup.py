from setuptools import setup, find_packages


required = [line for line in open('requirements/base.txt').read().split('\n')]

setup(
    name='django-healthvault',
    version=__import__('healthvaultapp').__version__,
    author='orcas',
    author_email='',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['distribute'] + required,
    url='https://github.com/orcasgit/django-healthvault/',
    license='',
    description=u' '.join(__import__('healthvaultapp').__doc__.splitlines()).strip(),
    long_description=open('README.md').read(),
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    test_suite="runtests.runtests",
    zip_safe=False,
)
