from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse

import requests


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# JavaScript to inject for capturing user interaction signals
INTERACTION_SCRIPT = """
window.microbehaviourData = {
    clicks: [],
    scrolls: [],
    hovers: [],
    inputs: [],
    rageClicks: []
};

// Click tracking with position and timing
document.addEventListener('click', function(e) {
    const clickData = {
        timestamp: Date.now(),
        x: e.pageX,
        y: e.pageY,
        target: e.target.tagName,
        targetClass: e.target.className,
        targetId: e.target.id,
        text: e.target.textContent?.slice(0, 100)
    };
    
    window.microbehaviourData.clicks.push(clickData);
    
    // Detect rage clicks (multiple rapid clicks in same area)
    const recentClicks = window.microbehaviourData.clicks.filter(
        c => Date.now() - c.timestamp < 2000 && 
        Math.abs(c.x - e.pageX) < 50 && 
        Math.abs(c.y - e.pageY) < 50
    );
    
    if (recentClicks.length > 3) {
        window.microbehaviourData.rageClicks.push({
            timestamp: Date.now(),
            x: e.pageX,
            y: e.pageY,
            count: recentClicks.length
        });
    }
});

// Scroll depth tracking
let maxScrollDepth = 0;
document.addEventListener('scroll', function() {
    const scrollTop = window.pageYOffset;
    const docHeight = document.documentElement.scrollHeight;
    const winHeight = window.innerHeight;
    const scrollPercent = (scrollTop / (docHeight - winHeight)) * 100;
    
    if (scrollPercent > maxScrollDepth) {
        maxScrollDepth = scrollPercent;
        window.microbehaviourData.scrolls.push({
            timestamp: Date.now(),
            depth: scrollPercent,
            position: scrollTop
        });
    }
});

// Hover tracking with dwell time
let hoverStartTime = {};
document.addEventListener('mouseenter', function(e) {
    hoverStartTime[e.target] = Date.now();
});

document.addEventListener('mouseleave', function(e) {
    if (hoverStartTime[e.target]) {
        const dwellTime = Date.now() - hoverStartTime[e.target];
        if (dwellTime > 500) { // Only track meaningful hovers
            window.microbehaviourData.hovers.push({
                timestamp: Date.now(),
                target: e.target.tagName,
                targetClass: e.target.className,
                dwellTime: dwellTime
            });
        }
        delete hoverStartTime[e.target];
    }
});

// Input focus/blur tracking
document.addEventListener('focus', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        window.microbehaviourData.inputs.push({
            timestamp: Date.now(),
            action: 'focus',
            target: e.target.tagName,
            targetType: e.target.type,
            targetClass: e.target.className
        });
    }
});

document.addEventListener('blur', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        window.microbehaviourData.inputs.push({
            timestamp: Date.now(),
            action: 'blur',
            target: e.target.tagName,
            targetType: e.target.type,
            targetClass: e.target.className,
            value: e.target.value?.slice(0, 100)
        });
    }
});

// Wait for page to be fully loaded
window.addEventListener('load', function() {
    // Small delay to capture any late-loading interactions
    setTimeout(() => {
        console.log('Microbehaviour data captured:', window.microbehaviourData);
    }, 1000);
});
"""


@dataclass
class ScrapingResult:
    """Result of scraping a webpage with enhanced behavioral data."""
    url: str
    html: str
    screenshot_path: Optional[str] = None
    dom_snapshot: Optional[str] = None
    interaction_data: Optional[Dict[str, Any]] = None
    content_type: str = "text/html"
    response_time_ms: Optional[float] = None
    needs_js: bool = False


def needs_javascript_rendering(html: str) -> bool:
    """Heuristic to detect if a page needs JavaScript rendering."""
    # Check for suspiciously small HTML
    if len(html) < 5000:
        return True
    
    # Check for empty body or minimal content
    if "<body></body>" in html or "<body><div></div></body>" in html:
        return True
    
    # Check for heavy JavaScript presence with minimal HTML content
    script_count = html.count("<script")
    div_count = html.count("<div")
    if script_count > 0 and div_count < 5:
        return True
    
    # Check for common SPA indicators
    spa_indicators = ["ng-app", "data-reactroot", "id=\"root\"", "id=\"app\""]
    if any(indicator in html for indicator in spa_indicators):
        return True
    
    return False


def fetch_html_static(url: str, timeout_seconds: int = 20, max_retries: int = 2) -> str:
    """Fetch raw HTML via HTTP GET using `requests`.

    Performs light retry on transient failures and sets a desktop UA.
    """
    if not re.match(r"^https?://", url):
        raise ValueError("URL must start with http:// or https://")

    backoff_seconds = 1.0
    last_error: Optional[Exception] = None
    start_time = time.time()
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout_seconds)
            response.raise_for_status()
            
            # Heuristic: only accept HTML-ish content types
            content_type = response.headers.get("Content-Type", "").lower()
            if "html" not in content_type and "xml" not in content_type:
                # Still return body; caller may decide how to handle
                return response.text
            return response.text
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt >= max_retries:
                break
            time.sleep(backoff_seconds)
            backoff_seconds *= 2

    raise RuntimeError(f"Failed to fetch URL after retries: {url}\nLast error: {last_error}")


def fetch_html_dynamic(
    url: str, 
    timeout_seconds: int = 30,
    capture_screenshot: bool = True,
    screenshot_dir: Optional[str] = None
) -> ScrapingResult:
    """Fetch HTML with a headless browser for JS-heavy pages with behavioral tracking.

    This uses Playwright if available. If not installed, instructs how to add it.
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "Playwright not installed. Install with: pip install playwright && playwright install"
        ) from exc
    
    # No signal handling - rely on Playwright's built-in timeouts

    # Setup screenshot directory
    if screenshot_dir:
        screenshot_path = Path(screenshot_dir)
        screenshot_path.mkdir(parents=True, exist_ok=True)
    else:
        screenshot_path = Path("screenshots")
        screenshot_path.mkdir(exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding"
            ]
        )
        
        try:
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=DEFAULT_HEADERS["User-Agent"],
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            page = context.new_page()
            page.set_extra_http_headers(DEFAULT_HEADERS)
            
            # Inject interaction tracking script
            page.add_init_script(INTERACTION_SCRIPT)
            
            # Navigate to page with more reasonable timeout
            try:
                page.goto(url, timeout=timeout_seconds * 1000, wait_until="domcontentloaded")
            except Exception as e:
                # If domcontentloaded fails, try with load event
                try:
                    page.goto(url, timeout=timeout_seconds * 1000, wait_until="load")
                except Exception as e2:
                    # If all else fails, just wait for basic navigation
                    page.goto(url, timeout=timeout_seconds * 1000)
            
            # Wait a bit more for any delayed interactions, but with shorter timeout
            try:
                page.wait_for_timeout(1000)
            except Exception:
                pass  # Don't fail if timeout fails
            
            # Capture behavioral data with timeout
            try:
                interaction_data = page.evaluate("() => window.microbehaviourData", timeout=5000)
            except Exception:
                interaction_data = {}
            
            # Take screenshot if requested
            screenshot_file = None
            if capture_screenshot:
                try:
                    domain = urlparse(url).netloc.replace(".", "_")
                    timestamp = int(time.time())
                    screenshot_file = screenshot_path / f"{domain}_{timestamp}.png"
                    page.screenshot(path=str(screenshot_file), full_page=True, timeout=5000)
                except Exception:
                    pass  # Don't fail if screenshot fails
            
            # Get DOM snapshot
            try:
                dom_snapshot = page.content()
            except Exception:
                dom_snapshot = ""
            
            # Get response time with timeout
            try:
                response_time = page.evaluate("() => performance.timing.loadEventEnd - performance.timing.navigationStart", timeout=5000)
            except Exception:
                response_time = 0
            
            return ScrapingResult(
                url=url,
                html=dom_snapshot,
                screenshot_path=str(screenshot_file) if screenshot_file else None,
                dom_snapshot=dom_snapshot,
                interaction_data=interaction_data,
                response_time_ms=response_time,
                needs_js=True
            )
            
        finally:
            browser.close()


def fetch_html_hybrid(
    url: str,
    timeout_seconds: int = 20,
    max_retries: int = 2,
    capture_screenshot: bool = True,
    screenshot_dir: Optional[str] = None
) -> ScrapingResult:
    """Simplified approach: use static HTML only for reliability.
    
    This avoids the complexity and potential hanging issues of dynamic rendering.
    """
    try:
        # Use static HTML only for now
        html = fetch_html_static(url, timeout_seconds, max_retries)
        
        return ScrapingResult(
            url=url,
            html=html,
            needs_js=False
        )
            
    except Exception as static_error:
        print(f"Static fetch failed for {url}: {static_error}")
        # Return empty result instead of trying dynamic
        return ScrapingResult(
            url=url,
            html="",
            needs_js=False
        )


def extract_structured_content(html: str) -> Dict[str, Any]:
    """Extract structured content from HTML for better analysis."""
    try:
        from bs4 import BeautifulSoup
        from readability import Document
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract main content using readability
        doc = Document(html)
        main_content = doc.summary()
        
        # Extract sections
        sections = {}
        for section in soup.find_all(['section', 'div'], class_=re.compile(r'hero|feature|pricing|cta|footer|header', re.I)):
            section_type = None
            for class_name in section.get('class', []):
                if any(keyword in class_name.lower() for keyword in ['hero', 'feature', 'pricing', 'cta', 'footer', 'header']):
                    section_type = class_name
                    break
            
            if section_type:
                sections[section_type] = {
                    'text': section.get_text(strip=True)[:500],
                    'html': str(section)[:1000],
                    'links': [a.get('href') for a in section.find_all('a', href=True)]
                }
        
        # Extract clickable elements
        clickable_elements = []
        for element in soup.find_all(['a', 'button', 'input']):
            if element.name == 'input' and element.get('type') in ['submit', 'button']:
                clickable_elements.append({
                    'type': 'input',
                    'text': element.get('value', ''),
                    'classes': element.get('class', []),
                    'id': element.get('id', '')
                })
            elif element.name in ['a', 'button']:
                clickable_elements.append({
                    'type': element.name,
                    'text': element.get_text(strip=True)[:100],
                    'href': element.get('href', ''),
                    'classes': element.get('class', []),
                    'id': element.get('id', '')
                })
        
        # Extract trust signals
        trust_signals = []
        trust_patterns = [
            'testimonial', 'review', 'rating', 'star', 'badge', 'certified',
            'trusted', 'secure', 'ssl', 'guarantee', 'warranty'
        ]
        
        for pattern in trust_patterns:
            elements = soup.find_all(text=re.compile(pattern, re.I))
            for element in elements:
                parent = element.parent
                if parent:
                    trust_signals.append({
                        'type': pattern,
                        'text': element.strip()[:200],
                        'context': parent.get_text(strip=True)[:300]
                    })
        
        return {
            'main_content': main_content,
            'title': soup.title.string if soup.title else '',
            'meta_description': soup.find('meta', attrs={'name': 'description'}).get('content', '') if soup.find('meta', attrs={'name': 'description'}) else '',
            'sections': sections,
            'clickable_elements': clickable_elements,
            'trust_signals': trust_signals,
            'word_count': len(soup.get_text().split()),
            'link_count': len(soup.find_all('a')),
            'form_count': len(soup.find_all('form'))
        }
        
    except ImportError:
        # Fallback if readability is not available
        return {
            'error': 'readability library not installed. Install with: pip install readability-lxml'
        }
    except Exception as e:
        return {
            'error': f'Failed to extract structured content: {str(e)}'
        }


