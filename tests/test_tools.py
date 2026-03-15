"""Tests for content extraction tools."""

from learnlock.tools import extract_content
from learnlock.tools.youtube import _normalize_youtube_url, find_timestamp_for_text


class TestNormalizeYoutubeUrl:
    def test_standard_watch_url(self):
        result = _normalize_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result is not None
        video_id, url = result
        assert video_id == "dQw4w9WgXcQ"
        assert url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def test_short_url(self):
        result = _normalize_youtube_url("https://youtu.be/dQw4w9WgXcQ")
        assert result is not None
        assert result[0] == "dQw4w9WgXcQ"

    def test_embed_url(self):
        result = _normalize_youtube_url("https://www.youtube.com/embed/dQw4w9WgXcQ")
        assert result is not None
        assert result[0] == "dQw4w9WgXcQ"

    def test_shorts_url(self):
        result = _normalize_youtube_url("https://www.youtube.com/shorts/dQw4w9WgXcQ")
        assert result is not None
        assert result[0] == "dQw4w9WgXcQ"

    def test_mobile_url(self):
        result = _normalize_youtube_url("https://m.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result is not None
        assert result[0] == "dQw4w9WgXcQ"

    def test_music_url(self):
        result = _normalize_youtube_url("https://music.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result is not None
        assert result[0] == "dQw4w9WgXcQ"

    def test_invalid_host(self):
        assert _normalize_youtube_url("https://notyoutube.com/watch?v=dQw4w9WgXcQ") is None

    def test_invalid_video_id_too_short(self):
        assert _normalize_youtube_url("https://youtube.com/watch?v=abc") is None

    def test_invalid_video_id_too_long(self):
        assert _normalize_youtube_url("https://youtube.com/watch?v=abcdefghijkl") is None

    def test_invalid_video_id_bad_chars(self):
        assert _normalize_youtube_url("https://youtube.com/watch?v=abc!@#$%^&*") is None

    def test_no_video_id(self):
        assert _normalize_youtube_url("https://youtube.com/") is None

    def test_empty_string(self):
        assert _normalize_youtube_url("") is None


class TestFindTimestampForText:
    def test_exact_match(self):
        segments = [
            {"text": "hello world", "start": 0.0},
            {"text": "this is about widgets", "start": 10.0},
            {"text": "and gadgets too", "start": 20.0},
        ]
        ts = find_timestamp_for_text(segments, "this is about widgets")
        assert ts == 10.0

    def test_word_overlap_match(self):
        segments = [
            {"text": "intro to the topic", "start": 0.0},
            {"text": "widgets are reusable components in modern frameworks", "start": 15.0},
        ]
        ts = find_timestamp_for_text(segments, "widgets are reusable components")
        assert ts is not None

    def test_no_match(self):
        segments = [
            {"text": "hello world", "start": 0.0},
        ]
        ts = find_timestamp_for_text(segments, "quantum physics entanglement")
        assert ts is None

    def test_empty_segments(self):
        assert find_timestamp_for_text([], "anything") is None


class TestExtractContentDispatch:
    """Test that extract_content routes to the correct extractor."""

    def test_unsupported_source(self):
        result = extract_content("some random text")
        assert "error" in result

    def test_youtube_dispatch(self, monkeypatch):
        monkeypatch.setattr(
            "learnlock.tools.extract_youtube",
            lambda url: {"source_type": "youtube", "url": url},
        )
        result = extract_content("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result["source_type"] == "youtube"

    def test_github_dispatch(self, monkeypatch):
        monkeypatch.setattr(
            "learnlock.tools.extract_github",
            lambda url: {"source_type": "github", "url": url},
        )
        result = extract_content("https://github.com/user/repo")
        assert result["source_type"] == "github"

    def test_pdf_dispatch(self, monkeypatch):
        monkeypatch.setattr(
            "learnlock.tools.extract_pdf",
            lambda url: {"source_type": "pdf", "url": url},
        )
        result = extract_content("https://example.com/paper.pdf")
        assert result["source_type"] == "pdf"

    def test_article_dispatch(self, monkeypatch):
        monkeypatch.setattr(
            "learnlock.tools.extract_article",
            lambda url: {"source_type": "article", "url": url},
        )
        result = extract_content("https://example.com/blog-post")
        assert result["source_type"] == "article"

    def test_youtu_be_dispatch(self, monkeypatch):
        monkeypatch.setattr(
            "learnlock.tools.extract_youtube",
            lambda url: {"source_type": "youtube", "url": url},
        )
        result = extract_content("https://youtu.be/dQw4w9WgXcQ")
        assert result["source_type"] == "youtube"

    def test_pdf_in_path_dispatch(self, monkeypatch):
        monkeypatch.setattr(
            "learnlock.tools.extract_pdf",
            lambda url: {"source_type": "pdf", "url": url},
        )
        result = extract_content("https://arxiv.org/pdf/1234.5678")
        assert result["source_type"] == "pdf"
