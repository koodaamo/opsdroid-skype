#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'opsdroid', 'arrow', 'botbuilder-core','botbuilder-schema',
    'botframework-connector'
]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Petri Savolainen",
    author_email='petri@koodaamo.fi',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Skype support for opsdroid",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='opsdroid skype bot',
    name='opsdroid-skype',
    packages=['opsdroid_skype'],
    setup_requires=setup_requirements,
    entry_points = {
        'opsdroid_connectors': [
            'skype = opsdroid_skype.connector'
        ]
    },
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/koodaamo/opsdroid-skype',
    version='0.1.0',
    zip_safe=False,
)
