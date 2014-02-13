# coding: utf-8
from __future__ import unicode_literals

from setuptools import setup, find_packages
from forme import __VERSION__

setup(
    name='forme',
    version=__VERSION__,
    license='MIT',

    author='Tomáš Ehrlich',
    author_email='tomas.ehrlich@gmail.com',

    description='Django forms for template designers… and for me!',
    long_description=open('README.md').read(),
    url='https://github.com/elvard/django-forme',

    packages=find_packages(),
    install_requires=[
        'django',
    ],
    tests_require=[
        'mock',
        'pytest',
        'pytest-django',
    ]
)
