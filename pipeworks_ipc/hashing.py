"""Core hashing and normalization utilities for IPC provenance tracking."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Protocol


class SupportsModelDump(Protocol):
    """Protocol for objects exposing Pydantic-style ``model_dump()``."""

    def model_dump(self) -> dict[str, Any]:
        """Return a plain dictionary representation."""


def _normalise_system_prompt(text: str) -> str:
    """Normalize system prompt text for stable hashing."""
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def _normalise_output(text: str) -> str:
    """Normalize output text while preserving structure and case."""
    stripped = text.strip()
    return re.sub(r" {2,}", " ", stripped)


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


def payload_hash(payload: SupportsModelDump) -> str:
    """Convenience wrapper: hash an object exposing ``model_dump()``."""
    payload_dict = payload.model_dump()
    if not isinstance(payload_dict, dict):
        raise TypeError("payload.model_dump() must return a dict")
    return compute_payload_hash(payload_dict)
