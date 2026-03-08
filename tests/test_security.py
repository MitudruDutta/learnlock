from pathlib import Path

import pytest

from learnlock import config
from learnlock.duel import BeliefState, save_duel_data
from learnlock.security import sanitize_filename, validate_remote_url


@pytest.mark.parametrize(
    ("url", "message"),
    [
        ("ftp://example.com/file.pdf", "Only http and https URLs are supported"),
        ("http://127.0.0.1/file.pdf", "Local and private network addresses are blocked"),
        ("http://localhost/file.pdf", "Local and private network addresses are blocked"),
        ("https://user:pass@example.com/file.pdf", "URLs with embedded credentials are not allowed"),
    ],
)
def test_validate_remote_url_rejects_unsafe_targets(url: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        validate_remote_url(url)


def test_validate_remote_url_accepts_public_https() -> None:
    assert validate_remote_url("https://example.com/article") == "https://example.com/article"


def test_sanitize_filename_removes_path_components() -> None:
    assert sanitize_filename("../../duel results?.json") == "duel_results_.json"


def test_save_duel_data_stays_inside_data_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    saved_path = Path(save_duel_data(BeliefState(ground_truth="truth"), "../../escape/path"))

    assert saved_path.exists()
    assert tmp_path.resolve() in saved_path.resolve().parents
    assert ".." not in saved_path.name
