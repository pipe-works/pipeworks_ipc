"""Tests for typed-package metadata wiring."""

from importlib import resources


def test_package_includes_py_typed_marker() -> None:
    """``pipeworks_ipc`` should advertise inline typing support to mypy."""
    marker = resources.files("pipeworks_ipc").joinpath("py.typed")
    assert marker.is_file()
