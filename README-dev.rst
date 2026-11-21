Setup for development
=====================

Install `Pixi <https://pixi.sh/>`_ 0.84.2 or newer and external
`uv <https://docs.astral.sh/uv/>`_. Keep both commands on ``PATH``; uv is not
installed by Pixi.

The Conda test environments use Mira's private Conda channel. Authenticate with
your own JFrog credentials before using them::

    pixi auth login --username <user@mirageoscience.com> --password <user-token> mirageoscienceltd.jfrog.io

Do not put credentials in the repository. The token may appear in shell history
and process listings.

Environments and tests
^^^^^^^^^^^^^^^^^^^^^^

The lock covers Windows and Linux with Python 3.12, 3.13 and 3.14. The
``pypi-mira`` environments use published Mira PyPI packages; ``conda-mira``
environments use their published Conda packages. Install and test the Python
3.12 PyPI environment with::

    pixi install --locked -e pypi-mira
    pixi run --frozen -e pypi-mira install
    pixi run --frozen -e pypi-mira test

Use ``conda-mira`` to test the Conda packages. The ``test-pyvers`` task runs
the PyPI tests on all three supported Python versions. The ``install`` task
installs this checkout in editable mode and checks its dependencies.

The lock test verifies the selected Mira package sources in each environment;
it permits unrelated PyPI dependencies. Run it with::

    pixi run --frozen -e pypi-mira python -m pytest -q tests/lock_test.py

Updating dependencies
^^^^^^^^^^^^^^^^^^^^^

After changing dependencies, solve and validate the lock, then run the
environment checks::

    pixi lock
    pixi lock --check
    pixi install --locked -e pypi-mira
    pixi run --frozen -e pypi-mira install
    pixi run --frozen -e pypi-mira test

Commit ``pixi.lock`` with the manifest changes. Keep the published Conda and
PyPI environments separate; this meta-package does not use Git dependency
environments.

Git hooks
^^^^^^^^^

Install `prek <https://prek.j178.dev/>`_ and use the repository hooks::

    prek install
    prek run --all-files

Copyright
^^^^^^^^^

Copyright (c) 2024-2026 Mira Geoscience Ltd.
