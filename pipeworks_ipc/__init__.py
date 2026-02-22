"""pipeworks_ipc package.

Deterministic IPC/hash utilities shared across Pipe-Works projects.
"""

from .hashing import (
    compute_ipc_id,
    compute_output_hash,
    compute_payload_hash,
    compute_system_prompt_hash,
    payload_hash,
)

__all__ = [
    "compute_payload_hash",
    "compute_system_prompt_hash",
    "compute_output_hash",
    "compute_ipc_id",
    "payload_hash",
]

__version__ = "0.1.0"
