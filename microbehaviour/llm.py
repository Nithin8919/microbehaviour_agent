from __future__ import annotations

import json
import os
import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI

# Set up logging
logger = logging.getLogger(__name__)


def analyze_page_text(
    source_url: str,
    page_text: str,
    *,
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    messages: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Send cleaned text to the LLM and return a structured JSON result."""
    logger.info(f"=== LLM ANALYSIS START ===")
    logger.info(f"Source URL: {source_url}")
    logger.info(f"Page text length: {len(page_text)} characters")
    logger.info(f"Model: {model}")
    
    resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
    logger.info(f"API Key status: {'SET' if resolved_api_key else 'NOT SET'}")
    
    if not resolved_api_key:
        logger.error("✗ OPENAI_API_KEY not set!")
        raise RuntimeError("OPENAI_API_KEY not set. Set env var or pass api_key.")

    logger.info(f"API Key length: {len(resolved_api_key)}")
    logger.info(f"API Key preview: {resolved_api_key[:10]}...")

    try:
        client = OpenAI(api_key=resolved_api_key)
        logger.info("✓ OpenAI client created successfully")
    except Exception as e:
        logger.error(f"✗ Failed to create OpenAI client: {e}")
        raise

    if messages is None:
        logger.info("Building default analysis messages...")
        from .prompts import build_analysis_messages
        messages = build_analysis_messages(source_url, page_text)

    logger.info(f"Total messages to send: {len(messages)}")
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown")
        content_len = len(msg.get("content", ""))
        logger.info(f"  Message {i+1}: {role} ({content_len} chars)")

    try:
        logger.info("Sending request to OpenAI API...")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        logger.info("✓ Received response from OpenAI API")
        
        # Log response metadata
        if hasattr(response, 'usage'):
            logger.info(f"Token usage: {response.usage}")
        
        content = response.choices[0].message.content or "{}"
        logger.info(f"Response content length: {len(content)} characters")
        logger.info(f"Response preview: {content[:200]}...")
        
        try:
            parsed_data = json.loads(content)
            logger.info(f"✓ Successfully parsed JSON response")
            logger.info(f"Response keys: {list(parsed_data.keys()) if isinstance(parsed_data, dict) else 'Not a dict'}")
            return parsed_data
        except json.JSONDecodeError as e:
            logger.error(f"✗ Failed to parse JSON response: {e}")
            logger.error(f"Raw content: {content}")
            return {"raw": content}
            
    except Exception as e:
        logger.error(f"✗ OpenAI API call failed: {e}", exc_info=True)
        raise


