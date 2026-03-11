"""Tests for CLI utilities and command routing."""

import json
import time
from contextlib import nullcontext
from types import SimpleNamespace

import learnlock.cli as cli
from learnlock import storage
from learnlock.cli import _is_github, _is_pdf, _is_url, _is_youtube, handle_input


class StubConsole:
    def __init__(self, inputs=None):
        self.inputs = list(inputs or [])
        self.messages = []

    def print(self, *args, **kwargs):
        self.messages.append(" ".join(str(arg) for arg in args))

    def input(self, prompt=""):
        return self.inputs.pop(0) if self.inputs else ""

    def clear(self):
        return None

    def get_time(self):
        return time.monotonic()


class TestUrlDetection:
    def test_http(self):
        assert _is_url("http://example.com")

    def test_https(self):
        assert _is_url("https://example.com")

    def test_www(self):
        assert _is_url("www.example.com")

    def test_not_url(self):
        assert not _is_url("just some text")

    def test_relative_path(self):
        assert not _is_url("./file.txt")


class TestIsYoutube:
    def test_standard(self):
        assert _is_youtube("https://www.youtube.com/watch?v=abc")

    def test_short(self):
        assert _is_youtube("https://youtu.be/abc")

    def test_mobile(self):
        assert _is_youtube("https://m.youtube.com/watch?v=abc")

    def test_not_youtube(self):
        assert not _is_youtube("https://example.com")


class TestIsPdf:
    def test_pdf_extension(self):
        assert _is_pdf("document.pdf")

    def test_pdf_url(self):
        assert _is_pdf("https://example.com/file.pdf")

    def test_pdf_in_path(self):
        assert _is_pdf("https://example.com/pdf/12345")

    def test_not_pdf(self):
        assert not _is_pdf("document.txt")


class TestIsGithub:
    def test_github_url(self):
        assert _is_github("https://github.com/user/repo")

    def test_not_github(self):
        assert not _is_github("https://gitlab.com/user/repo")


class TestHandleInput:
    def test_unknown_command(self, tmp_db):
        result = handle_input("/nonexistent")
        assert result is True  # Returns True (continue REPL)

    def test_help_command(self, tmp_db):
        result = handle_input("/help")
        assert result is True

    def test_quit_command(self, tmp_db):
        result = handle_input("/quit")
        assert result is False

    def test_exit_command(self, tmp_db):
        result = handle_input("/exit")
        assert result is False

    def test_unknown_text(self, tmp_db):
        result = handle_input("random text that is not a url")
        assert result is True


class TestPhase3Commands:
    def test_export_expands_tilde(self, tmp_db, tmp_path, monkeypatch):
        stub = StubConsole()
        monkeypatch.setattr(cli, "console", stub)
        monkeypatch.setenv("HOME", str(tmp_path))

        assert cli.cmd_export("~/learnlock-export.json") is True
        assert (tmp_path / "learnlock-export.json").exists()

    def test_import_invalid_payload_reports_error(self, tmp_db, tmp_path, monkeypatch):
        stub = StubConsole()
        monkeypatch.setattr(cli, "console", stub)

        bad_file = tmp_path / "bad.json"
        bad_file.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "sources": [{"id": 1, "url": "https://example.com"}],
                    "concepts": [],
                    "progress": [],
                    "explanations": [],
                    "duel_memory": [],
                    "cached_claims": [],
                }
            ),
            encoding="utf-8",
        )

        assert cli.cmd_import(str(bad_file)) is True
        assert any("Invalid export" in message for message in stub.messages)

    def test_delete_accepts_numeric_id_when_titles_collide(self, tmp_db, monkeypatch):
        first_id = storage.add_source("https://example.com/1", "Shared Title", "article", "one")
        second_id = storage.add_source("https://example.com/2", "Shared Title", "article", "two")
        stub = StubConsole()
        monkeypatch.setattr(cli, "console", stub)
        monkeypatch.setattr(cli.Prompt, "ask", lambda *args, **kwargs: "yes")

        assert cli.cmd_delete(str(second_id)) is True
        assert storage.get_source(second_id) is None
        assert storage.get_source(first_id) is not None

    def test_claims_generates_cache_before_first_duel(self, seeded_db, monkeypatch):
        stub = StubConsole(inputs=[""])
        monkeypatch.setattr(cli, "console", stub)
        monkeypatch.setattr(cli, "_check_api_keys", lambda **kwargs: True)
        monkeypatch.setattr(cli, "_spinner", lambda message: nullcontext())

        widget = next(
            concept for concept in storage.get_all_concepts() if concept["name"] == "Widget"
        )

        def fake_get_or_create_claims(ground_truth: str, concept_id: int | None = None):
            storage.save_cached_claims(
                concept_id,
                [
                    {
                        "statement": "Generated claim",
                        "claim_type": "definition",
                        "claim_index": 0,
                    }
                ],
            )
            return [SimpleNamespace(statement="Generated claim", claim_type="definition", index=0)]

        monkeypatch.setattr("learnlock.duel.get_or_create_claims", fake_get_or_create_claims)

        assert cli.cmd_claims(str(widget["id"])) is True
        assert storage.get_cached_claims(widget["id"])[0]["statement"] == "Generated claim"

    def test_visual_extracts_frame_for_specific_concept(self, tmp_db, monkeypatch):
        source_id = storage.add_source_with_concepts(
            url="https://www.youtube.com/watch?v=abcdefghijk",
            title="Video Source",
            source_type="youtube",
            raw_content="video transcript",
            segments=json.dumps([{"text": "Visual quote here", "start": 42.0}]),
            concepts=[
                {
                    "name": "Visual Concept",
                    "source_quote": "Visual quote here",
                    "ground_truth": "Visual quote here",
                    "question": "What is shown?",
                }
            ],
        )
        concept = storage.get_concepts_for_source(source_id)[0]
        stub = StubConsole()
        monkeypatch.setattr(cli, "console", stub)
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        monkeypatch.setattr(cli, "_spinner", lambda message: nullcontext())

        called = {}

        def fake_extract_frame(url: str, timestamp: float):
            called["url"] = url
            called["timestamp"] = timestamp
            return "A labeled diagram appears on screen."

        monkeypatch.setattr(
            "learnlock.tools.youtube.extract_frame_at_timestamp",
            fake_extract_frame,
        )

        assert cli.cmd_visual(str(concept["id"])) is True
        assert called == {
            "url": "https://www.youtube.com/watch?v=abcdefghijk",
            "timestamp": 42.0,
        }
