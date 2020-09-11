The API
=======

.. module:: polling2

This part of the documentation covers all the interfaces of Requests. For
parts where Requests depends on external libraries, we document the most
important right here and provide links to the canonical documentation.


Poll Method
-----------

The main method is the poll method.

.. autofunction:: poll


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
