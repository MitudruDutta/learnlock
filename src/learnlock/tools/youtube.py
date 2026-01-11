"""YouTube transcript extraction."""

import re
import os
from typing import Optional


def extract_youtube(url: str) -> dict:
    """Extract transcript from YouTube video.
    
    Returns: {"title": str, "content": str, "url": str, "source_type": "youtube"}
    Or: {"error": str}
    """
    video_id = _extract_video_id(url)
    if not video_id:
        return {"error": "Invalid YouTube URL"}
    
    # Try YouTube transcript API first
    result = _try_youtube_api(video_id, url)
    if "error" not in result:
        return result
    
    # Fallback to Whisper if GROQ_API_KEY is set
    if os.getenv("GROQ_API_KEY"):
        whisper_result = _try_whisper_fallback(video_id, url)
        if "error" not in whisper_result:
            return whisper_result
        # Return combined error
        return {"error": f"{result['error']}. Whisper fallback: {whisper_result['error']}"}
    
    return result


def _try_youtube_api(video_id: str, url: str) -> dict:
    """Get transcript via YouTube API."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=("en",))
        
        text = " ".join([snippet.text for snippet in transcript])
        title = _get_video_title(video_id) or f"YouTube Video ({video_id})"
        
        return {
            "title": title,
            "content": text,
            "url": url,
            "source_type": "youtube",
        }
    except Exception as e:
        return {"error": str(e)}


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
            
            # Get title first
            title = f"YouTube Video ({video_id})"
            try:
                with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get("title", title)
            except:
                pass
            
            # Download audio
            ydl_opts = {
                "format": "m4a/bestaudio[ext=m4a]/bestaudio",
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
    except:
        return None


def _extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r"(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:embed/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None
