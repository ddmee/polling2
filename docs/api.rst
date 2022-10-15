The API
=======

.. module:: polling2

This part of the documentation covers all the interfaces of polling2. polling2
depends on no external libraries and should run any version of python 2 or 3.


Poll Method
-----------

The main method is the poll method.

.. autofunction:: poll


Poll Decorator
--------------

There is also an equivalent decorator method. It's interface is essentially the same as poll().
But benefits from allowing you to write the polling functionality with decorator syntax.

.. autofunction:: poll_decorator


Helper Methods
--------------

There are some other supplemental methods that can help out.

.. autofunction:: step_constant
.. autofunction:: step_linear_double
.. autofunction:: is_truthy
.. autofunction:: is_value
.. autofunction:: log_value

Exceptions
----------

.. autoexception:: PollingException
.. autoexception:: TimeoutException
.. autoexception:: MaxCallException
