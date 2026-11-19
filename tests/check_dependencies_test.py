# Copyright (c) 2024-2026 Mira Geoscience Ltd.
"""Tests for dependency-check exceptions."""

from subprocess import CompletedProcess
from unittest.mock import Mock

import pytest

from scripts import check_dependencies


def test_known_platform_errors_are_allowed(monkeypatch):
    monkeypatch.setattr(check_dependencies, "known_legacy_wheel", lambda _: True)
    output = (
        "Checked 49 packages in 10ms\n"
        "Found 2 incompatibilities\n"
        "The package `properties` was built for a different platform\n"
        "The package `vectormath` was built for a different platform\n"
    )
    assert check_dependencies.only_known_platform_errors(output)


def test_other_errors_are_not_hidden(monkeypatch):
    monkeypatch.setattr(check_dependencies, "known_legacy_wheel", lambda _: True)
    output = (
        "Found 2 incompatibilities\n"
        "The package `properties` was built for a different platform\n"
        "package requires missing-dependency\n"
    )
    assert not check_dependencies.only_known_platform_errors(output)
    assert not check_dependencies.only_known_platform_errors(
        "Found 2 incompatibilities\n"
        "The package `properties` was built for a different platform\n"
    )


def test_unrecognized_build_is_not_allowed(monkeypatch):
    monkeypatch.setattr(check_dependencies, "known_legacy_wheel", lambda _: False)
    assert not check_dependencies.only_known_platform_errors(
        "Found 1 incompatibility\n"
        "The package `properties` was built for a different platform\n"
    )


@pytest.mark.parametrize(
    ("wheel", "record", "allowed"),
    [
        ("Root-Is-Purelib: true\nTag: cp27-none-any\n", True, True),
        ("Root-Is-Purelib: false\nTag: cp27-none-any\n", True, False),
        ("Root-Is-Purelib: true\nTag: py3-none-any\n", True, False),
        ("Root-Is-Purelib: true\nTag: cp27-none-any\n", False, False),
    ],
)
def test_exception_requires_the_exact_pure_conda_build(
    tmp_path, monkeypatch, wheel, record, allowed
):
    monkeypatch.setattr(check_dependencies.sys, "prefix", str(tmp_path))
    monkeypatch.setattr(
        check_dependencies,
        "distribution",
        lambda _: Mock(version="0.6.1", read_text=Mock(return_value=wheel)),
    )
    if record:
        conda_meta = tmp_path / "conda-meta"
        conda_meta.mkdir()
        (conda_meta / "properties-0.6.1-py_0.json").touch()
    assert check_dependencies.known_legacy_wheel("properties") is allowed


def test_other_uv_failures_stay_failures(monkeypatch):
    monkeypatch.setattr(
        check_dependencies.subprocess,
        "run",
        lambda *args, **kwargs: CompletedProcess(args, 2, "unexpected error\n"),
    )
    assert check_dependencies.main() == 2
