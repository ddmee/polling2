[![Build Status](https://travis-ci.com/ddmee/polling2.svg?branch=master)](https://travis-ci.org/ddmee/polling2)
[![PyPI](https://img.shields.io/pypi/dm/polling2.svg)](https://pypi.org/project/polling2/)
[![PyPI](https://img.shields.io/pypi/v/polling2.svg)](https://pypi.org/project/polling2/)
[![Documentation Status](https://readthedocs.org/projects/polling2/badge/?version=latest)](https://polling2.readthedocs.io/en/latest/?badge=latest)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ddmee_polling2&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ddmee_polling2)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=ddmee_polling2&metric=bugs)](https://sonarcloud.io/summary/new_code?id=ddmee_polling2)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=ddmee_polling2&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=ddmee_polling2)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=ddmee_polling2&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=ddmee_polling2)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=ddmee_polling2&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=ddmee_polling2)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# polling2

_Never write another polling function again!_

Documentation available at [Read the Docs](https://polling2.readthedocs.io)

You can install the package from [Pypi](https://pypi.org/project/polling2/)

Polling2 is a powerful python utility used to wait for a function to return a certain expected condition.

Some possible uses cases include:

- Wait for API response to return with code 200
- Wait for a file to exist (or not exist)
- Wait for a thread lock on a resource to expire

Polling2 is handy for getting rid of all that duplicated polling-code. Often, applications require retrying until the correct response is returned. Why re-implement the ability to poll again and again? Use Polling2!

Polling2 is a fork of the original [polling](https://github.com/justiniso/polling). It was forked when the original maintainer failed to respond to issues or PRs.

Polling2 is _under active development_. Would you like to see a particular feature? Ask and thou shall recieve.

## Installation

```shell
pip install polling2
```

## Development installation

```shell
# install lib, but use system links from the repo into sitepackages.
python setup.py develop
# install test dependenices.
python setup.py test
# run the tests
pytest tests
```

Note, `tox` is also available, as well as `pre-commit`.

```shell
# install tox and run it
pip install tox
tox
```

Pre-commit performs auto-formatting and things of that nature before each commit.

```shell
pip install pre-commit
pre-commit install
```

Now pre-commit will run automatically on ``git commit``.

## Example:

```python
# This call will wait until the file exists, checking every 0.1 seconds and stopping after 3 seconds have elapsed
file_handle = polling2.poll(
    lambda: open('/tmp/myfile.txt'),
    ignore_exceptions=(IOError,),
    timeout=3,
    step=0.1)

# Polling will return the value of your polling function, so you can now interact with it
file_handle.close()
```

There are [more examples](https://polling2.readthedocs.io/en/latest/examples) in the documentation.

## API and user guide at [Read the Docs](https://polling2.readthedocs.io)

[![Read the Docs](https://raw.githubusercontent.com/ddmee/polling2/master/ext/read_the_docs.png)](https://polling2.readthedocs.io)
