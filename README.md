# pipeworks_ipc

[![CI](https://github.com/pipe-works/pipeworks_ipc/actions/workflows/ci.yml/badge.svg)](https://github.com/pipe-works/pipeworks_ipc/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/pipe-works/pipeworks_ipc/graph/badge.svg?branch=main)](https://codecov.io/gh/pipe-works/pipeworks_ipc)
[![docs](https://readthedocs.org/projects/pipeworks-ipc/badge/?version=latest)](https://pipeworks-ipc.readthedocs.io/en/latest/)
[![python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![license](https://img.shields.io/badge/license-GPL--3.0--or--later-blue.svg)](LICENSE)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![lint: ruff](https://img.shields.io/badge/lint-ruff-46B1E8?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Reusable, deterministic IPC (Interpretive Provenance Chain) hashing utilities for Pipe-Works projects.

## What this package provides

- `compute_payload_hash(payload_dict)`
- `compute_system_prompt_hash(prompt_text)`
- `compute_output_hash(output_text)`
- `compute_ipc_id(input_hash, system_prompt_hash, model, temperature, max_tokens, seed)`
- `payload_hash(payload_model)` convenience wrapper for objects exposing `model_dump()`

The first release preserves Axis Descriptor Lab semantics so IPC values are reproducible across projects.

## Python / pyenv

This project targets Python 3.12+.

```bash
pyenv install -s 3.12.8
pyenv local 3.12.8
python -V
```

## Install

```bash
pip install -e .
pip install -e ".[dev]"
pip install -e ".[docs]"
```

## Install in Other Projects (Before PyPI)

Use one of these approaches when ``pipeworks-ipc`` is not yet published to PyPI.

Local path (editable):

```bash
pip install -e /path/to/pipeworks_ipc
```

GitHub tag:

```bash
pip install "pipeworks-ipc @ git+https://github.com/pipe-works/pipeworks_ipc.git@v0.1.1"
```

GitHub commit SHA (strict reproducibility):

```bash
pip install "pipeworks-ipc @ git+https://github.com/pipe-works/pipeworks_ipc.git@<commit-sha>"
```

For consumer ``pyproject.toml`` dependencies before PyPI publication:

```toml
[project]
dependencies = [
  "pipeworks-ipc @ git+https://github.com/pipe-works/pipeworks_ipc.git@v0.1.1"
]
```

## When to Publish to PyPI

Publish when all of these are true:

- at least one consumer project uses ``pipeworks-ipc`` in production-like flow
- IPC semantics are stable and deterministic tests are green
- CI/docs/release automation are consistently passing
- you want to stop relying on local paths and Git URL dependencies

Recommended progression:

1. integrate in a consumer project and stabilize
2. release to TestPyPI first
3. release to PyPI

## Pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Test

```bash
pytest -v
```

## Documentation

Build locally:

```bash
make -C docs html
```

Open:

```bash
docs/build/html/index.html
```

## Example

```python
from pipeworks_ipc.hashing import (
    compute_payload_hash,
    compute_system_prompt_hash,
    compute_output_hash,
    compute_ipc_id,
)

payload = {"seed": 42, "world_id": "pipeworks", "policy_hash": "abc", "axes": {}}
input_hash = compute_payload_hash(payload)
prompt_hash = compute_system_prompt_hash("You are ornamental.")
output_hash = compute_output_hash("A weathered figure stands.")
ipc_id = compute_ipc_id(
    input_hash=input_hash,
    system_prompt_hash=prompt_hash,
    model="gemma2:2b",
    temperature=0.2,
    max_tokens=120,
    seed=42,
)
```
