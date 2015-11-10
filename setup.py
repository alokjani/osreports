#!/usr/bin/env python
#
#   Copyright Reliance Jio Infocomm, Ltd.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#   implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from setuptools import setup, find_packages

with open('requirements.txt','r') as fp:
    requirements = [ x.strip() for x in fp ]

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='osreports',
    version='0.1.1',
    url='https://github.com/alokjani/osreports',
    author='Alok Jani',
    author_email='Alok.Jani@ril.com',
    description='Utilization Reporting for OpenStack Clouds',
    long_description=long_description,
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Environment :: OpenStack',
        ],
    entry_points={
        'console_scripts': [
            'osreports = osreports.client:main',
            ]
        },
)
