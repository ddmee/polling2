Future extensions
=================

This pages lists ideas for what could be added in future to extend the modules functionality.


- Add poll_killer(). Specify a hard timeout so that if the function being polled blocks and doesn't return, poll_killer() will raise a timeout.
- Add an option to do via multiprocessing.
- Add an option to do via threading - probably the default option.
- Add poll_chain(). Have reason to poll a bunch of functions in a row? poll_chain() allows you to chain a bunch of polling functions together.
- Allow step to be specificed as 0, so that we can poll continously. (Perhaps it's best to write a poll_continous() method.)
