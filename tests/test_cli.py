"""Tests for CLI utilities and command routing."""

from learnlock.cli import _is_url, _is_youtube, _is_pdf, _is_github, handle_input


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
