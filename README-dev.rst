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
* **Git LFS:** This repository uses Git LFS. Follow GitHub's `installation
  instructions
  <https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage>`_.
* **prek:** Install `prek <https://prek.j178.dev/>`_ for the configured Git
  hooks.
* **IDE interpreter:** Configure your IDE to use the interpreter inside
  ``.pixi/envs/default`` and exclude ``.pixi`` from source indexing.
  For **PyCharm**, follow Pixi's `JetBrains integration guide
  <https://pixi.prefix.dev/latest/integration/editor/jetbrains/>`_.
* **JFrog authentication:** authenticate with Mira  Artifactory using your
  own credentials::

      pixi auth login mirageoscienceltd.jfrog.io

  Never add credentials to ``pixi.toml`` or ``pixi.lock``.

Install and test
^^^^^^^^^^^^^^^^

The shared lock covers Windows and Linux with multiple Python versions::

    pixi install --locked -e py312
    pixi run --frozen -e py312 install
    pixi run --frozen -e py312 test

The ``install`` task installs this checkout in editable mode without changing
locked dependencies, then checks package compatibility.

The ``runtime`` environment omits test and lint tools.

On Windows, install the locked runtime into Geoscience Analyst with::

    install_in_analyst.bat
    install_in_analyst.bat -e --name simpeg-drivers-dev

The script exports the locked ``win-64`` runtime, installs its dependencies
through Analyst, and installs this checkout without resolving dependencies
again. Pass ``-e`` first for editable mode; optional ``--conda`` and ``--name``
arguments are forwarded to Analyst. A valid ``pixi.lock`` is required.

Working with local sibling checkouts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For a one-off test run, ``test-local`` installs the sibling checkouts as
editable dependencies and then runs the tests::

    pixi run -e py312 test-local

For ongoing development or IDE debugging, install editable sibling checkouts
into the default environment (the IDE environment) with::

    pixi run use-local-deps

Pixi syncs the environment from the manifest and lock file before running the
task; the task then installs the local checkouts. A subsequent ``pixi run``
without ``--as-is`` syncs again and replaces those editable installs with the
locked packages. An IDE configured to launch the ``default`` environment's
Python interpreter directly does not run ``pixi`` before each launch, so the
editable installs remain in effect.

Building documentation
^^^^^^^^^^^^^^^^^^^^^^

Read the Docs installs uv 0.13.8 separately.

The separate ``docs`` environment uses Python 3.14 and Jupyter Book 1.
Fetch the Git LFS documentation images, then build HTML with::

    git lfs pull
    pixi run --frozen --environment docs build-docs

The task installs the local package without dependencies, generates ``docs/conf.py``
from ``docs/_config.yml``, and builds the existing book into ``docs/_build/html``.
The generated Sphinx configuration is ignored; edit ``docs/_config.yml`` or
``docs/_ext/dynamic_config.py`` instead. Read the Docs uses the same task.


Updating dependencies
^^^^^^^^^^^^^^^^^^^^^

Keep published package requirements in ``pyproject.toml`` and their Conda/PyPI
environment equivalents in ``pixi.toml`` aligned. Update the recipe's matching
runtime requirements when a dependency constraint changes.

After editing requirements, run ``pixi update`` to update dependencies, or
``pixi lock`` to resolve the manifest and refresh the lock file without
installing the environments.

Commit ``pixi.lock`` with the manifest changes. In ``pixi.toml``, the
``mira-pypi`` feature lists Mira packages resolved from PyPI or GitHub:

- On a development branch, comment out published versions and use git sources.
- When preparing a release, use published versions and comment out git sources.

The lock file is checked by ``tests/lock_test.py``: it ensures all dependencies
are resolved from Conda, except for the Mira packages listed under the
``mira-pypi`` feature. Keep compatibility bounds on indirect Conda dependencies:
Pixi solves Conda before PyPI and does not backtrack between them.

Git hooks
^^^^^^^^^

Install `prek <https://prek.j178.dev/>`_ and use the existing hook configuration::

    prek install -t prepare-commit-msg -t commit-msg -t pre-commit -f --prepare-hooks
    prek run --all-files

The local pylint hook runs in the locked ``py312`` environment.

Test layout
^^^^^^^^^^^

Tests live under ``tests`` and use the ``_test.py`` filename suffix.

Repository-specific instructions: geoh5-interop
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The shared instructions above describe simpeg-drivers. The following
instructions take precedence for this meta-package; do not use the generic
``py312``, ``runtime`` or ``docs`` environments here.

Use ``default`` (Python 3.12, published Mira Conda packages and development
tools), ``conda-mira`` or ``pypi-mira`` for tests. The latter two have
``-py313`` and ``-py314`` variants. Runtime-only environments are
``conda-mira-rt`` and ``pypi-mira-rt``, with ``-py314`` variants. For example::

    pixi install --locked -e pypi-mira
    pixi run --frozen -e pypi-mira install
    pixi run --frozen -e pypi-mira test
    pixi run --frozen -e pypi-mira python -m pytest -q tests/lock_test.py tests/check_dependencies_test.py
    pixi lock --check

``install`` installs this checkout editable without dependencies and checks
compatibility. ``test-pyvers`` runs PyPI tests for Python 3.12, 3.13 and 3.14;
``repl`` is available in ``default``. There are no ``test-local``,
``use-local-deps`` or ``build-docs`` tasks. There is no documentation build
environment or Read the Docs build described above for this repository. The
pylint hook uses the existing default environment, not ``py312``.

The ``mira-conda`` and ``mira-pypi`` features use published Mira Conda and
PyPI packages respectively, including private pre-releases where configured.
Do not switch them to Git sources or create a Git dependency environment.
The lock tests check the selected Mira sources; unrelated PyPI dependencies
are permitted. Keep ``pyproject.toml``, ``pixi.toml`` and ``recipe.yaml``
requirements aligned and commit any updated lock.

Authenticate to the private Conda channels with the Pixi login above. Private
PyPI indexes require separate authentication; provide credentials through the
supported credential mechanism, not in the repository or index URLs. Avoid
passing tokens on the command line, where they can appear in history or process
listings.

The Analyst script exists here and exports ``conda-mira-rt`` from the lock;
use ``install_in_analyst.bat`` with optional ``-e`` first and ``--conda`` or
``--name`` as needed. The simpeg-drivers example name above is not this
package's recommended environment name. This package does not select a
PyTorch CPU or CUDA backend.

---------

*Copyright (c) 2023-2026 Mira Geoscience Ltd.*
