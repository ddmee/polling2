Contributing
============

Contributions are very welcome. This library is under active development.

It's important that any changes work on both python 2 and python 3.

Development Setup
-----------------

You can get your development environment running cloning the repository. Please test your changes. Do note any PRs you open, Travis will run and report the test results. So perhaps you can just rely on opening a PR::

    # install lib, but use system links from the repo into sitepackages.
    python setup.py develop
    # install test dependenices.
    python setup.py test
    # run the tests
    pytest tests

You can also use tox, which will run the tests for you.

    pip install tox
    tox

Pre-commit is also used to help auto-format things and do some checks before each commit.

    pip install pre-commit
    pre-commit install

Now pre-commit will run automatically on ``git commit``.

Note, there are also build jobs that run when a PR is opened on github. They provide extra checks that are easier to do on the CI pipeline rather than locally. Ultimately, the CI pipeline controls whether a PR is good enough to merge into master.
