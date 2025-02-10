#!/usr/bin/python3

from setuptools import setup
setup(
    name='lookup_service',
    version='6.0.0',
    description='LookupService',
    url='http://www.perfsonar.net',
    author='The perfSONAR Development Team',
    author_email='perfsonar-developer@perfsonar.net',
    license='Apache 2.0',
    packages=[
        'pslookup'
    ],
    install_requires=['requests',
                      'jsonschema',
                      'pyinotify'],

    #include_package_data=True,
    package_data={"pslookup": ["schema/schema.json"]},
    tests_require=['nose'],
    test_suite='nose.collector',
)