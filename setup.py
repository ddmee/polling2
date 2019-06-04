#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from polling2 import __version__

# consts
HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, "README.md"), "r") as fh:
    LONG_DESCRIPTION = fh.read()

with open(os.path.join(HERE, "test_requirements.txt")) as fp:
    TEST_REQUIREMENTS = fp.read().split("\n")

setup(
    name='polling2',
    version=__version__,
    author='Donal Mee',
    author_email='mee.donal@gmail.com',
    description='Updated polling utility with many configurable options',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url='http://github.com/ddmee/polling2',
    download_url='',
    py_modules=['polling2'],
    tests_require=TEST_REQUIREMENTS,
    test_suite='tests',
    setup_requires=['pytest-runner',],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)