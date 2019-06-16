import logging
import sys
import time
import unittest

# Some minor diff between py2 and py3.
try:
    import queue
except ImportError:
    import Queue as queue

from mock import patch, Mock
import pytest

import polling2


def is_py_34():
    """Returns True if the version of python running the tests is 3.4."""
    return sys.version_info.major == 3 and sys.version_info.minor == 4


def return_it(*args):
    """For the benefit of multiprocessing pickable target.
    Returns a tuple of the args.
    """
    return args


class SideEffect(object):
    """
    Create a callable object which returns the next item in the iterable passed
    to the constructor.
    """
    def __init__(self, iterable):
        self._iter = iter(iterable)

    def __call__(self):
        return next(self._iter)


FALSE_FALSE_TRUE = SideEffect([False, False, True])


class TestPoll(object):

    def test_import(self):
        """Test that you can import via correct usage"""
        import polling2
        from polling2 import poll, poll_killer

        assert poll
        assert poll_killer
        assert polling2

    def test_arg_no_arg(self):
        """Tests various permutations of calling with invalid args"""
        with pytest.raises(TypeError):
            polling2.poll()

    def test_arg_no_step(self):
        with pytest.raises(TypeError):
            polling2.poll(lambda: True)

    def test_no_poll_forever_or_maxtries(self):
        """No error raised without specifying poll_forever or a timeout/max_tries"""
        with pytest.raises(AssertionError):
            polling2.poll(lambda: True, step=1)

    def test_poll_forever_with_timeout_max_tries(self):
        with pytest.raises(AssertionError):
            polling2.poll(lambda: True, step=1, timeout=1, max_tries=1, poll_forever=True)

    def test_type_error_when_misspelt_argnames(self):
        with pytest.raises(TypeError):
            polling2.poll(target=lambda: None, step=2, timeout=10, check_sucess=lambda rv: rv is None)

    def test_valid_arg_options(self):
        # Valid options
        polling2.poll(lambda: True, step=1, poll_forever=True)
        polling2.poll(lambda: True, step=1, timeout=1)
        polling2.poll(lambda: True, step=1, max_tries=1)
        polling2.poll(lambda: True, step=1, timeout=1, max_tries=1)

    @patch('time.sleep', return_value=None)
    @patch('time.time', return_value=0)
    def test_timeout_exception(self, patch_sleep, patch_time):

        # Since the timeout is < 0, the first iteration of polling should raise the error if max timeout < 0
        try:
            polling2.poll(lambda: False, step=10, timeout=-1)
        except polling2.TimeoutException as e:
            assert e.values.qsize() == 1, 'There should have been 1 value pushed to the queue of values'
            assert e.last is False, 'The last value was incorrect'
        else:
            assert False, 'No timeout exception raised'

        # Test happy path timeout
        val = polling2.poll(lambda: True, step=0, timeout=0)
        assert val is True, 'Val was: {} != {}'.format(val, True)

    def test_max_call_exception(self):
        """
        Test that a MaxCallException will be raised 
        """
        tries = 100
        try:
            polling2.poll(lambda: False, step=0, max_tries=tries)
        except polling2.MaxCallException as e:
            assert e.values.qsize() == tries, 'Poll function called the incorrect number of times'
            assert e.last is False, 'The last value was incorrect'
        else:
            assert False, 'No MaxCallException raised'

    def test_max_call_no_sleep(self):
        """
        Test that a MaxCallException is raised without sleeping after the last call
        """
        tries = 2
        sleep = 0.1
        start_time = time.time()

        with pytest.raises(polling2.MaxCallException):
            polling2.poll(lambda: False, step=sleep, max_tries=tries)
        assert time.time() - start_time < tries * sleep, 'Poll function slept before MaxCallException'

    def test_ignore_specified_exceptions(self):
        """
        Test that ignore_exceptions tuple will ignore exceptions specified.
        Should throw any errors not in the tuple.
        """
        # raises_errors is a function that returns 3 different things, each time it is called.
        # First it raises a ValueError, then EOFError, then a TypeError.
        raises_errors = Mock(return_value=True, side_effect=[ValueError, EOFError, RuntimeError])
        with pytest.raises(RuntimeError):
            # We are ignoring the exceptions other than a TypeError.
            polling2.poll(target=raises_errors, step=0.1, max_tries=3,
                          ignore_exceptions=(ValueError, EOFError))
        assert raises_errors.call_count == 3


@pytest.mark.skipif(is_py_34(), reason="pytest logcap fixture isn't available on 3.4")
class TestPollLogging(object):

    def test_logs_response_at_debug(self, caplog):
        """
        Test that the log_value decorator will log values returned to a check_success function.
        """
        with caplog.at_level(logging.DEBUG):
            polling2.poll(target=lambda: True, step=0.1, max_tries=1, log=logging.DEBUG)
            assert len(caplog.records) == 1, "Should only be one log record."
            record = caplog.records[0]
            assert record.levelname == 'DEBUG'
            assert record.message == "poll() calls check_success(True)"

    def test_logs_response_change_level(self, caplog):
        """
        Test that the log parameter controls the logging level in poll function
        """
        with caplog.at_level(logging.DEBUG):
            polling2.poll(target=lambda: True, step=0.1, max_tries=1, log=logging.INFO)
            assert len(caplog.records) == 1, "Should only be one log record."
            record = caplog.records[0]
            assert record.levelname == 'INFO'
            assert record.message == "poll() calls check_success(True)"

    def test_default_is_not_log(self, caplog):
        """
        Shouldn't log anything unless explicitly asked to do so.
        """
        with caplog.at_level(logging.DEBUG):
            polling2.poll(target=lambda: True, step=0.1, max_tries=1)
            assert len(caplog.records) == 0, "Should not be any log records"

    def test_log_error_default_is_not_log(self, caplog):
        """
        Shouldn't log anything unless explicitly asked to do so.
        """
        raises_errors = Mock(side_effect=ValueError('msg is this'))
        with caplog.at_level(logging.DEBUG), pytest.raises(polling2.MaxCallException):
            polling2.poll(target=raises_errors, ignore_exceptions=(ValueError),
                          step=0.1, max_tries=2)
            assert len(caplog.records) == 0, "Wrong number of log records."
            # Test that logging.NOTSET does not print log records either.
            polling2.poll(target=raises_errors, ignore_exceptions=(ValueError),
                          step=0.1, max_tries=2, log_error=logging.NOTSET)
            assert len(caplog.records) == 0, "Wrong number of log records."

    def test_log_error_set_at_debug_level(self, caplog):
        """
        Test that when the log_error parameter is set to debug level, the ignored
        errors are sent to the logger.
        """
        raises_errors = Mock(side_effect=[ValueError('msg this'), RuntimeError('this msg')])
        with caplog.at_level(logging.DEBUG), pytest.raises(polling2.MaxCallException):
            polling2.poll(target=raises_errors, ignore_exceptions=(ValueError, RuntimeError),
                          step=0.1, max_tries=2, log_error=logging.DEBUG)
        assert len(caplog.records) == 2, "Wrong number of log records."
        assert caplog.records[0].message == "poll() ignored exception ValueError('msg this',)"
        assert caplog.records[1].message == "poll() ignored exception RuntimeError('this msg',)"


class TestPollKiller(object):
    """
    Test that a blocking target is forcibly returned when poll_killer() is used.
    """
    def test_blocking_call_raises_timeout_exception(self):
        """
        If call a target that sleeps for 10 seconds, but the timeout is specified
        to be 1 second, then a TimeoutException should be raised even though the
        target has effectively blocked the timeout handling of poll().
        """
        with pytest.raises(polling2.TimeoutException) as excinfo:
            polling2.poll_killer(target=time.sleep, step=0.01, args=(10,), timeout=1)
        expected_msg = "poll()'s target blocked and failed to return within 1 second(s)."
        assert expected_msg == str(excinfo.value)

    def test_works_with_no_keywords(self):
        """
        poll_killer() uses *arg, **kwargs to pass parameters through to poll().
        We need to be sure that if the user of poll_killer() uses positionl arguments
        only, the function behaves as expected.
        """
        with pytest.raises(polling2.TimeoutException) as excinfo:
            # poll() sig is target, step, args, kwargs, timeout
            polling2.poll_killer(time.sleep, 0.01, (10,), {}, timeout=1)
        expected_msg = "poll()'s target blocked and failed to return within 1 second(s)."
        assert expected_msg == str(excinfo.value)

    def test_can_retrieve_return_value_from_a_successful_target(self):
        """
        If the target() returns a value that satifies the check_success() then
        poll_killer() should return that value.
        """
        assert polling2.poll_killer(target=return_it, step=0.1, timeout=1, args=('hello',)) == ('hello',)

    def test_can_get_all_return_values_using_collect_values(self):
        """
        If a user specifies collect_values as True, can they get the values back?
        """
        with pytest.raises(polling2.MaxCallException) as excinfo:
            polling2.poll(target=FALSE_FALSE_TRUE, step=0.1, timeout=1, max_tries=2)

        the_queue = excinfo.value.values
        assert isinstance(the_queue, queue.Queue)

        for x in range(3):
            if x < 2:
                # first 2 items (the only 2 items) should be the value false
                assert the_queue.get(block=False) is False
            else:
                # The 3rd time get() is called, we should get this exception
                with pytest.raises(queue.Empty):
                    the_queue.get(block=False)

    def test_can_use_log_error(self):
        """
        Test that the logged-exceptions messages make their way into the main processe's logger.
        """
        assert False

    def test_can_use_log(self):
        """
        Same as above, except for the return values.
        """
        assert False
