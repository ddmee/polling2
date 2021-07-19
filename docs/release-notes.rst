Release notes
=============

0.4.8
-----
- NEW API addition: poll_decorator(). Per user-request, you can now use @poll_decorator() as a way to wrap a function with poll().
- The api otherwise remains the same. See the new function poll_decorator(). All options and arguments remain equivalent in poll()/poll_decorator(). Fully backward compatible change.

0.4.7
-----

- No API changes. Updated documentation to state that timeout=0 or timeout=None is equivalent to setting poll_forever=True.

0.4.6
-----

- No API changes. Presentation/documentations changes only. Should pose no backwards compatibility risk.
- Added /docs directory written for sphinx. Setup a readthedocs site from the sphinx build.
- Moved README contents to be largely inside the /docs/.
- Updated some of the comments strings inside polling2 module.

0.4.5
-----

'Begin poll(*)' message is logged when poll() is called. Hopefully this means the user doesn't feel the need to write a message before every call to poll() to indicate how long the poll() might take.

0.4.4
-----

Add is_value() function. A function that allows a user to easily build a custom checker, like is_truthy(), but for any value.

0.4.3
-----

Add log_error parameter to the poll signature. Enables logging of ignored exceptions.

0.4.2
-----

Add log_value() decorator and log parameter to poll signature. Enables logging of return_values.

0.4.0
-----

- Fixed polling function from waiting another sleep whenever the max_tries value has reached zero.
- Remove test-only dependencies from requirements to install the package.
- No longer testing on python 2.6. Add support for travis testing on python 3.6 and pypy 3.5.
- Creation of polling2, forked from polling as previous maintainer seems to be ignoring issues and pull-requests.
- Remove ```*a, **k``` from poll signature. This allows Type errors to be raised if caller spells arguments into correctly, making bugs easier to find.

0.3.0
-----

Support Python 3.4+

0.2.0
-----

- Allow users to access a "last" attribute on the exceptions. This should hold the last evaluated value, which is the more common use case than getting the first value. 
- Fix a bug that actually ran 1 more time than value specified by max_tries

0.1.0
-----

First version