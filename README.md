# pipeworks_ipc

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
```

## Pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Test

```bash
pytest -v
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
