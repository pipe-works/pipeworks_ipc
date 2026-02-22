"""Sphinx configuration for pipeworks_ipc."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

project = "pipeworks_ipc"
copyright = "2026, Pipe-Works"
author = "Pipe-Works"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path: list[str] = []
exclude_patterns: list[str] = []

html_theme = "sphinx_rtd_theme"
html_static_path: list[str] = []

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": False,
}
