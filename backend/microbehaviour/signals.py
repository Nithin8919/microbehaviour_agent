from __future__ import annotations

import re
from typing import Any, Dict, List
import itertools
import string
from bs4 import BeautifulSoup


CTA_KEYWORDS = [
    "book a call",
    "schedule",
    "get started",
    "sign up",
    "start now",
    "try",
    "contact",
    "buy",
]

SOCIAL_KEYWORDS = ["testimonial", "case study", "reviews", "as seen on", "clients", "logos"]

SCHEDULING_KEYWORDS = ["calendly", "hubspot meetings", "savvycal", "oncehub", "calendar"]


def compute_site_facts(text: str, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    t = text.lower()
    facts: Dict[str, Any] = {}

    # CTA occurrences
    cta_hits = sum(len(re.findall(re.escape(k), t)) for k in CTA_KEYWORDS)
    block_ctas = sum(len(b.get("local_ctas", [])) for b in blocks)
    facts["cta_occurrences"] = cta_hits + block_ctas
    facts["has_cta"] = (cta_hits + block_ctas) > 0

    # Social proof presence
    social_hits = sum(len(re.findall(k, t)) for k in SOCIAL_KEYWORDS)
    facts["has_social_proof"] = social_hits > 0

    # Forms
    forms_count = sum(len(b.get("local_forms", [])) for b in blocks)
    facts["forms_count"] = forms_count
    facts["has_form"] = forms_count > 0

    # Scheduling widget
    facts["has_scheduler"] = any(k in t for k in SCHEDULING_KEYWORDS)

    # FAQ / Pricing quick checks
    facts["has_faq"] = bool(re.search(r"\bf(aq|requently asked questions)\b", t))
    facts["has_pricing"] = bool(re.search(r"\b(pricing|plans|cost)\b", t))

    return facts


def derive_supporting_signals(html_pages: List[str], blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Derive additional concrete UI signals to ground the model.

    - navLabels: texts from <nav> links
    - headings: top-level headings from pages
    - ctaLabels: unique CTA/button labels aggregated across pages/blocks
    - guaranteePhrases: sentences containing "guarantee" or "money back"
    - pricingAmounts: dollar amounts or K patterns discovered
    - testimonialsCount: count of testimonial/case study/reviews mentions
    """
    nav_labels: List[str] = []
    headings: List[str] = []
    cta_labels: List[str] = list({lbl for b in blocks for lbl in (b.get("local_ctas") or []) if lbl})
    guarantee_phrases: List[str] = []
    pricing_amounts: List[str] = []
    testimonials_count = 0

    def clean_text(s: str) -> str:
        s = " ".join(s.split())
        return s.strip(string.whitespace)

    for html in html_pages:
        soup = BeautifulSoup(html, "lxml")
        # nav labels
        for nav in soup.find_all("nav"):
            for a in nav.find_all("a"):
                t = a.get_text(strip=True)
                if t:
                    nav_labels.append(t)
        # headings
        for level in ["h1", "h2"]:
            for h in soup.find_all(level):
                t = h.get_text(strip=True)
                if t:
                    headings.append(t)
        # CTA labels global
        for el in soup.find_all(["a", "button", "input"]):
            if el.name == "input" and el.get("type") == "submit":
                val = el.get("value") or "Submit"
                cta_labels.append(val.strip())
            else:
                t = el.get_text(strip=True)
                if t:
                    cta_labels.append(t)
        # guarantee phrases and pricing
        page_text = soup.get_text(" ", strip=True)
        # sentences with guarantee
        for sent in page_text.split("."):
            if any(k in sent.lower() for k in ["guarantee", "money back"]):
                guarantee_phrases.append(clean_text(sent) + ".")
        # pricing like $10, $2,997, $10k
        import re

        for m in re.findall(r"\$\s?\d[\d,]*(?:\.\d{2})?\s?[kK]?", page_text):
            pricing_amounts.append(m.strip())
        # testimonials mentions
        testimonials_count += len(re.findall(r"testimonial|case study|reviews", page_text, flags=re.I))

    # Dedupe while preserving order
    def dedupe(seq: List[str]) -> List[str]:
        seen = set()
        out: List[str] = []
        for s in seq:
            if s and s not in seen:
                seen.add(s)
                out.append(s)
        return out

    return {
        "navLabels": dedupe(nav_labels)[:25],
        "headings": dedupe(headings)[:40],
        "ctaLabels": dedupe(cta_labels)[:40],
        "guaranteePhrases": dedupe(guarantee_phrases)[:20],
        "pricingAmounts": dedupe(pricing_amounts)[:20],
        "testimonialsCount": testimonials_count,
    }


