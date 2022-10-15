import logging
import re
import sys
import time
import unittest

import pytest
from mock import Mock, patch

import polling2

WRONG_LOG_NUM = "Wrong number of log records."
WRONG_LAST_VAL = "The last value was incorrect"


def is_py_34():
    """Returns True if the version of python running the tests is 3.4."""
    return sys.version_info.major == 3 and sys.version_info.minor == 4


class TestPoll(object):
    def test_import(self):
        """Test that you can import via correct usage"""
        import polling2
        from polling2 import poll, poll_decorator

        assert poll
        assert polling2
        assert poll_decorator

    def test_no_poll_forever_or_maxtries(self):
        """No error raised without specifying poll_forever or a timeout/max_tries"""
        with pytest.raises(AssertionError):
            polling2.poll(lambda: True, step=1)

    def test_decorator_no_poll_forever_or_maxtries(self):
        """No error raised without specifying poll_forever or a timeout/max_tries"""
        with pytest.raises(AssertionError):

            @polling2.poll_decorator(step=1)
            def throwaway():
                return True

            throwaway()

    def test_poll_forever_with_timeout_max_tries(self):
        with pytest.raises(AssertionError):
            polling2.poll(
                lambda: True, step=1, timeout=1, max_tries=1, poll_forever=True
            )

    def test_decorator_poll_forever_with_timeout_max_tries(self):
        with pytest.raises(AssertionError):

            @polling2.poll_decorator(step=1, timeout=1, max_tries=1, poll_forever=True)
            def throwaway():
                return True

            throwaway()

    def test_valid_arg_options(self):
        # Valid options
        polling2.poll(lambda: True, step=1, poll_forever=True)

        @polling2.poll_decorator(step=1, poll_forever=True)
        def throwaway():
            return True

        throwaway()

        polling2.poll(lambda: True, step=1, timeout=1)

        @polling2.poll_decorator(step=1, timeout=1)
        def throwaway():
            return True

        throwaway()

        polling2.poll(lambda: True, step=1, max_tries=1)

        @polling2.poll_decorator(step=1, max_tries=1)
        def throwaway():
            return True

        throwaway()

        polling2.poll(lambda: True, step=1, timeout=1, max_tries=1)

        @polling2.poll_decorator(step=1, timeout=1, max_tries=1)
        def throwaway():
            return True

        throwaway()

    @patch("time.sleep", return_value=None)
    @patch("time.time", return_value=0)
    def test_timeout_exception(self, patch_sleep, patch_time):

        # Since the timeout is < 0, the first iteration of polling should raise the error if max timeout < 0
        try:
            polling2.poll(lambda: False, step=10, timeout=-1)
        except polling2.TimeoutException as e:
            assert (
                e.values.qsize() == 1
            ), "There should have been 1 value pushed to the queue of values"
            assert e.last is False, WRONG_LAST_VAL
        else:
            assert False, "No timeout exception raised"

        # Test happy path timeout
        val = polling2.poll(lambda: True, step=0, timeout=0)
        assert val is True, "Val was: {} != {}".format(val, True)

    @patch("time.sleep", return_value=None)
    @patch("time.time", return_value=0)
    def test_decorator_timeout_exception(self, patch_sleep, patch_time):

        # Since the timeout is < 0, the first iteration of polling should raise the error if max timeout < 0
        try:

            @polling2.poll_decorator(step=10, timeout=-1)
            def throwaway():
                return False

            throwaway()
        except polling2.TimeoutException as e:
            assert (
                e.values.qsize() == 1
            ), "There should have been 1 value pushed to the queue of values"
            assert e.last is False, WRONG_LAST_VAL
        else:
            assert False, "No timeout exception raised"

        # Test happy path timeout
        @polling2.poll_decorator(step=0, timeout=0)
        def throwaway():
            return True

        val = throwaway()
        assert val is True, "Val was: {} != {}".format(val, True)

    def test_max_call_exception(self):
        """
        Test that a MaxCallException will be raised
        """
        tries = 100
        try:
            polling2.poll(lambda: False, step=0, max_tries=tries)
        except polling2.MaxCallException as e:
            assert (
                e.values.qsize() == tries
            ), "Poll function called the incorrect number of times"
            assert e.last is False, WRONG_LAST_VAL
        else:
            assert False, "No MaxCallException raised"

    def test_decorator_max_call_exception(self):
        """
        Test that a MaxCallException will be raised
        """
        tries = 100
        try:

            @polling2.poll_decorator(step=0, max_tries=tries)
            def throwaway():
                return False

            throwaway()
        except polling2.MaxCallException as e:
            assert (
                e.values.qsize() == tries
            ), "Poll function called the incorrect number of times"
            assert e.last is False, WRONG_LAST_VAL
        else:
            assert False, "No MaxCallException raised"

    def test_max_call_no_sleep(self):
        """
        Test that a MaxCallException is raised without sleeping after the last call
        """
        tries = 2
        sleep = 0.1
        start_time = time.time()

        with pytest.raises(polling2.MaxCallException):
            polling2.poll(lambda: False, step=sleep, max_tries=tries)
        assert (
            time.time() - start_time < tries * sleep
        ), "Poll function slept before MaxCallException"

    def test_decorator_max_call_no_sleep(self):
        """
        Test that a MaxCallException is raised without sleeping after the last call
        """
        tries = 2
        sleep = 0.1
        start_time = time.time()

        with pytest.raises(polling2.MaxCallException):

            @polling2.poll_decorator(step=sleep, max_tries=tries)
            def throwaway():
                return False

            throwaway()
        assert (
            time.time() - start_time < tries * sleep
        ), "Poll function slept before MaxCallException"

    def test_ignore_specified_exceptions(self):
        """
        Test that ignore_exceptions tuple will ignore exceptions specified.
        Should throw any errors not in the tuple.
        """
        # raises_errors is a function that returns 3 different things, each time it is called.
        # First it raises a ValueError, then EOFError, then a TypeError.
        raises_errors = Mock(
            return_value=True, side_effect=[ValueError, EOFError, RuntimeError]
        )
        with pytest.raises(RuntimeError):
            # We are ignoring the exceptions other than a TypeError.
            polling2.poll(
                target=raises_errors,
                step=0.1,
                max_tries=3,
                ignore_exceptions=(ValueError, EOFError),
            )
        assert raises_errors.call_count == 3

    def test_decorator_ignore_specified_exceptions(self):
        """
        Test that ignore_exceptions tuple will ignore exceptions specified.
        Should throw any errors not in the tuple.
        """
        # raises_errors is a function that returns 3 different things, each time it is called.
        # First it raises a ValueError, then EOFError, then a TypeError.
        raises_errors = Mock(
            return_value=True, side_effect=[ValueError, EOFError, RuntimeError]
        )
        # Seems to be an issue on python 2 with functools.wraps and Mocks(). See https://stackoverflow.com/a/22204742/4498470
        # Just going to ignore this until someone complains.
        raises_errors.__name__ = "raises_errors"
        with pytest.raises(RuntimeError):
            # We are ignoring the exceptions other than a TypeError.
            # Note, instead of using @, calling poll_decorator like a traditional function.
            polling2.poll_decorator(
                step=0.1, max_tries=3, ignore_exceptions=(ValueError, EOFError)
            )(target=raises_errors)()
        assert raises_errors.call_count == 3

    def test_check_is_value(self):
        """
        Test that is_value() function can be used to create custom checkers.
        """
        result = polling2.poll(
            target=lambda: None,
            step=0.1,
            max_tries=1,
            check_success=polling2.is_value(None),
        )
        assert result is None
        result = polling2.poll(
            target=lambda: False,
            step=0.1,
            max_tries=1,
            check_success=polling2.is_value(False),
        )
        assert result is False
        result = polling2.poll(
            target=lambda: 123,
            step=0.1,
            max_tries=1,
            check_success=polling2.is_value(123),
        )
        assert result == 123
        with pytest.raises(polling2.MaxCallException):
            polling2.poll(
                target=lambda: 123,
                step=0.1,
                max_tries=1,
                check_success=polling2.is_value(444),
            )

    def test_decorator_check_is_value(self):
        """
        Test that is_value() function can be used to create custom checkers.
        """

        @polling2.poll_decorator(
            step=0.1, max_tries=1, check_success=polling2.is_value(None)
        )
        def throwaway():
            return None

        assert throwaway() is None

        @polling2.poll_decorator(
            step=0.1, max_tries=1, check_success=polling2.is_value(False)
        )
        def throwaway():
            return False

        assert throwaway() is False

        @polling2.poll_decorator(
            step=0.1, max_tries=1, check_success=polling2.is_value(123)
        )
        def throwaway():
            return 123

        assert throwaway() == 123

        with pytest.raises(polling2.MaxCallException):

            @polling2.poll_decorator(
                step=0.1, max_tries=1, check_success=polling2.is_value(444)
            )
            def throwaway():
                return 123

            throwaway()

    def test_decorator_uses_wraps(self):
        """
        Test that the function name is not replaced when poll_decorator() is used.
        Thus we should be using functools.wraps() correctly.
        """

        @polling2.poll_decorator(step=0.1, max_tries=1)
        def throwaway():
            """Is the doc retained?"""
            return True

        assert throwaway.__name__ == "throwaway", "decorated function name has changed"
        assert (
            throwaway.__doc__ == "Is the doc retained?"
        ), "decorated function doc has changed"


@pytest.mark.skipif(is_py_34(), reason="pytest logcap fixture isn't available on 3.4")
class TestPollLogging(object):
    def test_logs_call(self, caplog):
        """
        Test that basic information about the call to poll() is always logged.
        """
        with caplog.at_level(logging.DEBUG):
            polling2.poll(target=lambda: True, step=0.1, max_tries=1)
            assert len(caplog.records) == 1, "Should only be one log record."
            record = caplog.records[0]
            assert record.levelname == "DEBUG"
            pattern = r"""
                        # Note, in verbose mode, need to explicitly include whitespace
                        # by putting blackslash in front of anywhere there should be whitespace.
                        Begin\ poll\(
                        target=<function.*<lambda>\ at\ 0x[0-9A-Za-z]+>,  # contains pointer to the function.
                        \ step=0\.1,
                        \ timeout=None,
                        \ max_tries=1,
                        \ poll_forever=False
                        \)
                    """
            # Assert we have a match, which means the record is like the regular expression.
            assert re.search(pattern=pattern, string=record.message, flags=re.VERBOSE)

    def test_logs_response_at_debug(self, caplog):
        """
        Test that the log_value decorator will log values returned to a check_success function.
        """
        with caplog.at_level(logging.DEBUG):
            polling2.poll(target=lambda: True, step=0.1, max_tries=1, log=logging.DEBUG)
            assert len(caplog.records) == 2, "Should only be two log records."
            record = caplog.records[1]
            assert record.levelname == "DEBUG"
            assert record.message == "poll() calls check_success(True)"

    def test_logs_response_change_level(self, caplog):
        """
        Test that the log parameter controls the logging level in poll function
        """
        with caplog.at_level(logging.DEBUG):
            polling2.poll(target=lambda: True, step=0.1, max_tries=1, log=logging.INFO)
            assert len(caplog.records) == 2, "Should only be two log record."
            record = caplog.records[1]
            assert record.levelname == "INFO"
            assert record.message == "poll() calls check_success(True)"

    def test_default_is_not_log(self, caplog):
        """
        Shouldn't log anything unless explicitly asked to do so. Except for Begin poll()
        """
        with caplog.at_level(logging.DEBUG):
            polling2.poll(target=lambda: True, step=0.1, max_tries=1)
            assert len(caplog.records) == 1, "Should ony be one log records"
            assert "Begin poll(" in caplog.records[0].msg

    def test_log_error_default_is_not_log(self, caplog):
        """
        Shouldn't log anything unless explicitly asked to do so. Except for Begin poll()
        """
        raises_errors = Mock(side_effect=ValueError("msg is this"))
        with caplog.at_level(logging.DEBUG), pytest.raises(polling2.MaxCallException):
            polling2.poll(
                target=raises_errors,
                ignore_exceptions=(ValueError),
                step=0.1,
                max_tries=2,
            )
            assert len(caplog.records) == 1, WRONG_LOG_NUM
            # Test that logging.NOTSET does not print log records either.
            polling2.poll(
                target=raises_errors,
                ignore_exceptions=(ValueError),
                step=0.1,
                max_tries=2,
                log_error=logging.NOTSET,
            )
            assert len(caplog.records) == 2, WRONG_LOG_NUM

    def test_log_error_set_at_debug_level(self, caplog):
        """
        Test that when the log_error parameter is set to debug level, the ignored
        errors are sent to the logger.
        """
        raises_errors = Mock(
            side_effect=[ValueError("msg this"), RuntimeError("this msg")]
        )
        with caplog.at_level(logging.DEBUG), pytest.raises(polling2.MaxCallException):
            polling2.poll(
                target=raises_errors,
                ignore_exceptions=(ValueError, RuntimeError),
                step=0.1,
                max_tries=2,
                log_error=logging.DEBUG,
            )
        assert len(caplog.records) == 3, WRONG_LOG_NUM
        assert caplog.records[1].message.startswith(
            "poll() ignored exception ValueError('msg this"
        )
        assert caplog.records[2].message.startswith(
            "poll() ignored exception RuntimeError('this msg"
        )
