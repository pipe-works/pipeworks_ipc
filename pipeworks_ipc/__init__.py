"""pipeworks_ipc package.

Deterministic IPC/hash utilities shared across Pipe-Works projects.
"""

from .hashing import (
    DirectoryHashEntry,
    PolicyHashEntry,
    compute_ipc_id,
    compute_output_hash,
    compute_payload_hash,
    compute_policy_directory_hashes,
    compute_policy_file_hash,
    compute_policy_tree_hash,
    compute_system_prompt_hash,
    payload_hash,
)

__all__ = [
    "compute_payload_hash",
    "compute_system_prompt_hash",
    "compute_output_hash",
    "compute_ipc_id",
    "compute_policy_file_hash",
    "compute_policy_tree_hash",
    "compute_policy_directory_hashes",
    "payload_hash",
    "PolicyHashEntry",
    "DirectoryHashEntry",
]

__version__ = "0.1.2"
