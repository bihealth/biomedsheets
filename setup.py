#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'jsonschema==2.5.1',
    'pyyaml==3.12',
    'jsonpath-rw==1.4.0',
    'requests==2.12.4',
    'requests-file==1.4.1'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='biosheets',
    version='0.1.0',
    description=(
        'Python 3 library for accessing and managing BioMedical sheets'),
    long_description=readme + '\n\n' + history,
    author='Manuel Holtgrewe',
    author_email='manuel.holtgrewe@bihealth.de',
    url='https://github.com/holtgrewe/biosheets',
    packages=[
        'biomedsheets',
    ],
    package_dir={
        'biomedsheets': 'biomedsheets',
    },
    package_data={
        'biomedsheets': ['data/*.json'],
    },
    entry_points={
        'console_scripts': [
            'biomedsheets = biomedsheets.__main__:main',
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license='MIT license',
    zip_safe=False,
    keywords='biomed sheets',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
