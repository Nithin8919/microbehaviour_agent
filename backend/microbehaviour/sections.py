from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from bs4 import BeautifulSoup, Tag


@dataclass
class ContentBlock:
    heading: str
    snippet: str
    local_ctas: List[str]
    local_forms: List[Dict[str, str]]
    text_words: int
    link_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def extract_content_blocks(html: str) -> List[ContentBlock]:
    """Extract detailed content blocks with better structure for journey analysis.

    Heuristics:
    - Consider sizable containers (`section`, `div`, `main`, `article`) with enough text
    - Capture first heading, detailed snippet, CTAs, forms, word count, and link count
    - Preserve more context for better journey mapping
    """
    soup = BeautifulSoup(html, "lxml")
    blocks: List[ContentBlock] = []

    def heading_of(container: Tag) -> str:
        for level in ["h1", "h2", "h3", "h4"]:
            h = container.find(level)
            if h and h.get_text(strip=True):
                return h.get_text(strip=True)
        return ""

    def find_ctas(container: Tag) -> List[str]:
        labels: List[str] = []
        for el in container.find_all(["a", "button", "input"]):
            if el.name == "input" and el.get("type") == "submit":
                labels.append((el.get("value") or "Submit").strip())
            else:
                txt = el.get_text(strip=True)
                if txt:
                    labels.append(txt)
        # dedupe, preserve order
        seen: Dict[str, None] = {}
        out: List[str] = []
        for lbl in labels:
            if lbl not in seen:
                seen[lbl] = None
                out.append(lbl)
        return out

    def find_forms(container: Tag) -> List[Dict[str, str]]:
        forms: List[Dict[str, str]] = []
        for form in container.find_all("form"):
            fields: List[str] = []
            for inp in form.find_all(["input", "select", "textarea"]):
                name = (
                    inp.get("name")
                    or inp.get("id")
                    or inp.get("placeholder")
                    or inp.get("type")
                    or "field"
                )
                if name:
                    fields.append(str(name).strip())
            forms.append({"fields": ", ".join(fields)})
        return forms

    def get_detailed_snippet(container: Tag) -> str:
        """Get a more detailed snippet that preserves structure better."""
        # Try to get text with some structure preserved
        text_parts = []
        
        # Get headings first
        for h in container.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            if h.get_text(strip=True):
                text_parts.append(f"HEADING: {h.get_text(strip=True)}")
        
        # Get paragraphs and list items
        for p in container.find_all(["p", "li", "div"]):
            text = p.get_text(strip=True)
            if text and len(text) > 10:  # Only meaningful text
                text_parts.append(text)
        
        # Combine and truncate
        combined = " | ".join(text_parts)
        return combined[:500]  # Increased from 280 to 500

    # Look for more container types
    candidates = soup.find_all(["section", "div", "main", "article", "aside"])
    
    for container in candidates:
        text = container.get_text(" ", strip=True)
        words = text.split()
        
        # More flexible word count - capture smaller but meaningful blocks
        if len(words) < 5:  # Much more permissive
            continue
            
        heading = heading_of(container)
        snippet = get_detailed_snippet(container)
        links = container.find_all("a")
        
        # Much more permissive - capture any container with some content
        if heading or len(words) > 10 or snippet:
            blocks.append(
                ContentBlock(
                    heading=heading,
                    snippet=snippet,
                    local_ctas=find_ctas(container),
                    local_forms=find_forms(container),
                    text_words=len(words),
                    link_count=len(links),
                )
            )

    # Better ranking: prefer blocks with headings, more text, and meaningful content
    def rank_block(block: ContentBlock) -> tuple:
        has_heading = bool(block.heading)
        has_ctas = len(block.local_ctas) > 0
        has_forms = len(block.local_forms) > 0
        meaningful_content = block.text_words > 30
        
        # Priority: heading + CTAs/forms + meaningful content
        return (
            has_heading,
            has_ctas or has_forms,
            meaningful_content,
            block.text_words,
            -block.link_count  # Fewer links often means more focused content
        )
    
    blocks.sort(key=rank_block, reverse=True)
    
    # If we still have no blocks, create a fallback block from the entire page
    if not blocks:
        full_text = soup.get_text(" ", strip=True)
        if full_text:
            words = full_text.split()
            blocks.append(
                ContentBlock(
                    heading="Page Content",
                    snippet=full_text[:500],
                    local_ctas=find_ctas(soup),
                    local_forms=find_forms(soup),
                    text_words=len(words),
                    link_count=len(soup.find_all("a")),
                )
            )
    
    # Limit to top blocks to avoid overwhelming the LLM
    return blocks[:25]


