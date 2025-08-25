from __future__ import annotations

import re
from bs4 import BeautifulSoup


def html_to_text(html: str) -> str:
    """Convert HTML to readable plain text and normalize whitespace."""
    soup = BeautifulSoup(html, "lxml")

    for element in soup(["script", "style", "noscript", "svg", "img"]):
        element.decompose()

    text = soup.get_text(" ", strip=True)
    text = _collapse_whitespace(text)
    return text


def _collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def truncate_text(text: str, max_chars: int = 12000) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 3)] + "..."


