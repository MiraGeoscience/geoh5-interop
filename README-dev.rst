Setup for development
=====================

.. contents:: Table of Contents
   :local:
   :depth: 2

Prerequisites
^^^^^^^^^^^^^

* **Pixi and uv:** Install `Pixi <https://pixi.sh/>`_ 0.84.2 and external
  `uv <https://docs.astral.sh/uv/>`_. Keep both commands on ``PATH``; uv is not
  installed by Pixi.
* **prek:** Install `prek <https://prek.j178.dev/>`_ for the configured Git
  hooks.
* **IDE interpreter:** Configure your IDE to use the interpreter inside
  ``.pixi/envs/default`` and exclude ``.pixi`` from source indexing.
  For **PyCharm**, follow Pixi's `JetBrains integration guide
  <https://pixi.prefix.dev/latest/integration/editor/jetbrains/>`_.
* **JFrog authentication:** authenticate with Mira Artifactory using your
  own credentials::

      pixi auth login mirageoscienceltd.jfrog.io

  Never add credentials to ``pixi.toml`` or ``pixi.lock``.

.. note:: External contributors using Pixi

   The ``mira-*`` environments require access to Mira's private Conda and
   PyPI development repositories. Request access from the repository
   maintainers to use these environments. GitHub does not provide JFrog
   secrets to workflows triggered by fork pull requests, so those jobs cannot
   authenticate. Never share a JFrog token in a pull request or issue.

Install and test
^^^^^^^^^^^^^^^^

The shared lock covers Windows and Linux with multiple Python versions::

    pixi install --locked -e pypi-mira
    pixi run --frozen -e pypi-mira install
    pixi run --frozen -e pypi-mira test

The ``install`` task installs this checkout in editable mode without changing
locked dependencies, then checks package compatibility.

The ``conda-mira-rt`` and ``pypi-mira-rt`` environments omit test and lint
tools.

On Windows, install the locked runtime into Geoscience Analyst with::

    install_in_analyst.bat
    install_in_analyst.bat -e --name geoh5-interop-dev

The script exports the locked ``win-64`` runtime, installs its dependencies
through Analyst, and installs this checkout without resolving dependencies
again. Pass ``-e`` first for editable mode; optional ``--conda`` and ``--name``
arguments are forwarded to Analyst. A valid ``pixi.lock`` is required.

Updating dependencies
^^^^^^^^^^^^^^^^^^^^^

Keep published package requirements in ``pyproject.toml`` and their Conda/PyPI
environment equivalents in ``pixi.toml`` aligned. Update the recipe's matching
runtime requirements when a dependency constraint changes.

After editing requirements, run ``pixi update`` to update dependencies, or
``pixi lock`` to resolve the manifest and refresh the lock file without
installing the environments.

Commit ``pixi.lock`` with the manifest changes. The ``mira-conda`` and
``mira-pypi`` features use published Mira packages, including private
pre-releases where configured. Do not switch them to Git sources or create a
Git dependency environment. The lock file is checked by
``tests/lock_test.py``, which verifies Mira package sources for these features;
unrelated PyPI dependencies are permitted. Keep compatibility bounds on
indirect Conda dependencies: Pixi solves Conda before PyPI and does not
backtrack between them.

Git hooks
^^^^^^^^^

Install `prek <https://prek.j178.dev/>`_ and use the existing hook configuration::

    prek install -t prepare-commit-msg -t commit-msg -t pre-commit -f --prepare-hooks
    prek run --all-files

The local pylint hook runs in the default environment.

Test layout
^^^^^^^^^^^

Tests live under ``tests`` and use the ``_test.py`` filename suffix.

Repository-specific instructions: geoh5-interop
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following instructions are specific to this meta-package.

Use ``default`` (Python 3.12, published Mira Conda packages and development
tools), ``conda-mira`` or ``pypi-mira`` for tests. The latter two have
``-py313`` and ``-py314`` variants. Runtime-only environments are
``conda-mira-rt`` and ``pypi-mira-rt``, with ``-py314`` variants. Run focused
source and lock checks with::

    pixi run --frozen -e pypi-mira python -m pytest -q tests/lock_test.py tests/check_dependencies_test.py
    pixi lock --check

``install`` installs this checkout editable without dependencies and checks
compatibility. ``test-pyvers`` runs PyPI tests for Python 3.12, 3.13 and 3.14;
``repl`` is available in ``default``. This repository does not define local
sibling-dependency or documentation build tasks.

Keep ``pyproject.toml``, ``pixi.toml`` and ``recipe.yaml`` requirements aligned
and commit any updated lock.

Use the Pixi login above for Mira Artifactory access to the private Conda
channel and PyPI index. Never put credentials in the repository, index URLs,
or command-line arguments.

The Analyst script exists here and exports ``conda-mira-rt`` from the lock;
use ``install_in_analyst.bat`` with optional ``-e`` first and ``--conda`` or
``--name`` as needed; ``geoh5-interop-dev`` above is only an example name.
This package does not select a PyTorch CPU or CUDA backend.

---------

*Copyright (c) 2023-2026 Mira Geoscience Ltd.*
