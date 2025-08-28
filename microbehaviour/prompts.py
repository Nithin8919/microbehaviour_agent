from __future__ import annotations

from typing import List, Dict, Any


def build_analysis_messages_from_signals(
    *,
    url: str,
    goal: str | None,
    title: str | None,
    text_sample: str,
    blocks: List[Dict[str, Any]],
    facts: Dict[str, Any] | None = None,
    allowed_cta_labels: List[str] | None = None,
) -> List[Dict[str, str]]:
    """
    Build grounded LLM messages for CRO analysis:
    - Inputs are structured site signals (hero/sections/ctas/forms/text) + optional facts and allowed CTA labels
    - Output must be STRICT JSON with keys:
      {
        "items": [
          {
            "behavior": str,
            "explanation": str,
            "nudge": str,
            "priority": int (1-10),
            "friction"?: str,
            "frictionScore"?: int (1-10)
          }, ...
        ],
        "timeline": [
          {
            "index": int (1-based),
            "stage": str,
            "section"?: str,        # e.g., "H2: Pricing (Block #5)"
            "observed": str,        # 1–2 sentences grounded in scraped content for that section
            "items": [ ... ExperienceItem objects (1–5) ... ]
          }, ...
        ]
      }
    """
    system = (
        "You are a CRO/UX analyst. You will receive structured signals from a website plus an optional business goal. "
        "Infer likely visitor microbehaviors, sources of friction, and targeted persuasion nudges. "
        "Return ONLY strict JSON with keys: items (list), timeline (list). Do not include markdown, prose, or comments."
        "\n\nOutput contract:\n"
        "- items: Array of ExperienceItem, each with fields: behavior, explanation, nudge, priority (1-10), friction?, frictionScore?\n"
        "- timeline: 8–10 ordered stages, each with: index, stage, section?, observed, items (1–5 ExperienceItem objects)\n"
        "\nHard rules:\n"
        "1) Ground EVERYTHING in the provided signals. When writing a stage's 'observed', use the actual section content (heading/snippet/CTAs/form fields).\n"
        "2) Atomic items only: one behavior per item. If you think 'A and B', split into two items in the output list and reference the relevant one in timeline stages.\n"
        "3) Avoid duplicates: do not repeat the same idea with slightly different wording across items or across stages. Prefer the highest-impact phrasing once.\n"
        "4) Stage relevance: Only place form/CTA-related items in CTA or explicit form sections; put pricing doubts in Pricing; proof-seeking in Social Proof; process clarity in How It Works; etc.\n"
        "5) Use ONLY exact CTA labels from allowedCtas when citing a CTA. If a label is not present, refer generically to 'the CTA' without inventing text.\n"
        "6) Respect existing strengths: if the signals show something already present (e.g., visible pricing tiers), do not recommend adding the same thing; propose incremental improvements instead.\n"
        "7) Friction scoring: frictionScore is 1–10 (10 = highest). Use the content to justify intensity (e.g., bold guarantees → skepticism; pricing opacity → higher friction; long forms → hesitation).\n"
        "8) Priority: 1–10 (10 = most impactful). Sort items by descending priority.\n"
        "9) Timeline stages must map to real sections users see (Hero → next sections → Social Proof → How It Works → Pricing → FAQ/Guarantee → CTA → Confirmation if applicable). "
        "Populate 'section' with a helpful anchor (e.g., 'H1: … (Block #1)' or 'Pricing (Block #5)')."
    )

    # Compose compact, high-signal site context. Keep blocks ordered; they should each include fields like:
    # { index, type, heading, textSnippet, ctas, forms[{fields}] }
    signals: Dict[str, Any] = {
        "url": url,
        "goal": goal,
        "title": title,
        "textSample": text_sample[:2000],
        "contentBlocks": blocks[:20],  # preserve order for stage anchoring
    }
    if facts is not None:
        signals["siteFacts"] = facts
    if allowed_cta_labels:
        signals["allowedCtas"] = allowed_cta_labels

    user = (
        "Analyze these signals and produce a concise, high-signal CRO report. "
        "Focus on specific, plausible microbehaviors tied to what users will actually see in each section.\n\n"
        "Instructions:\n"
        "- First, produce items (6–12 total) capturing the most impactful microbehaviors and nudges, grounded in the signals.\n"
        "- Then, produce the timeline (8–10 stages). For each stage:\n"
        "  * Choose the real section from contentBlocks (preserve order) and write a 1–2 sentence 'observed' grounded in heading/snippet/CTAs/forms.\n"
        "  * Attach 1–5 relevant items for that stage (do not invent new ones; reuse items you produced).\n"
        "- Keep items atomic; avoid mixing two ideas in one.\n"
        "- Avoid duplicates across items and across stages.\n"
        "- CTA references must use exact labels from allowedCtas; otherwise say 'the CTA'.\n"
        "- Only suggest nudges that add value beyond what's already present.\n"
        "- Ensure frictionScore (1–10) is provided wherever meaningful.\n\n"
        f"Signals:\n{signals}"
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def build_journey_analysis_messages(
    *,
    url: str,
    text_sample: str,
    blocks: List[Dict[str, Any]],
    facts: Dict[str, Any] = None,
    allowed_cta_labels: List[str] = None,
    form_fields: List[str] = None,
) -> List[Dict[str, str]]:
    """
    Build grounded LLM messages for user journey analysis:
    - Inputs are structured site signals (hero/sections/ctas/forms/text) + facts and allowed CTA labels
    - Output must be STRICT JSON with keys for journey mapping and conversion funnel analysis
    """
    system = (
        "You are a User Experience and Conversion Funnel analyst. You will receive structured signals from a website "
        "and must map out the complete user journey from landing to conversion. "
        "Return ONLY strict JSON with keys: journey_steps (list), journey_insights (object). "
        "Do not include markdown, prose, or comments.\n\n"
        "IMPORTANT: Analyze the scraped content thoroughly and create meaningful journey steps based on what users would experience.\n\n"
        "Output contract:\n"
        "- journey_steps: Array of JourneyStep objects (AIM FOR 6-9 steps - create steps based on logical user flow)\n"
        "  * step_number: int (sequential numbering)\n"
        "  * step_name: str (descriptive name based on content found)\n"
        "  * description: str (detailed description using actual scraped content)\n"
        "  * content_elements: array of strings (content elements from scraped data)\n"
        "  * user_actions: array of strings (1-2 CRITICAL actions per step - focus on conversion-essential actions)\n"
        "  * conversion_indicators: array of strings (signs of progress found in content)\n"
        "  * friction_points: array of strings (actual obstacles found in content)\n"
        "  * optimization_suggestions: array of strings (specific improvements based on content gaps)\n"
        "- journey_insights: Object with fields:\n"
        "  * conversion_funnel_type: str (based on actual content analysis)\n"
        "  * primary_goal: str (inferred from actual CTAs and forms)\n"
        "  * journey_complexity: str ('Simple', 'Medium', 'Complex' based on actual steps)\n"
        "  * key_moments_of_truth: array of strings (critical decision points from content)\n"
        "  * optimization_priorities: array of strings (top areas to improve based on content)\n\n"
        "ANALYSIS GUIDELINES:\n"
        "1) Create journey steps based on logical user flow through the content\n"
        "2) Use actual text, headings, and content from the contentBlocks as reference\n"
        "3) Use EXACT CTA labels from allowedCtas when available\n"
        "4) Use EXACT form field names from formFields when available\n"
        "5) Each step should represent a logical progression in the user journey\n"
        "6) Include steps for: landing, content consumption, social proof, pricing, forms, conversion\n"
        "7) Base descriptions on actual content found, but be descriptive about user experience\n"
        "8) Create 6-9 meaningful steps that cover the complete user journey\n"
        "9) Focus on conversion-critical moments and user decision points\n"
        "10) Be thorough but realistic - don't force steps that don't make sense"
    )

    # Compose detailed site context for journey analysis
    signals: Dict[str, Any] = {
        "url": url,
        "textSample": text_sample[:4000],  # Increased text sample
        "contentBlocks": blocks[:30],  # Increased blocks for better context
    }
    if facts is not None:
        signals["siteFacts"] = facts
    if allowed_cta_labels:
        signals["allowedCtas"] = allowed_cta_labels
    if form_fields:
        signals["formFields"] = form_fields

    user = (
        "Create a realistic 6-8 step user journey using ONLY the actual scraped content provided:\n\n"
        "JOURNEY STRUCTURE:\n"
        "Phase 1 - Discovery (3-4 steps): What users do to understand the offer\n"
        "- Read specific headlines from contentBlocks (use exact heading text)\n"
    "- Click ONLY CTAs that exist in allowedCtas list\n" 
    "- Read specific content from contentBlocks (testimonials, descriptions, etc.)\n"
    "- Review pricing/plans ONLY if found in contentBlocks\n\n"
    "Phase 2 - Conversion (3-4 steps): The actual conversion process  \n"
    "- Click primary CTA from allowedCtas (use exact text)\n"
    "- Fill form fields from formFields (use exact field names)\n"
    "- Make selections based on scraped content\n"
    "- Complete confirmation steps\n\n"
    "CRITICAL RULES:\n"
    "- NO scrolling behaviors whatsoever\n"
    "- NO generic examples - ONLY use exact text from scraped signals\n" 
    "- NO invented sections or CTAs\n"
    "- If allowedCtas = ['Get Started', 'Contact Us'], ONLY use these exact texts\n"
    "- If formFields = ['email', 'company'], ONLY reference these exact fields\n"
    "- If contentBlocks don't contain testimonials, don't mention testimonials\n"
    "- Every behavior must map to actual scraped elements\n\n"
            f"Available CTAs: {allowed_cta_labels}\n" 
        f"Available Form Fields: {form_fields}\n"
        f"Signals:\n{signals}"
)

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def build_granular_actions_messages(
    *,
    url: str,
    goal: str | None,
    title: str | None,
    text_sample: str,
    blocks: List[Dict[str, Any]],
    facts: Dict[str, Any] | None = None,
    allowed_cta_labels: List[str] | None = None,
    form_fields: List[str] | None = None,
) -> List[Dict[str, str]]:
    """
    Build messages for granular step-by-step user action analysis.
    Focus on specific, actionable steps like "Click ad > Read headline > Fill form > Submit"
    """
    system = (
        "You are a conversion path analyst. Map the complete user journey from landing to goal achievement using ONLY actual scraped content. "
        "Return ONLY strict JSON with keys: action_sequence (array), interaction_details (object). "
        "CONVERSION SEQUENCE (6-8 critical steps):\n"
        "Goal: 'Book consultation call'\n"
        "1. 'Land on homepage'\n"
        "2. 'Read headline: [exact scraped headline]'\n"
        "3. 'Read testimonials section for trust'\n"
        "4. 'Click [exact CTA from allowedCtas] button'\n"
        "5. 'Fill [exact field from formFields] field'\n"
        "6. 'Select [specific option from scraped content]'\n"
        "7. 'Click [exact confirmation button] to submit'\n"
        "8. 'See success confirmation message'\n\n"
    
        "action_sequence: Array of ActionStep objects:\n"
        "- step_number: int (1-8)\n"
        "- action_type: str ('land', 'read', 'click', 'fill', 'select', 'submit', 'confirm')\n"
        "- action_description: str ('Read headline: [exact scraped text]')\n"
        "- content_target: str (exact element from scraped content)\n"
        "- friction_level: int (1-5, where 5 = highest friction)\n"
        "- success_indicators: array (signs step worked)\n"
        "- failure_points: array (what could go wrong)\n\n"
    
        "interaction_details: Object:\n"
        "- total_steps: int\n"
        "- critical_path_steps: array of step numbers (must complete for conversion)\n"
        "- optional_steps: array of step numbers (helpful but not required)\n"
        "- drop_off_risks: array of {step_number, risk_description}\n"
        "- optimization_sequence: array of improvement suggestions\n\n"
    
        "STRICT CONTENT RULES:\n"
        "1. ONLY use exact text from allowedCtas for CTAs\n"
        "2. ONLY use exact names from formFields for form interactions\n" 
        "3. ONLY reference headings/content that exist in contentBlocks\n"
        "4. NO scrolling, hovering, or navigation behaviors\n"
        "5. NO invented sections, buttons, or content\n"
        "- Each step = one specific user action\n"
        "- Must end with complete goal achievement\n"
        "- Focus on conversion-essential actions only"
    )

    # Compose detailed context for granular analysis
    signals: Dict[str, Any] = {
        "url": url,
        "goal": goal,
        "title": title,
        "textSample": text_sample[:3000],
        "contentBlocks": blocks[:25],
    }
    if facts is not None:
        signals["siteFacts"] = facts
    if allowed_cta_labels:
        signals["allowedCtas"] = allowed_cta_labels
    if form_fields:
        signals["formFields"] = form_fields

    user = (
        "Create a granular step-by-step user action sequence based on the actual scraped content. "
        "Think like a real user moving through the site from landing to conversion.\n\n"
        "REALISTIC USER JOURNEY TO GOAL ANALYSIS:\n"
        "Map the COMPLETE realistic path from landing to goal achievement based on the actual scraped content:\n"
        "1. Page entry and first glance (what catches attention)\n"
        "2. Initial content scanning (headlines, images, key points)\n"
        "3. Scrolling and exploration (different sections, reading more)\n"
        "4. Value discovery and interest building (understanding the offer)\n"
        "5. Trust building (testimonials, guarantees, social proof)\n"
        "6. Decision moment and primary CTA interaction\n"
        "7. Post-CTA conversion flow (forms, selections, confirmations)\n"
        "8. Goal completion process (booking details, payment, scheduling)\n"
        "9. Final confirmation and success state\n\n"
        "CONVERSION PATH REQUIREMENTS:\n"
        "- Trace the user's journey from landing to goal achievement\n"
        "- Include ALL steps needed to complete the conversion\n"
        "- Show realistic form interactions (name, email, phone, preferences)\n"
        "- Include selection steps (time slots, options, packages)\n"
        "- Show confirmation and next steps\n"
        "- Focus on the primary conversion flow, not secondary exploration\n\n"
        "REALISTIC CONVERSION PATH EXAMPLES:\n"
        "Goal: 'Book a consultation call'\n"
        "Path: 'Land on homepage' → 'First glance at hero section' → 'Read main headline' → 'Scroll down to view services' → 'Read service descriptions' → 'Scroll to testimonials section' → 'Read 2-3 client reviews' → 'Check pricing section' → 'Scroll back up' → 'Click \"Book Free Call\" CTA' → 'Fill name field' → 'Fill email field' → 'Fill phone field' → 'Select time slot' → 'Click \"Confirm Booking\"' → 'See confirmation message'\n\n"
        "Goal: 'Purchase product'\n"
        "Path: 'View product page' → 'Look at product images' → 'Read product title' → 'Scroll to features section' → 'Read feature list' → 'Scroll to reviews' → 'Read customer reviews' → 'Check FAQ section' → 'Scroll to pricing' → 'Compare pricing options' → 'Click \"Buy Now\"' → 'Select package' → 'Fill billing details' → 'Enter payment info' → 'Click \"Complete Purchase\"' → 'Get order confirmation'\n\n"
        "Goal: 'Download resource'\n"
        "Path: 'Land on blog post' → 'Read article intro' → 'Scroll through article' → 'Read section headers' → 'View resource preview image' → 'Read resource description' → 'Scroll to CTA section' → 'Click \"Download Free Guide\"' → 'Fill name field' → 'Fill work email' → 'Select company size' → 'Click \"Get Download Link\"' → 'Check email for link'\n\n"
        "BROWSING AND CONVERSION BEHAVIOR FOCUS:\n"
        "- Include initial viewing and first impressions\n"
        "- Map scrolling patterns (down, up, back and forth)\n"
        "- Show content scanning behaviors (headlines, bullets, images)\n"
        "- Include section exploration (services, testimonials, pricing, FAQ)\n"
        "- Add trust-building moments (reading reviews, checking guarantees)\n"
        "- Include decision-making pauses and consideration points\n"
        "- Show validation seeking (looking for proof, credentials)\n"
        "- Map the CTA decision moment and click\n"
        "- Detail complete form filling and selection process\n"
        "- End with goal achievement confirmation\n"
        "- Include mobile-specific actions (tap, swipe, zoom)\n\n"
        "Remember: Every action must be tied to actual content found in the scraped data. "
        "Use exact text, exact button labels, exact field names.\n\n"
        f"Signals:\n{signals}"
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]