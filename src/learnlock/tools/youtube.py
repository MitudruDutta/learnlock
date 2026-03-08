"""YouTube transcript extraction with timestamps for concept linking."""

import os
from typing import Optional
from urllib.parse import parse_qs, urlparse

from .. import config

_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}


def extract_youtube(url: str) -> dict:
    """Extract transcript with timestamps from YouTube.
    Returns: {
        "title": str,
        "content": str,
        "url": str,
        "source_type": "youtube",
        "segments": [{"text": str, "start": float}, ...]
    }
    Or: {"error": str}
    """
    normalized = _normalize_youtube_url(url)
    if not normalized:
        return {"error": "Invalid YouTube URL"}
    video_id, canonical_url = normalized

    result = _try_youtube_api(video_id, canonical_url)
    if "error" in result:
        if os.getenv("GROQ_API_KEY"):
            result = _try_whisper_fallback(video_id, canonical_url)

    return result


def _try_youtube_api(video_id: str, url: str) -> dict:
    """Get transcript with timestamps via YouTube API."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        api = YouTubeTranscriptApi()
        transcript = None

        try:
            transcript = api.fetch(video_id, languages=("en", "en-US", "en-GB"))
        except Exception:
            try:
                transcript_list = api.list(video_id)
                if transcript_list:
                    transcript = transcript_list[0].fetch()
            except Exception:
                pass

        if not transcript:
            return {"error": "No transcript available"}

        segments = [{"text": s.text, "start": s.start} for s in transcript]
        text = " ".join([s.text for s in transcript])
        title = _get_video_title(video_id) or f"YouTube Video ({video_id})"

        return {
            "title": title,
            "content": text,
            "url": url,
            "source_type": "youtube",
            "segments": segments,
        }
    except Exception as e:
        return {"error": str(e)}


def find_timestamp_for_text(segments: list[dict], search_text: str) -> Optional[float]:
    """Find timestamp where a concept appears in transcript."""
    if not segments:
        return None

    search_lower = search_text.lower()
    search_words = set(search_lower.split())

    best_match = None
    best_score = 0

    for seg in segments:
        seg_text = seg["text"].lower()
        if search_lower[:30] in seg_text:
            return seg["start"]
        seg_words = set(seg_text.split())
        overlap = len(search_words & seg_words)
        if overlap > best_score:
            best_score = overlap
            best_match = seg["start"]

    return best_match if best_score >= 2 else None


def get_video_link_at_time(url: str, timestamp: float) -> str:
    """Generate YouTube URL at specific timestamp."""
    normalized = _normalize_youtube_url(url)
    if not normalized:
        return url
    video_id, _ = normalized
    return f"https://youtube.com/watch?v={video_id}&t={int(timestamp)}"


def extract_frame_at_timestamp(url: str, timestamp: float) -> Optional[str]:
    """Extract frame at timestamp and describe with Gemini Vision. On-demand when user fails."""
    if not os.getenv("GEMINI_API_KEY"):
        return None

    normalized = _normalize_youtube_url(url)
    if not normalized:
        return None
    video_id, canonical_url = normalized

    try:
        import subprocess
        import tempfile

        import google.generativeai as genai
        import PIL.Image
        import yt_dlp

        genai.configure(api_key=os.environ["GEMINI_API_KEY"])

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "v.mp4")
            frame_path = os.path.join(tmpdir, "frame.jpg")
            _validate_downloadable_video(canonical_url)

            with yt_dlp.YoutubeDL(
                {
                    "format": "worst[ext=mp4]/worst",
                    "max_filesize": config.MAX_REMOTE_DOWNLOAD_BYTES,
                    "noplaylist": True,
                    "outtmpl": video_path,
                    "quiet": True,
                    "no_warnings": True,
                }
            ) as ydl:
                ydl.download([canonical_url])

            if not os.path.exists(video_path):
                return None

            subprocess.run(
                [
                    "ffmpeg",
                    "-ss",
                    str(timestamp),
                    "-i",
                    video_path,
                    "-frames:v",
                    "1",
                    "-q:v",
                    "2",
                    frame_path,
                ],
                capture_output=True,
                timeout=30,
            )

            if not os.path.exists(frame_path):
                return None

            img = PIL.Image.open(frame_path)
            model = genai.GenerativeModel("gemini-2.5-flash")
            resp = model.generate_content(
                [
                    "Describe what is shown in this educational video frame. "
                    "Focus on: equations, diagrams, text, code, formulas, whiteboard. "
                    "Transcribe any visible text exactly. Be specific.",
                    img,
                ]
            )

            return resp.text.strip() if resp.text else None

    except Exception:
        return None


def _try_whisper_fallback(video_id: str, url: str) -> dict:
    """Fallback: download audio and transcribe with Groq Whisper."""
    try:
        import tempfile

        import yt_dlp
        from groq import Groq
    except ImportError as e:
        return {"error": f"Missing dependency for Whisper fallback: {e}"}

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "GROQ_API_KEY not set"}

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = os.path.join(tmpdir, "audio")
            info = _validate_downloadable_video(url)

            # Get title first
            title = info.get("title") or f"YouTube Video ({video_id})"

            # Download audio
            ydl_opts = {
                "format": "m4a/bestaudio[ext=m4a]/bestaudio",
                "max_filesize": config.MAX_REMOTE_DOWNLOAD_BYTES,
                "noplaylist": True,
                "outtmpl": audio_path + ".%(ext)s",
                "quiet": True,
                "no_warnings": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Find downloaded file
            audio_file = None
            for f in os.listdir(tmpdir):
                if f.startswith("audio."):
                    audio_file = os.path.join(tmpdir, f)
                    break

            if not audio_file or not os.path.exists(audio_file):
                return {"error": "Audio download failed"}

            # Check size (25MB limit)
            file_size = os.path.getsize(audio_file)
            if file_size > 25 * 1024 * 1024:
                return {"error": f"Audio too large ({file_size // 1024 // 1024}MB > 25MB limit)"}

            # Transcribe with Groq Whisper
            client = Groq(api_key=api_key)
            with open(audio_file, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file), f),
                    model="whisper-large-v3",
                )

            return {
                "title": title,
                "content": transcription.text,
                "url": url,
                "source_type": "youtube",
            }
    except Exception as e:
        return {"error": f"Whisper transcription failed: {e}"}


def _get_video_title(video_id: str) -> Optional[str]:
    """Try to get video title using yt-dlp."""
    try:
        import yt_dlp

        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
            info = ydl.extract_info(f"https://youtube.com/watch?v={video_id}", download=False)
            return info.get("title")
    except Exception:
        return None


def _extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from various YouTube URL formats."""
    normalized = _normalize_youtube_url(url)
    return normalized[0] if normalized else None


def _normalize_youtube_url(url: str) -> Optional[tuple[str, str]]:
    """Accept only canonical YouTube hosts and return a trusted watch URL."""
    parsed = urlparse(url.strip())
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if hostname not in _YOUTUBE_HOSTS:
        return None

    video_id = ""
    if hostname == "youtu.be":
        video_id = parsed.path.lstrip("/").split("/", 1)[0]
    else:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        else:
            parts = [part for part in parsed.path.split("/") if part]
            if len(parts) >= 2 and parts[0] in {"embed", "shorts", "live", "v"}:
                video_id = parts[1]

    valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    if len(video_id) != 11 or any(ch not in valid_chars for ch in video_id):
        return None

    return video_id, f"https://www.youtube.com/watch?v={video_id}"


def _validate_downloadable_video(url: str) -> dict:
    """Reject oversized or excessively long downloads before yt-dlp writes anything."""
    import yt_dlp

    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "noplaylist": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    duration = info.get("duration")
    if duration and duration > config.MAX_YOUTUBE_DURATION_SECONDS:
        raise ValueError(
            f"Video is too long ({duration}s > {config.MAX_YOUTUBE_DURATION_SECONDS}s limit)"
        )

    estimated_size = info.get("filesize") or info.get("filesize_approx")
    if estimated_size and estimated_size > config.MAX_REMOTE_DOWNLOAD_BYTES:
        raise ValueError(
            f"Video is too large ({estimated_size // (1024 * 1024)}MB > "
            f"{config.MAX_REMOTE_DOWNLOAD_BYTES // (1024 * 1024)}MB limit)"
        )

    return info
