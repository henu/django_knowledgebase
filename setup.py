#!/usr/bin/env python
import os
from setuptools import setup

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django_knowledgebase',
    version='0.1',
    packages=['knowledgebase'],
    include_package_data=True,
    license='MIT License',
    description='Store various knowledge to graph.',
    author='Henrik Heino',
    author_email='henrik.heino@gmail.com',
    install_requires=['python-dateutil'],
    dependency_links=[],
)
