"""Security and safety helpers for remote ingestion and file output."""

from __future__ import annotations

import ipaddress
import socket
import tempfile
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

from . import config

REQUEST_HEADERS = {
    "User-Agent": "learn-lock/0.1.6 (+https://github.com/MitudruDutta/learnlock)",
}
_BLOCKED_HOST_SUFFIXES = (
    ".internal",
    ".lan",
    ".local",
    ".localdomain",
    ".localhost",
    ".home.arpa",
)
_MAX_FILENAME_LENGTH = 80
_SAFE_FILENAME_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
)


def validate_remote_url(url: str, *, allowed_hosts: tuple[str, ...] | None = None) -> str:
    """Reject unsafe URLs before touching the network."""

    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http and https URLs are supported")
    if not parsed.hostname:
        raise ValueError("URL must include a hostname")
    if parsed.username or parsed.password:
        raise ValueError("URLs with embedded credentials are not allowed")

    hostname = parsed.hostname.rstrip(".").lower()
    if allowed_hosts and not any(
        hostname == allowed or hostname.endswith(f".{allowed}") for allowed in allowed_hosts
    ):
        raise ValueError(f"Only {', '.join(allowed_hosts)} URLs are supported here")

    if _is_local_hostname(hostname):
        raise ValueError("Local and private network addresses are blocked")

    try:
        for resolved_ip in _resolve_public_ips(hostname):
            if not resolved_ip.is_global:
                raise ValueError("Local and private network addresses are blocked")
    except socket.gaierror:
        # DNS failures are handled by the actual fetcher. This still blocks obvious local targets.
        pass

    return parsed.geturl()


def download_to_tempfile(url: str, *, suffix: str, max_bytes: int | None = None) -> Path:
    """Stream a remote file to disk with redirect and size validation."""

    validate_remote_url(url)
    limit = max_bytes or config.MAX_REMOTE_DOWNLOAD_BYTES
    temp_path: Path | None = None

    try:
        with _get_with_safe_redirects(url) as response:
            response.raise_for_status()

            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > limit:
                raise ValueError(f"Remote file is larger than {limit // (1024 * 1024)}MB")

            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
                temp_path = Path(handle.name)
                bytes_written = 0

                for chunk in response.iter_content(chunk_size=64 * 1024):
                    if not chunk:
                        continue
                    bytes_written += len(chunk)
                    if bytes_written > limit:
                        raise ValueError(f"Remote file is larger than {limit // (1024 * 1024)}MB")
                    handle.write(chunk)

        if temp_path is None:
            raise RuntimeError("Temporary file was not created")
        return temp_path
    except Exception:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise


def _get_with_safe_redirects(url: str, *, max_redirects: int = 5) -> requests.Response:
    current_url = validate_remote_url(url)
    session = requests.Session()
    redirects_seen = 0

    try:
        while True:
            response = session.get(
                current_url,
                stream=True,
                timeout=(5, 30),
                allow_redirects=False,
                headers=REQUEST_HEADERS,
            )

            if response.is_redirect or response.is_permanent_redirect:
                location = response.headers.get("Location")
                if not location:
                    response.close()
                    raise ValueError("Redirect response missing Location header")

                redirects_seen += 1
                if redirects_seen > max_redirects:
                    response.close()
                    raise ValueError("Too many redirects")

                next_url = validate_remote_url(urljoin(current_url, location))
                response.close()
                current_url = next_url
                continue

            response.url = current_url

            original_close = response.close

            def close_with_session_cleanup() -> None:
                original_close()
                session.close()

            response.close = close_with_session_cleanup
            return response
    except Exception:
        session.close()
        raise


def sanitize_filename(value: str, *, default: str = "item") -> str:
    """Remove path separators and keep filenames portable."""

    cleaned = "".join(ch if ch in _SAFE_FILENAME_CHARS else "_" for ch in value.strip())
    cleaned = cleaned.strip("._-")[:_MAX_FILENAME_LENGTH]
    return cleaned or default


def _is_local_hostname(hostname: str) -> bool:
    if hostname in {"localhost"} or hostname.endswith(_BLOCKED_HOST_SUFFIXES):
        return True

    try:
        return not ipaddress.ip_address(hostname).is_global
    except ValueError:
        return False


def _resolve_public_ips(hostname: str) -> set[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    return {ipaddress.ip_address(info[4][0]) for info in infos}
