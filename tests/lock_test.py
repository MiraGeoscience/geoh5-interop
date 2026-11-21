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


def locked_conda_names(entries):
    return {
        canonicalize_name(
            unquote(urlsplit(entry["conda"]).path.rsplit("/", 1)[-1]).rsplit("-", 2)[0]
        )
        for entry in entries
        if "conda" in entry
    }


def test_locked_mira_sources():
    package_root = Path(__file__).resolve().parents[1]
    pixi = tomllib.loads((package_root / "pixi.toml").read_text())
    lock = yaml.safe_load((package_root / "pixi.lock").read_text())
    packages = {
        package["pypi"]: package["name"]
        for package in lock["packages"]
        if "pypi" in package
    }
    mira_conda = {
        canonicalize_name(name)
        for name in pixi["feature"]["mira-conda"]["dependencies"]
    }
    mira_pypi = {
        canonicalize_name(name)
        for name in pixi["feature"]["mira-pypi"]["pypi-dependencies"]
    }

    for environment, data in lock["environments"].items():
        if environment == "docs":
            continue
        features = pixi["environments"][environment]["features"]
        if not {"mira-conda", "mira-pypi"}.intersection(features):
            continue
        for platform, entries in data["packages"].items():
            conda_sources = locked_conda_names(entries)
            pypi_sources = locked_pypi_names(entries, packages)
            if "mira-conda" in features:
                assert mira_conda <= conda_sources, (
                    environment,
                    platform,
                    mira_conda - conda_sources,
                )
                assert mira_conda.isdisjoint(pypi_sources), (
                    environment,
                    platform,
                    mira_conda & pypi_sources,
                )
            if "mira-pypi" in features:
                assert mira_pypi <= pypi_sources, (
                    environment,
                    platform,
                    mira_pypi - pypi_sources,
                )
                assert mira_pypi.isdisjoint(conda_sources), (
                    environment,
                    platform,
                    mira_pypi & conda_sources,
                )
