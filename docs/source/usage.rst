Usage
=====

For a full consumer integration guide (including migration from copied hashing code and
manifest persistence), see :doc:`project_integration`.

Install for development:

.. code-block:: bash

   pip install -e ".[dev]"

Install with docs tooling:

.. code-block:: bash

   pip install -e ".[docs]"

Quick example:

.. code-block:: python

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
