.. Polling2 documentation master file, created by
   sphinx-quickstart on Thu Sep 10 11:49:54 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Polling2: Never write another polling function
==============================================

Release v\ |version|.

.. image:: https://travis-ci.com/ddmee/polling2.svg?branch=master
    :target: https://travis-ci.com/ddmee/polling2

.. image:: https://img.shields.io/pypi/dm/polling2.svg
    :target: https://pypi.org/project/polling2

.. image:: https://img.shields.io/pypi/pyversions/polling2.svg
    :target: https://pypi.org/project/polling2

.. image:: https://readthedocs.org/projects/polling2/badge/?version=latest
    :target: https://polling2.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

**Polling2** is a powerful python utility used to wait for a function to return when the specified condition is met.

Install
-------

polling2_ is available from Pypi.::

    python -m pip install polling2

.. _polling2: https://pypi.org/project/polling2/

.. toctree::
    :maxdepth: 2

    install


Examples
--------

**Watch polling do some arbitrary dances**::

    >> import polling2, time
    >> # Wait until the number of seconds (ignoring milliseconds) is divisible by 5.
    >>  polling2.poll(target=time.time, check_success=lambda x: int(x) % 5 == 0, step=0.5, timeout=6)
    1599737060.4507122
    >> # Lets use the decorator version to create a function that waits until the next even second.
    >> @polling2.poll_decorator(check_success=lambda x: int(x) % 2 == 0, step=0.5, timeout=6)
    ... def even_time():
    ...     return time.time()
    >> even_time()
    1599737080.016323
    >> even_time()
    1599737082.035758


View all the examples:

.. toctree::
    :maxdepth: 3

    examples

API
-----------------------------

.. toctree::
   :maxdepth: 2

   api


Contributor Guide
---------------------

If you want to contribute to the project...

.. toctree::
   :maxdepth: 3

   dev/contributing
   dev/authors
   dev/future
   dev/code_of_conduct

Release notes
--------------

The change log for each released version.

.. toctree::
   :maxdepth: 2

   release-notes


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
