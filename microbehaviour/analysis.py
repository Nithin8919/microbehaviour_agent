from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .crawler import crawl_same_host
from .scraper import fetch_html_static
from .cleaner import html_to_text, truncate_text
from .sections import extract_content_blocks
from .prompts import build_analysis_messages_from_signals, build_journey_analysis_messages, build_granular_actions_messages
from .llm import analyze_page_text
from .normalize import extract_json_maybe, normalize_items, backfill_timeline
from .schemas import ExperienceReport, TimelineStage, UserJourneyReport, JourneyStep, GranularActionReport, ActionStep, InteractionDetails, DropOffRisk
from .signals import compute_site_facts, derive_supporting_signals

# Set up logging
logger = logging.getLogger(__name__)


def analyze_experience(url: str, goal: Optional[str] = None, max_pages: int = 3, max_depth: int = 1) -> ExperienceReport:
    # Crawl small set of same-host pages
    pages = crawl_same_host(url, max_pages=max_pages, max_depth=max_depth)

    all_blocks: List[Dict[str, Any]] = []
    text_corpus: List[str] = []
    title: Optional[str] = None

    raw_html_pages: list[str] = []
    for p in pages:
        html = fetch_html_static(p)
        raw_html_pages.append(html)
        text = html_to_text(html)
        text_corpus.append(text)
        if title is None:
            # crude title extraction
            try:
                import re

                m = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
                if m:
                    title = m.group(1).strip()
            except Exception:
                pass
        blocks = [b.to_dict() for b in extract_content_blocks(html)]
        # attach page hint to heading if empty
        for b in blocks:
            if not b.get("heading"):
                b["heading"] = f"Block from {p}"
        all_blocks.extend(blocks)

    text_sample = truncate_text("\n\n".join(t[:4000] for t in text_corpus))
    facts = compute_site_facts("\n".join(text_corpus), all_blocks)
    support = derive_supporting_signals(raw_html_pages, all_blocks)

    # Collect allowed CTA labels from blocks to constrain phrasing
    allowed_ctas: list[str] = []
    for b in all_blocks:
        for label in b.get("local_ctas", []) or []:
            if label and label not in allowed_ctas:
                allowed_ctas.append(label)

    messages = build_analysis_messages_from_signals(
        url=url,
        goal=goal,
        title=title,
        text_sample=text_sample,
        blocks=all_blocks,
        facts={**facts, **support},
        allowed_cta_labels=allowed_ctas,
    )

    # Call LLM
    raw = analyze_page_text(url, text_sample, messages=messages)
    data = extract_json_maybe(str(raw)) if isinstance(raw, (str,)) else raw

    items_raw = data.get("items") or data.get("hypothesized_microbehaviors") or []
    items = normalize_items(items_raw, allowed_ctas)

    timeline_raw = data.get("timeline") or []
    timeline: List[TimelineStage] = []
    for idx, st in enumerate(timeline_raw, start=1):
        t_items = normalize_items(st.get("items", []), allowed_ctas)
        timeline.append(
            TimelineStage(
                index=idx,
                stage=str(st.get("stage") or f"Stage {idx}"),
                section=st.get("section"),
                observed=st.get("observed"),
                items=t_items,
            )
        )

    timeline = backfill_timeline(timeline)

    return ExperienceReport(url=url, goal=goal, items=items, timeline=timeline)


def analyze_user_journey(url: str, max_pages: int = 3, max_depth: int = 1) -> UserJourneyReport:
    """
    Analyze user journey from a website URL.
    
    This function:
    1. Crawls the website to gather pages
    2. Extracts content blocks from each page
    3. Analyzes the content to identify user journey steps
    4. Generates microbehaviors for each step
    5. Returns a comprehensive UserJourneyReport
    
    The journey follows a 9-step conversion funnel pattern:
    1. Landing via ad/social/referral
    2. Reading main headline + subheadline
    3. Glancing at credibility elements
    4. Understanding the process framework
    5. Reviewing social proof
    6. Checking pricing and features
    7. Clicking CTA buttons
    8. Filling booking forms
    9. Confirming calendar slots
    """
    logger.info(f"=== STARTING USER JOURNEY ANALYSIS ===")
    logger.info(f"URL: {url}")
    logger.info(f"Max pages: {max_pages}, Max depth: {max_depth}")
    
    # Check environment
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    logger.info(f"OpenAI API Key status: {'SET' if api_key else 'NOT SET'}")
    if api_key:
        logger.info(f"API Key length: {len(api_key)}")
        logger.info(f"API Key starts with: {api_key[:10]}...")
    
    # Crawl pages to gather content
    logger.info(f"Step 1: Crawling pages from {url}")
    try:
        pages = crawl_same_host(url, max_pages=max_pages, max_depth=max_depth)
        logger.info(f"✓ Successfully crawled {len(pages)} pages: {pages}")
    except Exception as e:
        logger.error(f"✗ Failed to crawl pages: {e}")
        raise
    
    all_blocks: List[Dict[str, Any]] = []
    text_corpus: List[str] = []
    raw_html_pages: list[str] = []
    
    logger.info(f"Step 2: Processing {len(pages)} pages for content extraction")
    for i, p in enumerate(pages, 1):
        logger.info(f"Processing page {i}/{len(pages)}: {p}")
        try:
            logger.info(f"  - Fetching HTML from {p}")
            html = fetch_html_static(p)
            logger.info(f"  ✓ Fetched {len(html)} characters of HTML")
            
            # Check if this is a JavaScript-heavy site that needs dynamic rendering
            from .scraper import needs_javascript_rendering, fetch_html_dynamic
            if needs_javascript_rendering(html):
                logger.info(f"  🔄 Site needs JavaScript rendering, switching to dynamic scraping...")
                try:
                    dynamic_result = fetch_html_dynamic(p, timeout_seconds=15)
                    html = dynamic_result.html
                    logger.info(f"  ✓ Dynamic HTML fetched: {len(html)} characters")
                except Exception as dynamic_error:
                    logger.warning(f"  ⚠️ Dynamic scraping failed, using static: {dynamic_error}")
            
            raw_html_pages.append(html)
            
            logger.info(f"  - Converting HTML to text")
            text = html_to_text(html)
            logger.info(f"  ✓ Extracted {len(text)} characters of text")
            text_corpus.append(text)
            
            logger.info(f"  - Extracting content blocks")
            blocks = [b.to_dict() for b in extract_content_blocks(html)]
            logger.info(f"  ✓ Extracted {len(blocks)} content blocks from {p}")
            
            # Log detailed block analysis for debugging
            if blocks:
                logger.info(f"  📊 Block analysis for {p}:")
                for j, b in enumerate(blocks[:5]):  # Log first 5 blocks
                    heading = b.get('heading', 'No heading')[:50]
                    snippet = b.get('snippet', '')[:100]
                    ctas = b.get('local_ctas', [])
                    forms = b.get('local_forms', [])
                    logger.info(f"    Block {j+1}: '{heading}' | {b.get('text_words', 0)} words | {len(ctas)} CTAs | {len(forms)} forms")
                    logger.info(f"      Snippet: {snippet}...")
                    if ctas:
                        logger.info(f"      CTAs: {ctas}")
                    if forms:
                        logger.info(f"      Forms: {forms}")
            else:
                logger.warning(f"  ⚠️ No content blocks extracted from {p}")
            
            # attach page hint to heading if empty
            for b in blocks:
                if not b.get("heading"):
                    b["heading"] = f"Block from {p}"
            all_blocks.extend(blocks)
            
        except Exception as e:
            logger.error(f"  ✗ Failed to process page {p}: {e}", exc_info=True)
            # Add a minimal block to prevent complete failure
            error_block = {
                "heading": f"Error processing {p}",
                "text_words": 0,
                "local_ctas": [],
                "local_forms": [],
                "text_snippet": f"Failed to load: {str(e)}"
            }
            all_blocks.append(error_block)
            text_corpus.append(f"Error loading page: {str(e)}")
            raw_html_pages.append("")
    
    logger.info(f"✓ Total content blocks extracted: {len(all_blocks)}")
    
    if not all_blocks:
        logger.error("✗ No content blocks were extracted from any pages!")
        # Create a minimal fallback report
        return UserJourneyReport(
            url=url,
            journey_steps=[],
            total_steps=0,
            conversion_funnel_type="Error - No Content",
            primary_goal="Unknown - No Content Found",
            journey_complexity="Error",
            key_moments_of_truth=["No content could be extracted"],
            optimization_priorities=["Fix content extraction system"]
        )
    
    logger.info(f"Step 3: Processing text and generating site signals")
    text_sample = truncate_text("\n\n".join(t[:4000] for t in text_corpus))
    logger.info(f"  ✓ Created text sample: {len(text_sample)} characters")
    
    logger.info(f"  - Computing site facts")
    facts = compute_site_facts("\n".join(text_corpus), all_blocks)
    logger.info(f"  ✓ Computed {len(facts)} site facts: {list(facts.keys())}")
    
    logger.info(f"  - Deriving supporting signals")
    support = derive_supporting_signals(raw_html_pages, all_blocks)
    logger.info(f"  ✓ Derived {len(support)} supporting signals: {list(support.keys())}")
    
    # Collect CTA labels and form fields for journey analysis
    logger.info(f"Step 4: Extracting CTAs and form fields")
    allowed_ctas: list[str] = []
    form_fields: list[str] = []
    for b in all_blocks:
        for label in b.get("local_ctas", []) or []:
            if label and label not in allowed_ctas:
                allowed_ctas.append(label)
        for form in b.get("local_forms", []) or []:
            fields_str = form.get("fields", "")
            if fields_str:
                fields = [f.strip() for f in fields_str.split(",")]
                for field in fields:
                    if field and field not in form_fields:
                        form_fields.append(field)
    
    logger.info(f"  ✓ Found {len(allowed_ctas)} CTAs: {allowed_ctas}")
    logger.info(f"  ✓ Found {len(form_fields)} form fields: {form_fields}")
    
    # Build journey analysis messages
    logger.info(f"Step 5: Building LLM analysis messages")
    try:
        messages = build_journey_analysis_messages(
            url=url,
            text_sample=text_sample,
            blocks=all_blocks,
            facts={**facts, **support},
            allowed_cta_labels=allowed_ctas,
            form_fields=form_fields
        )
        logger.info(f"  ✓ Built {len(messages)} messages for LLM")
        logger.info(f"  📝 Messages overview:")
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content_len = len(msg.get("content", ""))
            logger.info(f"    Message {i+1}: {role} ({content_len} chars)")
    except Exception as e:
        logger.error(f"  ✗ Failed to build LLM messages: {e}", exc_info=True)
        raise
    
    logger.info(f"Step 6: Sending analysis request to LLM...")
    
    # Call LLM for journey analysis
    try:
        logger.info(f"  - Calling analyze_page_text with {len(text_sample)} chars of text")
        raw = analyze_page_text(url, text_sample, messages=messages)
        logger.info(f"  ✓ LLM returned response: {type(raw)}")
        logger.info(f"  📄 Raw response preview: {str(raw)[:200]}...")
        
        data = extract_json_maybe(str(raw)) if isinstance(raw, (str,)) else raw
        logger.info(f"  ✓ Parsed JSON data: {type(data)}")
        if isinstance(data, dict):
            logger.info(f"  📊 Data keys: {list(data.keys())}")
        else:
            logger.warning(f"  ⚠️ Data is not a dict: {data}")
            
    except Exception as e:
        logger.error(f"  ✗ LLM analysis failed: {e}", exc_info=True)
        # Provide minimal fallback data
        data = {
            "journey_steps": [],
            "journey_insights": {
                "conversion_funnel_type": "Error",
                "primary_goal": "Unknown",
                "journey_complexity": "Unknown",
                "key_moments_of_truth": [],
                "optimization_priorities": ["Fix analysis system"]
            }
        }
        logger.info(f"  🔄 Using fallback data structure")
    
    logger.info(f"Step 7: Processing LLM response")
    
    # Parse journey steps
    journey_steps_raw = data.get("journey_steps") or []
    logger.info(f"  📈 Parsed {len(journey_steps_raw)} raw journey steps from LLM")
    
    if not journey_steps_raw:
        logger.warning(f"  ⚠️ No journey steps found in LLM response!")
        logger.info(f"  🔍 Full LLM response data: {data}")
    else:
        logger.info(f"  ✓ Found journey steps in LLM response")
        for i, step in enumerate(journey_steps_raw[:3]):  # Log first 3 steps
            step_name = step.get('step_name', 'No name')
            step_desc = step.get('description', 'No description')[:100]
            logger.info(f"    Step {i+1}: '{step_name}' - {step_desc}...")
    
    logger.info(f"Step 8: Creating comprehensive microbehaviors (targeting 8-10 behaviors)")
    journey_steps: List[JourneyStep] = []
    
    # Extract comprehensive microbehaviors to maximize the 10-step limit
    all_behaviors = []
    
    # First, get the most important CTAs and actions from the actual scraped content
    top_ctas = [cta for cta in allowed_ctas[:5] if cta not in ['Help Center', 'Contact Us', 'Privacy Policy', 'Terms of Service']]
    logger.info(f"  Top CTAs from scraped content: {top_ctas}")
    
    # Process each journey step to extract specific behaviors
    for idx, step_data in enumerate(journey_steps_raw, start=1):
        step_name = step_data.get('step_name', f'Step {idx}')
        logger.info(f"  Processing step {idx}: '{step_name}'")
        
        user_actions = step_data.get("user_actions", [])
        content_elements = step_data.get("content_elements", [])
        conversion_indicators = step_data.get("conversion_indicators", [])
        
        # Add specific user actions (prioritize these)
        for action in user_actions:
            all_behaviors.append({
                "behavior": action,
                "step_context": step_name,
                "friction_score": 3,
                "priority": 9
            })
        
        # Add content reading behaviors for important elements
        for element in content_elements[:1]:  # Take the main content element
            if element and len(element) > 5:  # Skip very short elements
                all_behaviors.append({
                    "behavior": f"Read '{element[:60]}{'...' if len(element) > 60 else ''}'",
                    "step_context": step_name,
                    "friction_score": 2,
                    "priority": 7
                })
        
        # Add conversion-focused behaviors
        for indicator in conversion_indicators[:1]:
            if indicator and "click" not in indicator.lower():
                all_behaviors.append({
                    "behavior": indicator,
                    "step_context": step_name,
                    "friction_score": 4,
                    "priority": 8
                })
    
    # Add specific CTA-based behaviors if we have room (targeting 10 total)
    cta_behaviors_added = 0
    for cta in top_ctas:
        if len(all_behaviors) < 9 and cta_behaviors_added < 3:  # Leave room and don't overdo CTAs
            # Make CTA behavior more specific
            if 'start' in cta.lower() or 'get started' in cta.lower():
                behavior_text = f"Click '{cta}' to begin onboarding"
            elif 'how it works' in cta.lower():
                behavior_text = f"Click '{cta}' to understand the process"
            elif 'pricing' in cta.lower():
                behavior_text = f"Check '{cta}' to see pricing options"
            else:
                behavior_text = f"Click '{cta}'"
                
            all_behaviors.append({
                "behavior": behavior_text,
                "step_context": "CTA Interaction",
                "friction_score": 3,
                "priority": 8
            })
            cta_behaviors_added += 1
    
    # Add essential behaviors if we don't have enough (aim for 8-10 total)
    essential_behaviors = [
        {"behavior": "Land on website homepage", "step_context": "Initial Visit", "friction_score": 1, "priority": 10},
        {"behavior": "Scroll down to explore content", "step_context": "Content Discovery", "friction_score": 2, "priority": 9},
        {"behavior": "Read main value proposition", "step_context": "Value Assessment", "friction_score": 2, "priority": 9}
    ]
    
    # Add essential behaviors if we're short
    existing_behaviors_text = [b['behavior'].lower() for b in all_behaviors]
    for essential in essential_behaviors:
        if len(all_behaviors) < 8:  # Only add if we need more
            # Check if we already have something similar (simple check)
            essential_words = essential['behavior'].lower().split()[:2]  # First 2 words
            already_exists = any(word in existing for existing in existing_behaviors_text for word in essential_words)
            if not already_exists:
                all_behaviors.append(essential)
    
    # Sort by priority (highest first) and limit to 10 behaviors maximum
    all_behaviors.sort(key=lambda x: x['priority'], reverse=True)
    key_behaviors = all_behaviors[:10]
    
    # Ensure we have meaningful diversity - remove duplicates
    seen_behaviors = set()
    final_behaviors = []
    for behavior in key_behaviors:
        behavior_key = behavior['behavior'].lower()[:20]  # First 20 chars as key
        if behavior_key not in seen_behaviors:
            seen_behaviors.add(behavior_key)
            final_behaviors.append(behavior)
    
    key_behaviors = final_behaviors
    logger.info(f"  Generated {len(key_behaviors)} comprehensive microbehaviors")
    
    # Create a single journey step with all key microbehaviors
    if key_behaviors:
        step = JourneyStep(
            step_number=1,
            step_name="Complete User Journey",
            description="Key microbehaviors extracted from the website content",
            content_elements=[],
            user_actions=[],
            conversion_indicators=[],
            friction_points=[],
            optimization_suggestions=[],
            microbehaviors=key_behaviors
        )
        journey_steps.append(step)
        total_microbehaviors = len(key_behaviors)
        logger.info(f"    ✓ Generated {len(key_behaviors)} focused microbehaviors")
    else:
        # Fallback if no behaviors found
        step = JourneyStep(
            step_number=1,
            step_name="Basic User Journey",
            description="Default user behaviors",
            content_elements=[],
            user_actions=[],
            conversion_indicators=[],
            friction_points=[],
            optimization_suggestions=[],
            microbehaviors=[{
                "behavior": "Visit website",
                "step_context": "Landing",
                "friction_score": 2,
                "priority": 8
            }]
        )
        journey_steps.append(step)
        total_microbehaviors = 1
    
    # Extract overall journey insights
    logger.info(f"Step 9: Extracting journey insights")
    journey_insights = data.get("journey_insights", {})
    logger.info(f"  Journey insights keys: {list(journey_insights.keys())}")
    
    logger.info(f"=== ANALYSIS COMPLETED ===")
    logger.info(f"✓ Created {len(journey_steps)} journey steps")
    logger.info(f"✓ Generated {total_microbehaviors} total microbehaviors")
    logger.info(f"✓ Conversion funnel type: {journey_insights.get('conversion_funnel_type', 'Standard')}")
    logger.info(f"✓ Primary goal: {journey_insights.get('primary_goal', 'Conversion')}")
    
    final_report = UserJourneyReport(
        url=url,
        journey_steps=journey_steps,
        total_steps=len(journey_steps),
        conversion_funnel_type=journey_insights.get("conversion_funnel_type", "Standard"),
        primary_goal=journey_insights.get("primary_goal", "Conversion"),
        journey_complexity=journey_insights.get("journey_complexity", "Medium"),
        key_moments_of_truth=journey_insights.get("key_moments_of_truth", []),
        optimization_priorities=journey_insights.get("optimization_priorities", [])
    )
    
    logger.info(f"🎉 Report generated successfully with {final_report.total_steps} steps and {total_microbehaviors} microbehaviors")
    return final_report


def analyze_granular_actions(url: str, goal: Optional[str] = None, max_pages: int = 3, max_depth: int = 1) -> GranularActionReport:
    """
    Analyze user micro-interactions and generate granular step-by-step action sequence.
    Focus on specific actions like "Click ad > Read headline > Fill form > Submit"
    """
    logger.info(f"🔍 Starting granular action analysis for {url}")
    
    # Import API key validation
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    if api_key and len(api_key) > 10:
        logger.info(f"API Key length: {len(api_key)}")
        logger.info(f"API Key starts with: {api_key[:10]}...")
    
    # Crawl pages to gather content
    logger.info(f"Step 1: Crawling pages from {url}")
    try:
        pages = crawl_same_host(url, max_pages=max_pages, max_depth=max_depth)
        logger.info(f"✓ Successfully crawled {len(pages)} pages: {pages}")
    except Exception as e:
        logger.error(f"✗ Failed to crawl pages: {e}")
        raise
    
    all_blocks: List[Dict[str, Any]] = []
    text_corpus: List[str] = []
    title: Optional[str] = None
    
    raw_html_pages: list[str] = []
    for p in pages:
        html = fetch_html_static(p)
        raw_html_pages.append(html)
        
        text = html_to_text(html)
        text_corpus.append(text)
        
        blocks = extract_content_blocks(html)
        if blocks and not title:
            title = next((b.get('title') for b in blocks if b.get('title')), None)
        
        for block in blocks:
            block['source_url'] = p
        all_blocks.extend(blocks)
    
    logger.info(f"✓ Extracted {len(all_blocks)} content blocks from {len(pages)} pages")
    
    # Derive supporting signals
    facts = compute_site_facts(raw_html_pages)
    allowed_cta_labels, form_fields = derive_supporting_signals(all_blocks, goal)
    
    logger.info(f"✓ Found {len(allowed_cta_labels)} CTAs and {len(form_fields)} form fields")
    
    # Build text sample
    text_sample = truncate_text(" ".join(text_corpus), max_words=1500)
    
    # Generate granular action analysis using LLM
    logger.info("Step 2: Generating granular action sequence")
    try:
        messages = build_granular_actions_messages(
            url=url,
            goal=goal,
            title=title,
            text_sample=text_sample,
            blocks=all_blocks,
            facts=facts,
            allowed_cta_labels=allowed_cta_labels,
            form_fields=form_fields
        )
        
        raw_response = analyze_page_text(messages)
        logger.info(f"✓ Raw LLM response length: {len(raw_response)} characters")
        
        # Extract JSON response
        parsed_response = extract_json_maybe(raw_response)
        logger.info(f"✓ Parsed response keys: {list(parsed_response.keys()) if isinstance(parsed_response, dict) else type(parsed_response)}")
        
    except Exception as e:
        logger.error(f"✗ Failed to generate granular analysis: {e}")
        raise
    
    # Build action sequence
    action_sequence: List[ActionStep] = []
    interaction_details = InteractionDetails(total_steps=0)
    
    if isinstance(parsed_response, dict):
        # Process action sequence
        if "action_sequence" in parsed_response:
            raw_actions = parsed_response["action_sequence"]
            logger.info(f"Processing {len(raw_actions)} action steps")
            
            for i, action_data in enumerate(raw_actions, 1):
                try:
                    action_step = ActionStep(
                        step_number=action_data.get("step_number", i),
                        action_type=action_data.get("action_type", "view"),
                        action_description=action_data.get("action_description", ""),
                        content_target=action_data.get("content_target", ""),
                        friction_level=action_data.get("friction_level", 1),
                        success_indicators=action_data.get("success_indicators", []),
                        failure_points=action_data.get("failure_points", [])
                    )
                    action_sequence.append(action_step)
                except Exception as e:
                    logger.warning(f"Failed to process action step {i}: {e}")
                    continue
        
        # Process interaction details
        if "interaction_details" in parsed_response:
            details_data = parsed_response["interaction_details"]
            try:
                drop_off_risks = []
                for risk_data in details_data.get("drop_off_risks", []):
                    if isinstance(risk_data, dict):
                        drop_off_risk = DropOffRisk(
                            step_number=risk_data.get("step_number", 1),
                            risk_description=risk_data.get("risk_description", "")
                        )
                        drop_off_risks.append(drop_off_risk)
                
                interaction_details = InteractionDetails(
                    total_steps=details_data.get("total_steps", len(action_sequence)),
                    critical_path_steps=details_data.get("critical_path_steps", []),
                    optional_steps=details_data.get("optional_steps", []),
                    drop_off_risks=drop_off_risks,
                    optimization_sequence=details_data.get("optimization_sequence", [])
                )
            except Exception as e:
                logger.warning(f"Failed to process interaction details: {e}")
    
    # Create final report
    final_report = GranularActionReport(
        url=url,
        goal=goal,
        action_sequence=action_sequence,
        interaction_details=interaction_details
    )
    
    logger.info(f"🎉 Granular action analysis completed with {len(action_sequence)} steps")
    return final_report
