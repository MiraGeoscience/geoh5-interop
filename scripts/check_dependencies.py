# Copyright (c) 2024-2026 Mira Geoscience Ltd.
"""Check dependencies while reporting two known Conda wheel-tag defects."""

from __future__ import annotations

import re
import subprocess
import sys
from email.parser import Parser
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path


LEGACY_CONDA_BUILDS = {
    "properties": ("0.6.1", "py_0"),
    "vectormath": ("0.2.2", "py_0"),
}
PLATFORM_ERROR = re.compile(r"The package `([^`]+)` was built for a different platform")


def known_legacy_wheel(name: str) -> bool:
    """Identify the exact pure-Python Conda builds with incorrect wheel tags."""
    if name not in LEGACY_CONDA_BUILDS:
        return False
    version, build = LEGACY_CONDA_BUILDS[name]
    conda_record = Path(sys.prefix) / "conda-meta" / f"{name}-{version}-{build}.json"
    try:
        package = distribution(name)
    except PackageNotFoundError:
        return False
    if package.version != version or not conda_record.is_file():
        return False
    wheel = package.read_text("WHEEL")
    if wheel is None:
        return False
    metadata = Parser().parsestr(wheel)
    return metadata.get("Root-Is-Purelib", "").lower() == "true" and metadata.get_all(
        "Tag", []
    ) == ["cp27-none-any"]


def only_known_platform_errors(output: str) -> bool:
    """Recognize only the documented legacy Conda wheel-tag errors."""
    count = None
    errors = []
    for line in output.splitlines():
        if line.startswith(("Using Python ", "Checked ")):
            continue
        summary = re.fullmatch(r"Found (\d+) incompatibilit(?:y|ies)", line)
        if summary:
            if count is not None:
                return False
            count = int(summary.group(1))
            continue
        match = PLATFORM_ERROR.fullmatch(line)
        if match and known_legacy_wheel(match.group(1)):
            errors.append(match.group(1))
            continue
        return False
    return bool(errors) and count == len(errors) and len(errors) == len(set(errors))


def main() -> int:
    result = subprocess.run(
        ["uv", "pip", "check", "--python", sys.executable],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    print(result.stdout, end="")
    if result.returncode == 0:
        return 0
    if result.returncode == 1 and only_known_platform_errors(result.stdout):
        print(
            "Ignoring documented incorrect Python 2 wheel tags in legacy Conda builds."
        )
        return 0
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
