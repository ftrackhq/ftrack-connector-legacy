# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys
import os
import subprocess
from distutils.spawn import find_executable


from setuptools import setup, find_packages, Command
from distutils.command.build import build as BuildCommand
from distutils.command.clean import clean as CleanCommand

from setuptools.command.bdist_egg import bdist_egg as BuildEggCommand
from setuptools.command.test import test as TestCommand
import distutils.dir_util
import distutils
import fileinput
from pkg_resources import get_distribution, DistributionNotFound

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
SOURCE_PATH = os.path.join(ROOT_PATH, 'source')
README_PATH = os.path.join(ROOT_PATH, 'README.rst')
RESOURCE_PATH = os.path.join(ROOT_PATH, 'resource')
DISTRIBUTION_PATH = os.path.join(ROOT_PATH, 'dist')

RESOURCE_TARGET_PATH = os.path.join(
    SOURCE_PATH, 'ftrack_connector_legacy', 'ui', 'resource.py'
)

try:
    release = get_distribution('ftrack-connector-legacy').version
    # take major/minor/patch
    VERSION = '.'.join(release.split('.')[:3])

except DistributionNotFound:
    # package is not installed
    VERSION = 'Unknown version'


# Custom commands.
class BuildResources(Command):
    '''Build additional resources.'''

    user_options = []

    def initialize_options(self):
        '''Configure default options.'''

    def finalize_options(self):
        '''Finalize options to be used.'''
        self.sass_path = os.path.join(RESOURCE_PATH, 'sass')
        self.css_path = RESOURCE_PATH
        self.resource_source_path = os.path.join(
            RESOURCE_PATH, 'resource.qrc'
        )
        self.resource_target_path = RESOURCE_TARGET_PATH

    def _replace_imports_(self):
        '''Replace imports in resource files to QtExt instead of QtCore.

        This allows the resource file to work with many different versions of
        Qt.

        '''
        replace = 'from QtExt import QtCore'
        for line in fileinput.input(self.resource_target_path, inplace=True):
            if 'import QtCore' in line:
                # Calling print will yield a new line in the resource file.
                sys.stdout.write(line.replace(line, replace))
            else:
                # Calling print will yield a new line in the resource file.
                sys.stdout.write(line)

    def run(self):
        '''Run build.'''
        try:
            import scss
        except ImportError:
            raise RuntimeError(
                'Error compiling sass files. Could not import "scss". '
                'Check you have the pyScss Python package installed.'
            )

        compiler = scss.Scss(
            search_paths=[self.sass_path]
        )

        themes = [
            'style_light',
            'style_dark'
        ]
        for theme in themes:
            scss_source = os.path.join(self.sass_path, '{0}.scss'.format(theme))
            css_target = os.path.join(self.css_path, '{0}.css'.format(theme))

            compiled = compiler.compile(
                scss_file=scss_source
            )
            with open(css_target, 'w') as file_handle:
                file_handle.write(compiled)
                print('Compiled {0}'.format(css_target))

        try:
            pyside_rcc_command = 'pyside-rcc'

            # On Windows, pyside-rcc is not automatically available on the
            # PATH so try to find it manually.
            if sys.platform == 'win32':
                import PySide
                pyside_rcc_command = os.path.join(
                    os.path.dirname(PySide.__file__),
                    'pyside-rcc.exe'
                )

            subprocess.check_call([
                pyside_rcc_command,
                '-o',
                self.resource_target_path,
                self.resource_source_path
            ])

        except (subprocess.CalledProcessError, OSError) as error:
            raise RuntimeError(
                'Error compiling resource.py using pyside-rcc. Possibly '
                'pyside-rcc could not be found. You might need to manually add '
                'it to your PATH. See README for more information.'
            )

        self._replace_imports_()


class BuildEgg(BuildEggCommand):
    '''Custom egg build to ensure resources built.

    .. note::

        Required because when this project is a dependency for another project,
        only bdist_egg will be called and *not* build.

    '''

    def run(self):
        '''Run egg build ensuring build_resources called first.'''
        self.run_command('build_resources')
        BuildEggCommand.run(self)


class Build(BuildCommand):
    '''Custom build to pre-build resources.'''

    def run(self):
        '''Run build ensuring build_resources called first.'''
        self.run_command('build_resources')
        BuildCommand.run(self)


class Clean(CleanCommand):
    '''Custom clean to remove built resources and distributions.'''

    def run(self):
        '''Run clean.'''
        relative_resource_path = os.path.relpath(
            RESOURCE_TARGET_PATH, ROOT_PATH
        )
        if os.path.exists(relative_resource_path):
            os.remove(relative_resource_path)
        else:
            distutils.log.warn(
                '\'{0}\' does not exist -- can\'t clean it'
                .format(relative_resource_path)
            )

        if self.all:
            relative_distribution_path = os.path.relpath(
                DISTRIBUTION_PATH, ROOT_PATH
            )
            if os.path.exists(relative_distribution_path):
                distutils.dir_util.remove_tree(
                    relative_distribution_path, dry_run=self.dry_run
                )
            else:
                distutils.log.warn(
                    '\'{0}\' does not exist -- can\'t clean it'
                    .format(relative_distribution_path)
                )

        CleanCommand.run(self)


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
    package_dir={
        '': 'source'
    },
    project_urls={
        'Source Code': 'https://bitbucket.org/ftrack/ftrack-connector-legacy/src/{}'.format(VERSION),
    },
    setup_requires=[
        'qtext @ git+https://bitbucket.org/ftrack/qtext/get/0.2.2.zip#egg=qtext',
        'pyScss >= 1.2.0, < 2',
        'sphinx >= 1.2.2, < 2',
        'sphinx_rtd_theme >= 0.1.6, < 2',
        'PySide >= 1.2.2, < 2',
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
        'ftrack-python-api >=2, < 3',
        'Riffle',
        'arrow >= 0.4.6, < 1',
        'appdirs == 1.4.0',
        'requests >= 2, <3',
        'future',
        'lowdown >= 0.1.0, < 1',
        'qtext @ git+https://bitbucket.org/ftrack/qtext/get/0.2.2.zip#egg=qtext'
    ],
    python_requires='>= 2.7.9, < 3.0',
    cmdclass={
        'build': Build,
        'build_ext': Build,
        'build_resources': BuildResources,
        'bdist_egg': BuildEgg,
        'clean': Clean,
        'test': PyTest
    },
    zip_safe=True,
)