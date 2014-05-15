# coding: utf-8
from __future__ import unicode_literals

import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from forme import __version__


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))

setup(
    name='forme',
    version=__version__,
    license='MIT',

    author='Tomáš Ehrlich',
    author_email='tomas.ehrlich@gmail.com',

    description='Django forms for template designers… and for me!',
    long_description=open('README.md').read(),
    url='https://github.com/elvard/django-forme',

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django',
    ],

    cmdclass={'test': PyTest},
    tests_require=[
        'pytest',
        'beautifulsoup4',
        'mock',
    ],

    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
)
