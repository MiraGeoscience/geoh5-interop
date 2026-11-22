# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2026 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of geoh5-interop meta-package.                            '
#                                                                              '
#  All rights reserved.                                                        '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import tomllib
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from packaging.utils import canonicalize_name


def locked_pypi_names(entries, packages):
    return {
        canonicalize_name(packages[entry["pypi"]])
        for entry in entries
        if "pypi" in entry
    }


def test_locked_pypi_names_with_git_source():
    url = "git+https://github.com/MiraGeoscience/geoh5py.git@release/ga-4.9"
    assert locked_pypi_names([{"pypi": url}], {url: "geoh5py"}) == {"geoh5py"}


def test_locked_pypi_sources():
    """Check that Mira packages use the source selected by each environment."""

    package_root = Path(__file__).resolve().parents[1]
    pixi = tomllib.loads((package_root / "pixi.toml").read_text())
    mira_sources = {
        canonicalize_name(name)
        for name in pixi["feature"]["mira-pypi"]["pypi-dependencies"]
    }
    mira_conda = {
        canonicalize_name(name)
        for name in pixi["feature"]["mira-conda"]["dependencies"]
    }
    lock = yaml.safe_load((package_root / "pixi.lock").read_text())
    packages = {
        package["pypi"]: package["name"]
        for package in lock["packages"]
        if "pypi" in package
    }
    for environment, data in lock["environments"].items():
        features = pixi["environments"][environment]["features"]
        expected_pypi = mira_sources if "mira-pypi" in features else set()
        expected_conda = mira_conda if "mira-conda" in features else set()
        for platform, entries in data["packages"].items():
            pypi_sources = locked_pypi_names(entries, packages)
            conda_sources = {
                canonicalize_name(
                    unquote(urlsplit(entry["conda"]).path.rsplit("/", 1)[-1]).rsplit(
                        "-", 2
                    )[0]
                )
                for entry in entries
                if "conda" in entry
            }
            assert pypi_sources & mira_sources == expected_pypi, (
                environment,
                platform,
                expected_pypi,
                pypi_sources & mira_sources,
            )
            assert conda_sources & mira_conda == expected_conda, (
                environment,
                platform,
                expected_conda,
                conda_sources & mira_conda,
            )
