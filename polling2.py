"""Polling2 module containing all exceptions and helpers used for the polling function

Never write another polling function again.

"""

__version__ = '0.4.4'

import multiprocessing
import logging
import time

try:
    from Queue import Queue
except ImportError:
    from queue import Queue


LOGGER = logging.getLogger(__name__)


class PollingException(Exception):
    """Base exception that stores all return values of attempted polls"""
    def __init__(self, msg, values, last=None):
        self.values = values
        self.last = last
        super(PollingException, self).__init__(msg)


class TimeoutException(PollingException):
    """Exception raised if polling function times out"""


class MaxCallException(PollingException):
    """Exception raised if maximum number of iterations is exceeded"""


def step_constant(step):
    """Use this function when you want the step to remain fixed in every iteration (typically good for
    instances when you know approximately how long the function should poll for)"""
    return step


def step_linear_double(step):
    """Use this function when you want the step to double each iteration (e.g. like the way ArrayList works in
    Java). Note that this can result in very long poll times after a few iterations"""
    return step * 2


def is_truthy(val):
    """Use this function to test if a return value is truthy"""
    return bool(val)


def log_value(check_success, level=logging.DEBUG):
    """A decorator for a check_success function that logs the return_value passed to check_success.

    :opt param level: the level at which to log the return value, defaults to debug. Must be
        one of the values in logging._levelNames (i.e. an int or a string).

    Returns decorator check_success function.
    """
    def wrap_check_success(return_val):
        LOGGER.log(level, "poll() calls check_success(%s)", return_val)
        return check_success(return_val)
    return wrap_check_success


def poll_killer(*args, **kwargs):
    """
    Guarantees that, even a blocking target, respects the timeout value.

    :param timeout: (mandatory)

    Otherwise, all arguments are the same as poll.

    Run's the target in a second process, so even if it blocks, the specified timeout is
    still respected. Protection is provided via a process and a timeout. 

    WARNING: the target() function must be picklable. Due to how multiprocessing works.
    """
    # TODO: Add ability to retrive log messages from the second process for log and log_error.
    # I'm not sure it's possible with apply_async, unless perhaps log and log_error are created
    # as Queues? Need to work this out.
    if not kwargs.get('timeout'):
        raise TypeError('timeout parameter missing')
    else:
        timeout = kwargs['timeout']
        pool = multiprocessing.Pool(processes=1)
        async_result = pool.apply_async(func=poll, args=args, kwds=kwargs)
        try:
            result = async_result.get(timeout=timeout)
        except multiprocessing.TimeoutError:
            _msg = "poll()'s target blocked and failed to return within %s second(s)." % timeout
            raise TimeoutException(_msg, values=[])
        else:
            return result


def _check_max_tries(max_tries, tries, values, last_item):
    if max_tries is not None and tries >= max_tries:
        _msg = "polls()'s target failed check_sucess() after %s calls" % max_tries
        raise MaxCallException(msg=_msg, values=values, last=last_item)


def poll(target, step, args=(), kwargs=None, timeout=None, max_tries=None, check_success=is_truthy,
         step_function=step_constant, ignore_exceptions=(), poll_forever=False, collect_values=None,
         log=logging.NOTSET, log_error=logging.NOTSET):
    """Poll by calling a target function until a certain condition is met. You must specify at least a target
    function to be called and the step -- base wait time between each function call.

    :param step: Step defines the amount of time to wait (in seconds)

    :param args: Arguments to be passed to the target function

    :type kwargs: dict
    :param kwargs: Keyword arguments to be passed to the target function

    :param timeout: The target function will be called until the time elapsed is greater than the maximum timeout
    (in seconds). NOTE that the actual execution time of the function *can* exceed the time specified in the timeout.
    For instance, if the target function takes 10 seconds to execute and the timeout is 21 seconds, the polling
    function will take a total of 30 seconds (two iterations of the target --20s which is less than the timeout--21s,
    and a final iteration)

    :param max_tries: Maximum number of times the target function will be called before failing

    :param check_success: A callback function that accepts the return value of the target function. It should
    return true if you want the polling function to stop and return this value. It should return false if you want it
    to continue executing. The default is a callback that tests for truthiness (anything not False, 0, or empty
    collection).

    :param step_function: A callback function that accepts each iteration's "step." By default, this is constant,
    but you can also pass a function that will increase or decrease the step. As an example, you can increase the wait
    time between calling the target function by 10 seconds every iteration until the step is 100 seconds--at which
    point it should remain constant at 100 seconds

    >>> def my_step_function(step):
    >>>     step += 10
    >>>     return max(step, 100)

    :type ignore_exceptions: tuple
    :param ignore_exceptions: You can specify a tuple of exceptions that should be caught and ignored on every
    iteration. If the target function raises one of these exceptions, it will be caught and the exception
    instance will be pushed to the queue of values collected during polling. Any other exceptions raised will be
    raised as normal.

    :param poll_forever: If set to true, this function will retry until an exception is raised or the target's
    return value satisfies the check_success function. If this is not set, then a timeout or a max_tries must be set.

    :type collect_values: Queue
    :param collect_values: By default, polling will create a new Queue to store all of the target's return values.
    Optionally, you can specify your own queue to collect these values for access to it outside of function scope.

    :type log: int or str, one of logging._levelNames
    :opt param log: By default, return values passed to check_success are not logged. However, if this param is
    set to a log level greater than NOTSET, then the return values passed to check_success will be logged.
    This is done by using the decorator log_value.

    :type log_error: int or str, one of logging._levelNames
    :opt param log_level: If ignore_exception has been set, you might want to log the exceptions that are
    ignored. If the log_error level is greater than NOTSET, then any caught exceptions will be logged at that
    level. Note: the logger.exception() function is not used. That would print the stacktrace in the logs. Because
    you are ignoring these exceptions, it seems unlikely that'd you'd want a full stack trace for each exception.
    However, if you do what this, you can retrieve the exceptions using the collect_values parameter.

    :return: Polling will return first value from the target function that meets the condions of the check_success
    callback. By default, this will be the first value that is not None, 0, False, '', or an empty collection.
    """

    assert (timeout is not None or max_tries is not None) or poll_forever, \
        ('You did not specify a maximum number of tries or a timeout. Without either of these set, the polling '
         'function will poll forever. If this is the behavior you want, pass "poll_forever=True"')

    assert not ((timeout is not None or max_tries is not None) and poll_forever), \
        'You cannot specify both the option to poll_forever and max_tries/timeout.'

    kwargs = kwargs or dict()
    values = collect_values or Queue()

    max_time = time.time() + timeout if timeout else None
    tries = 0

    if log:
        check_success = log_value(check_success, level=log)

    last_item = None
    while True:

        _check_max_tries(max_tries=max_tries, tries=tries, values=values,
                         last_item=last_item)

        try:
            val = target(*args, **kwargs)
            last_item = val
        except ignore_exceptions as e:
            last_item = e

            if log_error: # NOTSET is 0, so it'll evaluate to False.
                LOGGER.log(log_error, "poll() ignored exception %r", e)

        else:
            # Condition passes, this is the only "successful" exit from the polling function
            if check_success(val):
                return val

        values.put(last_item)
        tries += 1

        # Check the max tries at this point so it will not sleep before raising the exception
        _check_max_tries(max_tries=max_tries, tries=tries, values=values,
                         last_item=last_item)

        # Check the time after to make sure the poll function is called at least once
        if max_time is not None and time.time() >= max_time:
            _msg = "polls()'s target failed to return within %s seconds" % timeout
            raise TimeoutException(msg=_msg, values=values, last=last_item)

        time.sleep(step)
        step = step_function(step)

