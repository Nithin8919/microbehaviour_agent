from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from .schemas import ExperienceItem, TimelineStage, ExperienceReport


FALLBACK_PRIORITY = 5


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(upper, value))


def extract_json_maybe(text: str) -> Dict[str, Any]:
    text = text.strip()
    # Remove fences if present
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text, flags=re.IGNORECASE).strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    # Substring between first { and last }
    if not (text.startswith("{") and text.endswith("}")):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
    try:
        return json.loads(text)
    except Exception:
        return {"raw": text}


def normalize_items(items: List[Dict[str, Any]], allowed_ctas: List[str] | None = None) -> List[ExperienceItem]:
    normalized: List[ExperienceItem] = []
    for raw in items:
        # split compound behaviors
        behavior = (raw.get("behavior") or raw.get("action") or "").strip()
        if not behavior:
            continue
        parts = split_atomic(behavior)
        for part in parts:
            # sanitize numeric fields before constructing the model
            priority_val = _coerce_int(raw.get("priority"), FALLBACK_PRIORITY)
            if priority_val is None:
                priority_val = FALLBACK_PRIORITY
            priority_val = _clamp(priority_val, 1, 10)

            fs_val = _coerce_int(raw.get("frictionScore"), None)

            e = ExperienceItem(
                behavior=part,
                explanation=_clean_text(raw.get("explanation")),
                nudge=_clean_text(raw.get("nudge")),
                priority=priority_val,
                friction=_clean_text(raw.get("friction")),
                frictionScore=None,  # set below
                section=_clean_text(raw.get("section")),
            )
            if fs_val is None:
                e.frictionScore = infer_friction_score(e)
            else:
                e.frictionScore = _clamp(fs_val, 1, 10)
            # If behavior references a CTA label not present, soften to generic 'the CTA'
            if allowed_ctas is not None and any(token in e.behavior.lower() for token in ["book a call", "book", "call"]):
                if not any(lbl.lower() in e.behavior.lower() for lbl in allowed_ctas):
                    e.behavior = re.sub(r"book[^\w]*a[^\w]*call", "the CTA", e.behavior, flags=re.IGNORECASE)
                    if e.nudge:
                        e.nudge = re.sub(r"book[^\w]*a[^\w]*call", "the CTA", e.nudge, flags=re.IGNORECASE)
            normalized.append(e)

    # dedupe by behavior + section
    seen: set[tuple[str, str | None]] = set()
    deduped: List[ExperienceItem] = []
    for it in normalized:
        key = (normalize_key(it.behavior), it.section)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(it)
    return deduped


def split_atomic(text: str) -> List[str]:
    parts = re.split(r"\s*(?:and|then|&|;|→|->)\s*", text, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _coerce_int(value: Any, default: int | None) -> int | None:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def normalize_key(text: str) -> str:
    text = re.sub(r"\s+", " ", text.lower().strip())
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text


def infer_friction_score(item: ExperienceItem) -> int:
    score = item.priority or FALLBACK_PRIORITY
    s = f"{item.behavior} {item.explanation or ''} {item.friction or ''}".lower()
    # keyword biases
    if any(k in s for k in ["blocker", "error", "fail", "stuck", "mandatory", "payment"]):
        score = max(score, 8)
    if any(k in s for k in ["confus", "hesitat", "unclear", "inconsist"]):
        score = max(score, 6)
    return max(1, min(10, score))


def backfill_timeline(stages: List[TimelineStage]) -> List[TimelineStage]:
    # Ensure each stage has at least 2 items when possible by borrowing from others
    pool: List[ExperienceItem] = []
    for st in stages:
        if len(st.items) > 2:
            pool.extend(st.items[2:])
            st.items = st.items[:2]
    for st in stages:
        while len(st.items) < 2 and pool:
            st.items.append(pool.pop(0))
    # reindex
    for idx, st in enumerate(stages, start=1):
        st.index = idx
    return stages

