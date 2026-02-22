Use in a Project
================

This page describes a practical pattern for adopting ``pipeworks_ipc`` in a consumer
project (for example, ``pipeworks_name_generation``) so you can stop duplicating IPC
hashing code across repositories.

Why this package exists
-----------------------

``pipeworks_ipc`` centralizes deterministic IPC hashing semantics so one implementation
is shared everywhere:

- no re-implementation drift between projects
- stable and reproducible IPC values for equivalent inputs
- easier testing and auditing of provenance metadata

The first release intentionally preserves Axis Descriptor Lab IPC behavior.

Step 1: Add the dependency
--------------------------

For local development (editable install):

.. code-block:: bash

   pip install -e /path/to/pipeworks_ipc

For Git-based installation (before PyPI publication):

.. code-block:: bash

   pip install "pipeworks-ipc @ git+https://github.com/pipe-works/pipeworks_ipc.git@v0.1.1"

For strict reproducibility, pin a commit SHA:

.. code-block:: bash

   pip install "pipeworks-ipc @ git+https://github.com/pipe-works/pipeworks_ipc.git@<commit-sha>"

For a consumer ``pyproject.toml`` dependency before PyPI:

.. code-block:: toml

   [project]
   dependencies = [
     "pipeworks-ipc @ git+https://github.com/pipe-works/pipeworks_ipc.git@v0.1.1",
   ]

Step 2: Centralize IPC creation in one helper
---------------------------------------------

Create one project-local module (for example ``your_project/provenance.py``) and call
the package functions there. Do not spread direct hash calls across unrelated modules.

.. code-block:: python

   from __future__ import annotations

   from typing import Any

   from pipeworks_ipc.hashing import (
       compute_ipc_id,
       compute_output_hash,
       compute_payload_hash,
       compute_system_prompt_hash,
   )


   def build_ipc_metadata(
       *,
       payload: dict[str, Any],
       system_prompt: str,
       output_text: str,
       model: str,
       temperature: float,
       max_tokens: int,
       seed: int,
   ) -> dict[str, str]:
       input_hash = compute_payload_hash(payload)
       system_prompt_hash = compute_system_prompt_hash(system_prompt)
       output_hash = compute_output_hash(output_text)
       ipc_id = compute_ipc_id(
           input_hash=input_hash,
           system_prompt_hash=system_prompt_hash,
           model=model,
           temperature=temperature,
           max_tokens=max_tokens,
           seed=seed,
       )
       return {
           "ipc_id": ipc_id,
           "input_hash": input_hash,
           "system_prompt_hash": system_prompt_hash,
           "output_hash": output_hash,
       }

Step 3: Persist IPC metadata with every run artifact
----------------------------------------------------

Write IPC values into your run manifest (or equivalent metadata file) at the same time
you write generated outputs.

Example JSON fragment:

.. code-block:: json

   {
     "run_id": "20260222_113000",
     "model": "gemma2:2b",
     "seed": 42,
     "ipc": {
       "ipc_id": "e9b9...",
       "input_hash": "5b19...",
       "system_prompt_hash": "2a03...",
       "output_hash": "d8fe..."
     }
   }

Migration from copied IPC code
------------------------------

If your project currently duplicates Axis-style hashing code:

1. Remove the duplicated normalization/hash helpers from the consumer project.
2. Keep your payload construction logic unchanged.
3. Replace local hash calls with ``pipeworks_ipc.hashing`` calls in one integration
   helper.
4. Re-run deterministic tests on fixed fixtures and compare expected IPC IDs.

Determinism checklist
---------------------

- keep payload keys and value types stable for equivalent runs
- pass explicit ``seed`` values (do not rely on implicit randomness)
- persist model and generation parameters used in ``compute_ipc_id``
- avoid mutating payload objects after hash computation

Test template for consumers
---------------------------

Add at least one integration test in the consumer project:

.. code-block:: python

   def test_ipc_is_deterministic_for_fixed_inputs() -> None:
       metadata_a = build_ipc_metadata(
           payload={"world_id": "pipeworks", "seed": 42, "policy_hash": "abc", "axes": {}},
           system_prompt="You are ornamental.",
           output_text="A weathered figure stands.",
           model="gemma2:2b",
           temperature=0.2,
           max_tokens=120,
           seed=42,
       )
       metadata_b = build_ipc_metadata(
           payload={"world_id": "pipeworks", "seed": 42, "policy_hash": "abc", "axes": {}},
           system_prompt="You are ornamental.",
           output_text="A weathered figure stands.",
           model="gemma2:2b",
           temperature=0.2,
           max_tokens=120,
           seed=42,
       )
       assert metadata_a["ipc_id"] == metadata_b["ipc_id"]

This gives you a reusable, testable provenance layer without re-coding IPC internals in
every repository.

When to publish to PyPI
-----------------------

Publish when these are all true:

- at least one consumer project has stable integration
- deterministic IPC tests are passing consistently
- CI/docs/release automation are all green
- Git URL or local path installs are becoming operational friction

Practical rollout:

1. stabilize one consumer integration
2. publish to TestPyPI
3. publish to PyPI
