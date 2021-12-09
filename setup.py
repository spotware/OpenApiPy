#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['protobuf', 'twisted', 'pyopenssl', 'service-identity']

test_requirements = [ ]

setup(
    author="Spotware",
    author_email='connect@spotware.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="A Python package for interacting with Spotware Open API",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='spotware_openApiPy',
    name='spotware_openApiPy',
    packages=find_packages(include=['spotware_openApiPy', 'spotware_openApiPy.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/spotware/OpenApiPy',
    version='1.0.0',
    zip_safe=False,
)
