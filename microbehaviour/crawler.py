from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable, List, Set, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import json
import time

from bs4 import BeautifulSoup

from .scraper import fetch_html_hybrid, ScrapingResult, extract_structured_content


@dataclass
class PageNode:
    """Represents a page in the site graph with behavioral data."""
    url: str
    html: str
    screenshot_path: Optional[str] = None
    interaction_data: Optional[Dict[str, Any]] = None
    structured_content: Optional[Dict[str, Any]] = None
    response_time_ms: Optional[float] = None
    needs_js: bool = False
    crawl_timestamp: float = 0.0
    friction_score: Optional[float] = None
    error: Optional[str] = None


@dataclass
class SiteGraph:
    """Represents the complete site structure with behavioral insights."""
    nodes: Dict[str, PageNode]
    edges: List[tuple[str, str]]  # (from_url, to_url)
    start_url: str
    crawl_timestamp: float
    total_pages: int
    total_interactions: int
    avg_response_time: float
    js_pages_count: int
    static_pages_count: int


def is_same_host(base_url: str, candidate_url: str) -> bool:
    b = urlparse(base_url)
    c = urlparse(candidate_url)
    return (c.scheme in {"http", "https"}) and (c.netloc == b.netloc)


def normalize_link(base_url: str, href: str | None) -> str | None:
    if not href:
        return None
    if href.startswith("mailto:") or href.startswith("tel:") or href.startswith("#"):
        return None
    return urljoin(base_url, href)


def extract_links(base_url: str, html: str) -> List[str]:
    soup = BeautifulSoup(html, 'lxml')
    links: List[str] = []
    for a in soup.find_all("a"):
        normalized = normalize_link(base_url, a.get("href"))
        if normalized and is_same_host(base_url, normalized):
            links.append(normalized)
    return links


def calculate_friction_score(page_node: PageNode) -> float:
    """Calculate a friction score based on behavioral data and content analysis.
    
    Lower scores indicate higher friction (more problematic pages).
    """
    score = 100.0  # Start with perfect score
    
    # Penalize slow response times
    if page_node.response_time_ms:
        if page_node.response_time_ms > 5000:  # > 5 seconds
            score -= 30
        elif page_node.response_time_ms > 3000:  # > 3 seconds
            score -= 20
        elif page_node.response_time_ms > 1000:  # > 1 second
            score -= 10
    
    # Penalize JavaScript-heavy pages (potential loading issues)
    if page_node.needs_js:
        score -= 15
    
    # Analyze interaction data if available
    if page_node.interaction_data:
        # Penalize rage clicks (user frustration)
        rage_clicks = page_node.interaction_data.get('rageClicks', [])
        if rage_clicks:
            score -= len(rage_clicks) * 10
        
        # Penalize low scroll depth (content not engaging)
        scrolls = page_node.interaction_data.get('scrolls', [])
        if scrolls:
            max_depth = max((s.get('depth', 0) for s in scrolls), default=0)
            if max_depth < 25:  # Less than 25% scroll
                score -= 20
            elif max_depth < 50:  # Less than 50% scroll
                score -= 10
        
        # Penalize low click engagement
        clicks = page_node.interaction_data.get('clicks', [])
        if len(clicks) < 2:  # Very few interactions
            score -= 15
    
    # Analyze structured content if available
    if page_node.structured_content:
        content = page_node.structured_content
        
        # Penalize very short content
        if content.get('word_count', 0) < 100:
            score -= 25
        elif content.get('word_count', 0) < 300:
            score -= 15
        
        # Penalize pages with few clickable elements
        if content.get('link_count', 0) < 3:
            score -= 10
        
        # Penalize pages without clear CTAs
        clickable_elements = content.get('clickable_elements', [])
        cta_keywords = ['buy', 'sign up', 'get started', 'learn more', 'contact', 'download']
        has_cta = any(
            any(keyword in element.get('text', '').lower() for keyword in cta_keywords)
            for element in clickable_elements
        )
        if not has_cta:
            score -= 15
    
    # Ensure score doesn't go below 0
    return max(0.0, score)


def crawl_same_host_enhanced(
    start_url: str, 
    max_pages: int = 10, 
    max_depth: int = 2,
    capture_screenshots: bool = True,
    screenshot_dir: Optional[str] = None
) -> SiteGraph:
    """Enhanced crawler that captures behavioral data and builds a site graph.
    
    This version captures much richer data for behavioral analysis and
    friction detection compared to the basic crawler.
    """
    visited: Set[str] = set()
    queue: deque[tuple[str, int]] = deque([(start_url, 0)])
    nodes: Dict[str, PageNode] = {}
    edges: List[tuple[str, str]] = []
    crawl_start = time.time()
    
    total_interactions = 0
    js_pages_count = 0
    static_pages_count = 0
    total_response_time = 0.0
    
    while queue and len(nodes) < max_pages:
        url, depth = queue.popleft()
        
        if url in visited:
            continue
            
        visited.add(url)
        print(f"Crawling {url} (depth {depth})...")
        
        try:
            # Use hybrid scraping for best results
            result = fetch_html_hybrid(
                url, 
                capture_screenshot=capture_screenshots,
                screenshot_dir=screenshot_dir
            )
            
            # Extract structured content
            structured_content = extract_structured_content(result.html)
            
            # Create page node
            page_node = PageNode(
                url=url,
                html=result.html,
                screenshot_path=result.screenshot_path,
                interaction_data=result.interaction_data,
                structured_content=structured_content,
                response_time_ms=result.response_time_ms,
                needs_js=result.needs_js,
                crawl_timestamp=time.time()
            )
            
            # Calculate friction score
            page_node.friction_score = calculate_friction_score(page_node)
            
            # Store node
            nodes[url] = page_node
            
            # Track statistics
            if result.needs_js:
                js_pages_count += 1
            else:
                static_pages_count += 1
                
            if result.response_time_ms:
                total_response_time += result.response_time_ms
                
            if result.interaction_data:
                total_interactions += sum(len(data) for data in result.interaction_data.values())
            
            # Extract links for next level crawling
            if depth < max_depth:
                links = extract_links(url, result.html)
                for link in links:
                    if link not in visited and len(nodes) < max_pages:
                        queue.append((link, depth + 1))
                        edges.append((url, link))
            
            # Add small delay to be respectful
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            # Create error node for failed pages
            error_node = PageNode(
                url=url,
                html="",
                error=str(e),
                crawl_timestamp=time.time(),
                friction_score=0.0  # Failed pages get worst score
            )
            nodes[url] = error_node
    
    # Calculate averages
    avg_response_time = total_response_time / len(nodes) if nodes else 0.0
    
    return SiteGraph(
        nodes=nodes,
        edges=edges,
        start_url=start_url,
        crawl_timestamp=crawl_start,
        total_pages=len(nodes),
        total_interactions=total_interactions,
        avg_response_time=avg_response_time,
        js_pages_count=js_pages_count,
        static_pages_count=static_pages_count
    )


def export_site_graph(site_graph: SiteGraph, output_file: str) -> None:
    """Export the site graph to a JSON file for analysis."""
    export_data = {
        'metadata': {
            'start_url': site_graph.start_url,
            'crawl_timestamp': site_graph.crawl_timestamp,
            'total_pages': site_graph.total_pages,
            'total_interactions': site_graph.total_interactions,
            'avg_response_time': site_graph.avg_response_time,
            'js_pages_count': site_graph.js_pages_count,
            'static_pages_count': site_graph.static_pages_count
        },
        'pages': {}
    }
    
    for url, node in site_graph.nodes.items():
        export_data['pages'][url] = {
            'url': node.url,
            'screenshot_path': node.screenshot_path,
            'interaction_data': node.interaction_data,
            'structured_content': node.structured_content,
            'response_time_ms': node.response_time_ms,
            'needs_js': node.needs_js,
            'crawl_timestamp': node.crawl_timestamp,
            'friction_score': node.friction_score,
            'error': node.error
        }
    
    export_data['edges'] = site_graph.edges
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"Site graph exported to {output_file}")


def analyze_friction_patterns(site_graph: SiteGraph) -> Dict[str, Any]:
    """Analyze the site graph to identify friction patterns and insights."""
    analysis = {
        'high_friction_pages': [],
        'low_friction_pages': [],
        'performance_issues': [],
        'interaction_insights': [],
        'content_quality': [],
        'recommendations': []
    }
    
    # Analyze friction scores
    friction_scores = [(url, node.friction_score) for url, node in site_graph.nodes.items() if node.friction_score is not None]
    friction_scores.sort(key=lambda x: x[1])  # Sort by score (lowest first = highest friction)
    
    # High friction pages (bottom 20%)
    high_friction_count = max(1, len(friction_scores) // 5)
    analysis['high_friction_pages'] = [
        {'url': url, 'score': score, 'rank': i + 1}
        for i, (url, score) in enumerate(friction_scores[:high_friction_count])
    ]
    
    # Low friction pages (top 20%)
    analysis['low_friction_pages'] = [
        {'url': url, 'score': score, 'rank': len(friction_scores) - i}
        for i, (url, score) in enumerate(friction_scores[-high_friction_count:])
    ]
    
    # Performance analysis
    response_times = [node.response_time_ms for node in site_graph.nodes.values() if node.response_time_ms]
    if response_times:
        slow_pages = [
            {'url': url, 'response_time': node.response_time_ms}
            for url, node in site_graph.nodes.items()
            if node.response_time_ms and node.response_time_ms > 3000
        ]
        analysis['performance_issues'] = slow_pages
    
    # Interaction insights
    total_clicks = 0
    total_rage_clicks = 0
    total_scrolls = 0
    
    for node in site_graph.nodes.values():
        if node.interaction_data:
            total_clicks += len(node.interaction_data.get('clicks', []))
            total_rage_clicks += len(node.interaction_data.get('rageClicks', []))
            total_scrolls += len(node.interaction_data.get('scrolls', []))
    
    analysis['interaction_insights'] = {
        'total_clicks': total_clicks,
        'total_rage_clicks': total_rage_clicks,
        'total_scrolls': total_scrolls,
        'rage_click_rate': (total_rage_clicks / total_clicks * 100) if total_clicks > 0 else 0,
        'avg_interactions_per_page': total_clicks / len(site_graph.nodes) if site_graph.nodes else 0
    }
    
    # Content quality analysis
    content_metrics = []
    for url, node in site_graph.nodes.items():
        if node.structured_content and not node.error:
            content = node.structured_content
            metrics = {
                'url': url,
                'word_count': content.get('word_count', 0),
                'link_count': content.get('link_count', 0),
                'form_count': content.get('form_count', 0),
                'has_trust_signals': len(content.get('trust_signals', [])) > 0,
                'section_count': len(content.get('sections', {}))
            }
            content_metrics.append(metrics)
    
    analysis['content_quality'] = content_metrics
    
    # Generate recommendations
    recommendations = []
    
    if analysis['interaction_insights']['rage_click_rate'] > 5:
        recommendations.append("High rage click rate detected - investigate UI responsiveness and button states")
    
    if site_graph.js_pages_count > site_graph.static_pages_count:
        recommendations.append("Many JavaScript-heavy pages - consider optimizing loading performance")
    
    if analysis['performance_issues']:
        recommendations.append(f"{len(analysis['performance_issues'])} slow pages detected - optimize response times")
    
    if not any(metrics['has_trust_signals'] for metrics in content_metrics):
        recommendations.append("No trust signals found - consider adding testimonials, reviews, or security badges")
    
    analysis['recommendations'] = recommendations
    
    return analysis


# Keep the original simple crawler for backward compatibility
def crawl_same_host(start_url: str, max_pages: int = 3, max_depth: int = 1) -> List[str]:
    """Original simple crawler for backward compatibility."""
    visited: Set[str] = set()
    queue: deque[tuple[str, int]] = deque([(start_url, 0)])
    order: List[str] = []

    while queue and len(order) < max_pages:
        url, depth = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        order.append(url)
        if depth >= max_depth:
            continue
        try:
            # Use the new hybrid scraper
            result = fetch_html_hybrid(url)
            html = result.html
        except Exception:
            continue
        for link in extract_links(url, html):
            if link not in visited:
                queue.append((link, depth + 1))
    return order


