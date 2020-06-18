# :coding: utf-8
# :copyright: Copyright (c) 2017-2020 ftrack

import os

from pkg_resources import DistributionNotFound, get_distribution
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
SOURCE_PATH = os.path.join(ROOT_PATH, 'source')
README_PATH = os.path.join(ROOT_PATH, 'README.rst')


try:
    release = get_distribution('ftrack-connector-legacy').version
    # take major/minor/patch
    VERSION = '.'.join(release.split('.')[:3])

except DistributionNotFound:
    # package is not installed
    VERSION = 'Unknown version'


# Custom commands.
class PyTest(TestCommand):
    '''Pytest command.'''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        '''Import pytest and run.'''
        import pytest

        errno = pytest.main(self.test_args)
        raise SystemExit(errno)


version_template = '''
# :coding: utf-8
# :copyright: Copyright (c) 2017-2020 ftrack

__version__ = {version!r}
'''

# Configuration.
setup(
    name='ftrack-connector-legacy',
    version=VERSION,
    description='Legacy Qt Widgets and DCC-specific connectors extracted from ftrack Connect.',
    long_description=open(README_PATH).read(),
    keywords='ftrack',
    url='https://bitbucket.org/ftrack/ftrack-connector-legacy',
    author='ftrack',
    author_email='support@ftrack.com',
    license='Apache License (2.0)',
    packages=find_packages(SOURCE_PATH),
    package_dir={'': 'source'},
    project_urls={
        'Source Code': 'https://bitbucket.org/ftrack/ftrack-connector-legacy/src/{}'.format(VERSION),
    },
    setup_requires=[
        'qtext @ git+https://bitbucket.org/ftrack/qtext/get/0.2.2.zip#egg=qtext',
        'pyScss >= 1.2.0, < 2',
        'sphinx >= 1.2.2, < 2',
        'sphinx_rtd_theme >= 0.1.6, < 2',
        'lowdown >= 0.1.0, < 1',
        'setuptools>=30.3.0',
        'setuptools_scm'
    ],
    tests_require=['pytest >= 2.3.5, < 3'],
    use_scm_version={
        'write_to': 'source/ftrack_connector_legacy/_version.py',
        'write_to_template': version_template,
    },
    install_requires=[
        'ftrack-python-legacy-api >=3, <4',
        'ftrack-python-api >= 1, < 2',
        'Riffle',
        'arrow >= 0.4.6, < 1',
        'appdirs == 1.4.0',
        'requests >= 2, <3',
        'lowdown >= 0.1.0, < 1',
        'qtext @ git+https://bitbucket.org/ftrack/qtext/get/0.2.2.zip#egg=qtext'
    ],
    python_requires='>= 2.7.9, < 3.0',
    cmdclass={
        'test': PyTest
    },
    zip_safe=True,
)