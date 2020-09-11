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

.. image:: http://hits.dwyl.io/ddmee/polling2.svg
    :target: https://pypi.org/project/polling2

.. image:: https://img.shields.io/pypi/pyversions/polling2.svg
    :target: https://pypi.org/project/polling2

**Polling2** is a powerful python utility used to wait for a function to return when the specified condition is met.

Install
-------
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
