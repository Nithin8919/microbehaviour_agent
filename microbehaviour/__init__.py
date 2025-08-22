from __future__ import annotations

# Load .env automatically if present to pick up OPENAI_API_KEY (and others)
try:  # pragma: no cover
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

__all__: list[str] = []



