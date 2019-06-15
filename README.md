[![Build Status](https://travis-ci.org/ddmee/polling2.svg?branch=master)](https://travis-ci.org/ddmee/polling2)
[![PyPI](https://img.shields.io/pypi/dm/polling2.svg)]()
[![PyPI](https://img.shields.io/pypi/v/polling2.svg)]()
[![HitCount](http://hits.dwyl.io/ddmee/polling2.svg)](http://hits.dwyl.io/ddmee/polling2)

polling2
=============

_Never write another polling function again!_

Polling2 is a powerful python utility used to wait for a function to return a certain expected condition.

Some possible uses cases include:

- Wait for API response to return with code 200
- Wait for a file to exist (or not exist)
- Wait for a thread lock on a resource to expire

Polling2 is handy for getting rid of all that duplicated polling-code. Often, applications require retrying until the correct response is returned. Why re-implement the ability to poll again and again? Use Polling2!

Polling2 is a fork of the original [polling](https://github.com/justiniso/polling). It was forked when the original maintainer failed to respond to issues or PRs. 

Polling2 is ++under active development++. Would you like to see a particular feature? Ask and thou shall recieve.

# Installation

```
pip install polling2
```

# Development installation

```shell
# install lib, but use system links from the repo into sitepackages.
python setup.py develop
# install test dependenices.
python setup.py test
# run the tests
pytest tests
```

# Examples

### Example: Poll every minute until a url returns 200 status code

```python
import requests
polling2.poll(
    lambda: requests.get('http://google.com').status_code == 200,
    step=60,
    poll_forever=True)
```

If you are creating a new cloud provider instance (e.g. waiting for an EC2 instance to come online), you can continue to poll despite getting ConnectionErrors:

```python
import requests
polling2.poll(
    lambda: requests.get('your.instance.ip').status_code == 200,
    step=60,
    ignore_exceptions=(requests.exceptions.ConnectionError,),
    poll_forever=True)
```

### Example: Poll for a file to exist

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
    
### Example: Polling for Selenium WebDriver elements

```python
from selenium import webdriver
driver = webdriver.Firefox()

driver.get('http://google.com')
search_box = polling2.poll(
    lambda: driver.find_element_by_id('search'),
    step=0.5,
    timeout=7)

search_box.send_keys('python polling')
```

### Example: Using the polling timeout exception

```python
# An exception will be raised by the polling function on timeout (or the maximum number of calls is exceeded).
# This exception will have a 'values' attribute. This is a queue with all values that did not meet the condition.
# You can access them in the except block.

import random
try:
    polling2.poll(lambda: random.choice([0, (), False]), step=0.5, timeout=1)
except polling2.TimeoutException, te:
    while not te.values.empty():
        # Print all of the values that did not meet the exception
        print te.values.get()
```


### Example: Using a custom condition callback function

```python
import requests

def is_correct_response(response):
    """Check that the response returned 'success'"""
    return response == 'success'

polling2.poll(
    lambda: requests.put('http://mysite.com/api/user', data={'username': 'Jill'},
    check_success=is_correct_response,
    step=1,
    timeout=10)
```

### Example: Logging the return values from the target function.

```python
import logging
import requests

def is_correct_response(response):
    """Check that the response returned 'success'"""
    return response == 'success'

polling2.poll(
    lambda: requests.put('http://mysite.com/api/user', data={'username': 'Jill'},
    check_success=is_correct_response,
    step=1,
    timeout=10,
    log=logging.DEBUG)
```

This will log the string representation of response object to python's logging module at the debug level.
A message like this will be sent to the log for each return value. You can change the level by providing
a different value to the log parameter.

```text
poll() calls check_success(<Response [200]>)
```

There is also an option to log the exceptions that are caught by ignore_exceptions. Note, the full-exception traceback
will not be printed in the logs. Instead, the error and it's message (using %r formatting) will appear. In the following
code snippet, the ValueError raised by the function `raises_error()` will be sent to the logger at the 'warning' level.

```python
import polling2
import logging
import mock

# basicConfig should sent warning level messages to the stdout.
logging.basicConfig()

# Create a function that raises a ValueError, then a RuntimeError.
raises_error = mock.Mock(side_effect=[ValueError('a message'), RuntimeError])

try:
    polling2.poll(
        target=raises_error,
        step=0.1,
        max_tries=3,
        ignore_exceptions=(ValueError),  # Only ignore the ValueError.
        log_error=logging.WARNING  # Ignored errors should be passed to the logger at warning level.
    )
except RuntimeError as _e:
    print "Un-ignored %r" % _e``
```
 
# Future extensions

- Add poll_killer(). Specify a hard timeout so that if the function being polled blocks and doesn't return, poll_killer() will raise a timeout.
  - Add an option to do via multiprocessing.
  - Add an option to do via threading - probably the default option.
- Add poll_chain(). Have reason to poll a bunch of functions in a row? poll_chain() allows you to chain a bunch of polling functions together.
- Allow step to be specificed as 0, so that we can poll continously. (Perhaps it's best to write a poll_continous() method.)

# Release notes

## 0.4.3 
- Add log_error parameter to the poll signature. Enables logging of ignored exceptions.

## 0.4.2
- Add log_value() decorator and log parameter to poll signature. Enables logging of return_values.

## 0.4.0
- Fixed polling function from waiting another sleep whenever the max_tries value has reached zero.
- Remove test-only dependencies from requirements to install the package.
- No longer testing on python 2.6. Add support for travis testing on python 3.6 and pypy 3.5.
- Creation of polling2, forked from polling as previous maintainer seems to be ignoring issues and pull-requests.
- Remove ```*a, **k``` from poll signature. This allows Type errors to be raised if caller spells arguments into correctly, making bugs easier to find.

## 0.3.0

- Support Python 3.4+

## 0.2.0

- Allow users to access a "last" attribute on the exceptions. This should hold the last evaluated value, which is the more common use case than getting the first value. 
- Fix a bug that actually ran 1 more time than value specified by max_tries

## 0.1.0

- First version

# Contributors
- Justin Iso (original creator)
- Donal Mee
