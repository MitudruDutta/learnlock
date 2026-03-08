"""PDF extraction tool."""

import os
from pathlib import Path

from ..security import download_to_tempfile


def extract_pdf(path_or_url: str) -> dict:
    """Extract text from PDF file or URL.
    Returns: {"title": str, "content": str, "url": str, "source_type": "pdf"}
    Or: {"error": str}
    """
    try:
        import pymupdf
    except ImportError:
        return {"error": "pymupdf not installed. Run: pip install pymupdf"}

    temp_path = None
    try:
        pdf_path = path_or_url

        # Download if URL
        if path_or_url.startswith(("http://", "https://")):
            temp_path = download_to_tempfile(path_or_url, suffix=".pdf")
            pdf_path = str(temp_path)
        else:
            pdf_path = str(Path(path_or_url).expanduser().resolve())

        if not os.path.exists(pdf_path):
            return {"error": f"File not found: {pdf_path}"}

        with pymupdf.open(pdf_path) as doc:
            text_parts = [page.get_text() for page in doc]
            content = "\n".join(text_parts)
            if not content.strip():
                return {"error": "No text found in PDF"}

            # Get title from metadata or filename
            title = doc.metadata.get("title") or os.path.basename(pdf_path).replace(".pdf", "")

        return {
            "title": title,
            "content": content,
            "url": path_or_url,
            "source_type": "pdf",
        }
    except Exception as e:
        return {"error": f"PDF extraction failed: {e}"}
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)
