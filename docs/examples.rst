Examples
========

Poll under the current time in seconds is divisble by 5
-------------------------------------------------------

(Ignoring milliseconds)

::

    import polling2, time
    # Wait until the number of seconds (ignoring milliseconds) is divisible by 5.
    polling2.poll(target=time.time, check_success=lambda x: int(x) % 5 == 0, step=0.5, timeout=6)
    1599737060.4507122


Poll every minute until a url returns 200 status code
--------------------------------------------------------------

::

    import requests
    polling2.poll(
        lambda: requests.get('http://google.com').status_code == 200,
        step=60,
        poll_forever=True)


Poll but ignore specifc exceptions
----------------------------------

If you are creating a new cloud provider instance (e.g. waiting for an EC2 instance to come online), you can continue to poll despite getting ConnectionErrors

::

    import requests
    polling2.poll(
        lambda: requests.get('your.instance.ip').status_code == 200,
        step=60,
        ignore_exceptions=(requests.exceptions.ConnectionError,),
        poll_forever=True)

Poll for a file to exist
------------------------

This call will wait until the file exists, checking every 0.1 seconds and stopping after 3 seconds have elapsed

::

    file_handle = polling2.poll(lambda: open('/tmp/myfile.txt'), ignore_exceptions=(IOError,), timeout=3, step=0.1)
    # Polling will return the value of your polling function, so you can now interact with it
    file_handle.close()

Note, poll returns the value of whatever the target last returned.


Polling for Selenium WebDriver elements
---------------------------------------

::

    from selenium import webdriver
     
    driver = webdriver.Firefox()
    driver.get('http://google.com')
     
    search_box = polling2.poll(lambda: driver.find_element_by_id('search'), step=0.5, timeout=7)
    search_box.send_keys('python polling')

Using the polling timeout exception
-----------------------------------

An exception will be raised by the polling function on timeout (or the maximum number of calls is exceeded).
This exception will have a 'values' attribute. This is a queue with all values that did not meet the condition.
You can access them in the except block.

::

    import random
     
    try:
        polling2.poll(lambda: random.choice([0, (), False]), step=0.5, timeout=1)
    except polling2.TimeoutException, te:
        while not te.values.empty():
            # Print all of the values that did not meet the exception
            print te.values.get()

Use a custom checker to decide whether your target has returned what your waiting for
--------------------------------------------------------------------------------------

is_truthy() is the default checker for the parameter check_success. But, it's easy to create a custom checker function, that tests whether the value returned by the target is the expected value.

Here the target is going to return None, which the custom checker, created by is_value(None)  will return True for.

::

    polling2.poll(target=lambda: None, step=0.1, max_tries=1, check_success=polling2.is_value(None))
    # Or another example, where we can test that False is returned by the target.
    polling2.poll(target=lambda: False, step=0.1, max_tries=1, check_success=polling2.is_value(False))

Using a custom condition callback function
------------------------------------------

::

    import requests
     
    def is_correct_response(response):
        """Check that the response returned 'success'"""
        return response == 'success'
    
    polling2.poll(
        lambda: requests.put('http://mysite.com/api/user', data={'username': 'Jill'},
        check_success=is_correct_response,
        step=1,
        timeout=10)

Logging the return values from the target function
---------------------------------------------------

::

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

This will log the string representation of response object to python's logging module at the debug level.
A message like this will be sent to the log for each return value. You can change the level by providing
a different value to the log parameter.

::

    poll() calls check_success(<Response [200]>)

There is also an option to log the exceptions that are caught by ignore_exceptions. Note, the full-exception traceback
will not be printed in the logs. Instead, the error and it's message (using %r formatting) will appear. In the following
code snippet, the ValueError raised by the function `raises_error()` will be sent to the logger at the 'warning' level.

::

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
        print "Un-ignored %r" % _e"
