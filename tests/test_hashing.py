"""Tests for pipeworks_ipc hashing behavior and determinism."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from pipeworks_ipc.hashing import (
    _normalise_output,
    _normalise_system_prompt,
    compute_ipc_id,
    compute_output_hash,
    compute_payload_hash,
    compute_system_prompt_hash,
    payload_hash,
)


@dataclass
class DummyPayload:
    """Simple test double exposing ``model_dump``."""

    data: dict

    def model_dump(self) -> dict:
        return dict(self.data)


class DummyPayloadBad:
    """Bad test double returning non-dict."""

    def model_dump(self):  # noqa: ANN201
        return "not-a-dict"


class TestNormaliseSystemPrompt:
    def test_strips_leading_trailing_whitespace_per_line(self) -> None:
        raw = "  line one  \n  line two  "
        assert _normalise_system_prompt(raw) == "line one\nline two"

    def test_removes_blank_lines_at_start_and_end(self) -> None:
        raw = "\n\n  content here  \n\n"
        assert _normalise_system_prompt(raw) == "content here"

    def test_preserves_internal_blank_lines(self) -> None:
        raw = "paragraph one\n\nparagraph two"
        assert _normalise_system_prompt(raw) == "paragraph one\n\nparagraph two"

    def test_preserves_case(self) -> None:
        raw = "NEVER use metaphor"
        assert _normalise_system_prompt(raw) == "NEVER use metaphor"


class TestNormaliseOutput:
    def test_strips_outer_whitespace(self) -> None:
        assert _normalise_output("  some output text  ") == "some output text"

    def test_collapses_multiple_spaces(self) -> None:
        assert _normalise_output("word   word    word") == "word word word"

    def test_preserves_newlines(self) -> None:
        assert _normalise_output("line one\nline two") == "line one\nline two"


class TestComputeSystemPromptHash:
    def test_deterministic(self) -> None:
        prompt = "You are a descriptive layer."
        assert compute_system_prompt_hash(prompt) == compute_system_prompt_hash(prompt)

    def test_returns_64_char_hex(self) -> None:
        result = compute_system_prompt_hash("test prompt")
        assert len(result) == 64
        assert result == result.lower()
        int(result, 16)

    def test_whitespace_variations_same_hash(self) -> None:
        raw_a = "  line one  \n  line two  "
        raw_b = "line one\nline two"
        assert compute_system_prompt_hash(raw_a) == compute_system_prompt_hash(raw_b)


class TestComputeOutputHash:
    def test_deterministic(self) -> None:
        text = "A weathered figure stands."
        assert compute_output_hash(text) == compute_output_hash(text)

    def test_returns_64_char_hex(self) -> None:
        result = compute_output_hash("test output")
        assert len(result) == 64
        assert result == result.lower()
        int(result, 16)

    def test_extra_spaces_normalised(self) -> None:
        assert compute_output_hash("word  word") == compute_output_hash("word word")


class TestComputeIpcId:
    _BASE_INPUT_HASH = "a" * 64
    _BASE_PROMPT_HASH = "b" * 64
    _BASE_MODEL = "gemma2:2b"
    _BASE_TEMP = 0.2
    _BASE_MAX_TOKENS = 120
    _BASE_SEED = 42

    def _base_id(self) -> str:
        return compute_ipc_id(
            input_hash=self._BASE_INPUT_HASH,
            system_prompt_hash=self._BASE_PROMPT_HASH,
            model=self._BASE_MODEL,
            temperature=self._BASE_TEMP,
            max_tokens=self._BASE_MAX_TOKENS,
            seed=self._BASE_SEED,
        )

    def test_deterministic(self) -> None:
        assert self._base_id() == self._base_id()

    def test_returns_64_char_hex(self) -> None:
        result = self._base_id()
        assert len(result) == 64
        assert result == result.lower()
        int(result, 16)

    def test_all_fields_affect_hash(self) -> None:
        base_id = self._base_id()

        assert (
            compute_ipc_id(
                input_hash="x" * 64,
                system_prompt_hash=self._BASE_PROMPT_HASH,
                model=self._BASE_MODEL,
                temperature=self._BASE_TEMP,
                max_tokens=self._BASE_MAX_TOKENS,
                seed=self._BASE_SEED,
            )
            != base_id
        )
        assert (
            compute_ipc_id(
                input_hash=self._BASE_INPUT_HASH,
                system_prompt_hash="x" * 64,
                model=self._BASE_MODEL,
                temperature=self._BASE_TEMP,
                max_tokens=self._BASE_MAX_TOKENS,
                seed=self._BASE_SEED,
            )
            != base_id
        )
        assert (
            compute_ipc_id(
                input_hash=self._BASE_INPUT_HASH,
                system_prompt_hash=self._BASE_PROMPT_HASH,
                model="llama3:8b",
                temperature=self._BASE_TEMP,
                max_tokens=self._BASE_MAX_TOKENS,
                seed=self._BASE_SEED,
            )
            != base_id
        )
        assert (
            compute_ipc_id(
                input_hash=self._BASE_INPUT_HASH,
                system_prompt_hash=self._BASE_PROMPT_HASH,
                model=self._BASE_MODEL,
                temperature=0.9,
                max_tokens=self._BASE_MAX_TOKENS,
                seed=self._BASE_SEED,
            )
            != base_id
        )
        assert (
            compute_ipc_id(
                input_hash=self._BASE_INPUT_HASH,
                system_prompt_hash=self._BASE_PROMPT_HASH,
                model=self._BASE_MODEL,
                temperature=self._BASE_TEMP,
                max_tokens=256,
                seed=self._BASE_SEED,
            )
            != base_id
        )
        assert (
            compute_ipc_id(
                input_hash=self._BASE_INPUT_HASH,
                system_prompt_hash=self._BASE_PROMPT_HASH,
                model=self._BASE_MODEL,
                temperature=self._BASE_TEMP,
                max_tokens=self._BASE_MAX_TOKENS,
                seed=999,
            )
            != base_id
        )

    def test_colon_delimiter_prevents_collision(self) -> None:
        id_a = compute_ipc_id(
            input_hash="ab",
            system_prompt_hash="cd",
            model="m",
            temperature=0.1,
            max_tokens=10,
            seed=1,
        )
        id_b = compute_ipc_id(
            input_hash="abc",
            system_prompt_hash="d",
            model="m",
            temperature=0.1,
            max_tokens=10,
            seed=1,
        )
        assert id_a != id_b


class TestComputePayloadHash:
    _SAMPLE = {
        "axes": {
            "health": {"label": "weary", "score": 0.5},
            "age": {"label": "old", "score": 0.7},
        },
        "policy_hash": "abc123",
        "seed": 42,
        "world_id": "test_world",
    }

    def test_deterministic(self) -> None:
        assert compute_payload_hash(self._SAMPLE) == compute_payload_hash(self._SAMPLE)

    def test_order_independent(self) -> None:
        reversed_axes = {
            "age": {"label": "old", "score": 0.7},
            "health": {"label": "weary", "score": 0.5},
        }
        reversed_dict = {
            "world_id": "test_world",
            "seed": 42,
            "policy_hash": "abc123",
            "axes": reversed_axes,
        }
        assert compute_payload_hash(self._SAMPLE) == compute_payload_hash(reversed_dict)


class TestPayloadHash:
    def test_hashes_model_dump_dict(self) -> None:
        payload = DummyPayload(
            {
                "axes": {"health": {"label": "weary", "score": 0.5}},
                "policy_hash": "h",
                "seed": 1,
                "world_id": "w",
            }
        )
        h1 = payload_hash(payload)
        h2 = payload_hash(payload)
        assert h1 == h2
        assert len(h1) == 64

    def test_raises_when_model_dump_not_dict(self) -> None:
        with pytest.raises(TypeError):
            payload_hash(DummyPayloadBad())
