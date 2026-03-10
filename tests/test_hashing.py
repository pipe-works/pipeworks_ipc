"""Tests for pipeworks_ipc hashing behavior and determinism."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from pipeworks_ipc.hashing import (
    DirectoryHashEntry,
    PolicyHashEntry,
    _normalise_output,
    _normalise_system_prompt,
    compute_ipc_id,
    compute_output_hash,
    compute_payload_hash,
    compute_policy_directory_hashes,
    compute_policy_file_hash,
    compute_policy_tree_hash,
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


class TestPolicyTreeHashing:
    def test_compute_policy_file_hash_is_deterministic(self) -> None:
        payload = b"text: |\n  goblin\n"
        first = compute_policy_file_hash("image/blocks/species/goblin_v1.yaml", payload)
        second = compute_policy_file_hash("image/blocks/species/goblin_v1.yaml", payload)
        assert first == second

    def test_compute_policy_file_hash_changes_with_path_or_content(self) -> None:
        left = compute_policy_file_hash("image/prompts/base.txt", b"one")
        right_path = compute_policy_file_hash("image/prompts/alt.txt", b"one")
        right_content = compute_policy_file_hash("image/prompts/base.txt", b"two")
        assert left != right_path
        assert left != right_content

    @pytest.mark.parametrize("relative_path", ["", ".", "./", "////"])
    def test_compute_policy_file_hash_rejects_empty_relative_path(self, relative_path: str) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            compute_policy_file_hash(relative_path, b"content")

    @pytest.mark.parametrize("relative_path", ["../x.txt", "image/../x.txt"])
    def test_compute_policy_file_hash_rejects_parent_traversal(self, relative_path: str) -> None:
        with pytest.raises(ValueError, match="must not traverse upwards"):
            compute_policy_file_hash(relative_path, b"content")

    def test_compute_policy_tree_hash_is_order_independent(self) -> None:
        entries_a = [
            PolicyHashEntry(relative_path="image/prompts/a.txt", content_hash="h1"),
            PolicyHashEntry(relative_path="image/prompts/b.txt", content_hash="h2"),
        ]
        entries_b = list(reversed(entries_a))
        assert compute_policy_tree_hash(entries_a) == compute_policy_tree_hash(entries_b)

    def test_compute_policy_tree_hash_changes_on_single_entry_change(self) -> None:
        baseline = [
            PolicyHashEntry(relative_path="image/prompts/a.txt", content_hash="h1"),
            PolicyHashEntry(relative_path="image/prompts/b.txt", content_hash="h2"),
        ]
        changed = [
            PolicyHashEntry(relative_path="image/prompts/a.txt", content_hash="h1"),
            PolicyHashEntry(relative_path="image/prompts/b.txt", content_hash="h3"),
        ]
        assert compute_policy_tree_hash(baseline) != compute_policy_tree_hash(changed)

    def test_compute_policy_directory_hashes_is_stable_and_scoped(self) -> None:
        entries = [
            PolicyHashEntry(relative_path="image/prompts/a.txt", content_hash="h1"),
            PolicyHashEntry(relative_path="image/prompts/nested/b.txt", content_hash="h2"),
            PolicyHashEntry(relative_path="translation/prompts/c.txt", content_hash="h3"),
        ]

        result_a = compute_policy_directory_hashes(entries)
        result_b = compute_policy_directory_hashes(list(reversed(entries)))
        assert result_a == result_b

        by_path = {entry.path: entry for entry in result_a}
        assert by_path["image"].file_count == 2
        assert by_path["image/prompts"].file_count == 2
        assert by_path["image/prompts/nested"].file_count == 1
        assert by_path["translation"].file_count == 1

        changed_entries = [
            PolicyHashEntry(relative_path="image/prompts/a.txt", content_hash="changed"),
            PolicyHashEntry(relative_path="image/prompts/nested/b.txt", content_hash="h2"),
            PolicyHashEntry(relative_path="translation/prompts/c.txt", content_hash="h3"),
        ]
        changed = {entry.path: entry for entry in compute_policy_directory_hashes(changed_entries)}
        assert changed["image"].hash != by_path["image"].hash
        assert changed["translation"].hash == by_path["translation"].hash


class TestPolicyHashEntryDataclasses:
    def test_directory_hash_entry_is_comparable_for_stable_assertions(self) -> None:
        first = DirectoryHashEntry(path="image", file_count=1, hash="abc")
        second = DirectoryHashEntry(path="image", file_count=1, hash="abc")
        assert first == second
