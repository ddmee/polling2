Contributing
============

Contributions are very welcome. This library is under active development.

It's important that any changes work on both python 2 and python 3.

Development Setup
----------

You can get your development environment running cloning the repository. Please test your changes. Do note any PRs you open, Travis will run and report the test results. So perhaps you can just rely on opening a PR::

    # install lib, but use system links from the repo into sitepackages.
    python setup.py develop
    # install test dependenices.
    python setup.py test
    # run the tests
    pytest tests
