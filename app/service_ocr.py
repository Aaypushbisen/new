import os
import requests


def ocr_from_url(file_url: str) -> str:
    """Perform OCR using ocr.space given a publicly accessible file URL.

    Returns a best-effort concatenated text string; returns empty string on failure.
    """
    api_key = os.getenv("OCR_SPACE_API_KEY")
    if not api_key:
        return ""
    try:
        response = requests.post(
            "https://api.ocr.space/parse/image",
            data={
                "apikey": api_key,
                "url": file_url,
                "OCREngine": 2,
                "scale": True,
                "isTable": True,
            },
            timeout=60,
        )
        response.raise_for_status()
        parsed = response.json()
        results = parsed.get("ParsedResults") or []
        parts = []
        for item in results:
            text = item.get("ParsedText") or ""
            if text:
                parts.append(text)
        return "\n".join(parts)
    except Exception:
        return ""

