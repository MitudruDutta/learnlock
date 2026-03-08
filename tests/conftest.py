"""Shared fixtures for learn-lock tests."""

from pathlib import Path

import pytest

from learnlock import config
from learnlock import storage


@pytest.fixture()
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Provide a fresh temporary database for each test."""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", db_path)
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    storage.reset_init_cache()
    storage.init_db(db_path)
    return db_path


@pytest.fixture()
def mock_llm(monkeypatch: pytest.MonkeyPatch):
    """Mock llm.call() to avoid real API calls. Returns a controller object.

    Usage:
        def test_something(mock_llm):
            mock_llm.set_response("hello")
            # or
            mock_llm.set_responses(["first", "second"])
    """

    class _MockLLM:
        def __init__(self):
            self.responses: list[str] = ["mocked response"]
            self._call_count = 0
            self.calls: list[dict] = []

        def set_response(self, text: str):
            self.responses = [text]
            self._call_count = 0

        def set_responses(self, texts: list[str]):
            self.responses = list(texts)
            self._call_count = 0

        def __call__(self, prompt, **kwargs):
            self.calls.append({"prompt": prompt, **kwargs})
            idx = min(self._call_count, len(self.responses) - 1)
            self._call_count += 1
            return self.responses[idx]

    mock = _MockLLM()
    monkeypatch.setattr("learnlock.llm.call", mock)
    return mock


@pytest.fixture()
def seeded_db(tmp_db):
    """A database with one source and two concepts already inserted."""
    source_id = storage.add_source_with_concepts(
        url="https://example.com/test",
        title="Test Source",
        source_type="article",
        raw_content="Some test content about widgets and gadgets.",
        concepts=[
            {
                "name": "Widget",
                "source_quote": "Widgets are reusable components",
                "ground_truth": "Widgets encapsulate UI and state",
                "question": "What is a Widget?",
            },
            {
                "name": "Gadget",
                "source_quote": "Gadgets extend widgets",
                "ground_truth": "Gadgets add behaviour to widgets",
                "question": "What is a Gadget?",
            },
        ],
    )
    return source_id
