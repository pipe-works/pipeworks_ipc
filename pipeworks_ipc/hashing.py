"""Core hashing and normalization utilities for IPC provenance tracking."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Protocol

_POLICY_TREE_HASH_VERSION = "policy_tree_hash_v1"


class SupportsModelDump(Protocol):
    """Protocol for objects exposing Pydantic-style ``model_dump()``."""

    def model_dump(self) -> dict[str, Any]:
        """Return a plain dictionary representation."""


@dataclass(frozen=True, slots=True)
class PolicyHashEntry:
    """Canonical file entry used to compute deterministic policy tree digests."""

    relative_path: str
    content_hash: str


@dataclass(frozen=True, slots=True)
class DirectoryHashEntry:
    """Deterministic hash summary for one policy directory subtree."""

    path: str
    file_count: int
    hash: str


def _normalise_system_prompt(text: str) -> str:
    """Normalize system prompt text for stable hashing."""
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def _normalise_output(text: str) -> str:
    """Normalize output text while preserving structure and case."""
    stripped = text.strip()
    return re.sub(r" {2,}", " ", stripped)


def _normalise_policy_relative_path(relative_path: str) -> str:
    """Normalize and validate policy-relative paths used in hash payloads."""

    normalized = PurePosixPath(relative_path.replace("\\", "/")).as_posix().lstrip("./")
    if normalized in {"", "."}:
        raise ValueError("Policy relative path must not be empty")
    if normalized.startswith("../") or "/../" in f"/{normalized}":
        raise ValueError(f"Policy relative path must not traverse upwards: {relative_path!r}")
    return normalized


def compute_payload_hash(payload_dict: dict) -> str:
    """Return SHA-256 hex digest for canonicalized payload JSON."""
    canonical = json.dumps(payload_dict, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_system_prompt_hash(prompt_text: str) -> str:
    """Return SHA-256 hex digest for normalized system prompt text."""
    normalised = _normalise_system_prompt(prompt_text)
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()


def compute_output_hash(output_text: str) -> str:
    """Return SHA-256 hex digest for normalized output text."""
    normalised = _normalise_output(output_text)
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()


def compute_ipc_id(
    *,
    input_hash: str,
    system_prompt_hash: str,
    model: str,
    temperature: float,
    max_tokens: int,
    seed: int,
) -> str:
    """Return IPC identifier digest using explicit colon-delimited provenance fields."""
    parts = [
        input_hash,
        system_prompt_hash,
        model,
        str(temperature),
        str(max_tokens),
        str(seed),
    ]
    combined = ":".join(parts)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def compute_policy_file_hash(relative_path: str, content_bytes: bytes) -> str:
    """Return deterministic hash for one policy file path and its raw bytes."""

    normalized_path = _normalise_policy_relative_path(relative_path)
    payload = {
        "hash_version": _POLICY_TREE_HASH_VERSION,
        "relative_path": normalized_path,
        "content_bytes_hex": content_bytes.hex(),
    }
    return compute_payload_hash(payload)


def compute_policy_tree_hash(file_entries: list[PolicyHashEntry]) -> str:
    """Return deterministic digest for a full policy file-set snapshot."""

    normalized_entries = [
        {
            "relative_path": _normalise_policy_relative_path(entry.relative_path),
            "content_hash": entry.content_hash,
        }
        for entry in file_entries
    ]
    normalized_entries.sort(key=lambda entry: entry["relative_path"])
    payload = {
        "hash_version": _POLICY_TREE_HASH_VERSION,
        "entries": normalized_entries,
    }
    return compute_payload_hash(payload)


def compute_policy_directory_hashes(
    file_entries: list[PolicyHashEntry],
) -> list[DirectoryHashEntry]:
    """Return subtree hashes for each non-root directory in the policy tree."""

    grouped: dict[str, list[PolicyHashEntry]] = {}
    for entry in file_entries:
        normalized_path = _normalise_policy_relative_path(entry.relative_path)
        normalized_entry = PolicyHashEntry(
            relative_path=normalized_path,
            content_hash=entry.content_hash,
        )

        current = PurePosixPath(normalized_path).parent
        while True:
            directory = current.as_posix()
            grouped.setdefault(directory, []).append(normalized_entry)
            if directory == ".":
                break
            current = current.parent

    results: list[DirectoryHashEntry] = []
    for directory, directory_entries in grouped.items():
        if directory == ".":
            continue
        results.append(
            DirectoryHashEntry(
                path=directory,
                file_count=len(directory_entries),
                hash=compute_policy_tree_hash(directory_entries),
            )
        )

    return sorted(results, key=lambda entry: entry.path)


def payload_hash(payload: SupportsModelDump) -> str:
    """Convenience wrapper: hash an object exposing ``model_dump()``."""
    payload_dict = payload.model_dump()
    if not isinstance(payload_dict, dict):
        raise TypeError("payload.model_dump() must return a dict")
    return compute_payload_hash(payload_dict)
