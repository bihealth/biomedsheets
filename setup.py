#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import pip
from pip.req import parse_requirements

import versioneer

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

reqs = parse_requirements('requirements.txt', session=pip.download.PipSession())

requirements = [str(ir.req) for ir in reqs]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='biomedsheets',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description=(
        'Python 3 library for accessing and managing BioMedical sheets'),
    long_description=readme + '\n\n' + history,
    author='Manuel Holtgrewe',
    author_email='manuel.holtgrewe@bihealth.de',
    url='https://github.com/bihealth/biomedsheets',
    packages=find_packages(),
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
    keywords='biomedsheets',
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
