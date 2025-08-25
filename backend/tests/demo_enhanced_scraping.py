#!/usr/bin/env python3
"""
Demo script showcasing the enhanced scraping capabilities of microbehaviour.

This script demonstrates:
1. Hybrid scraping (static + dynamic)
2. Behavioral interaction tracking
3. Friction pattern analysis
4. Site graph building
5. Screenshot capture
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the microbehaviour package to the path
sys.path.insert(0, str(Path(__file__).parent))

from microbehaviour.scraper import fetch_html_hybrid, extract_structured_content
from microbehaviour.crawler import crawl_same_host_enhanced, analyze_friction_patterns, export_site_graph


def demo_single_page_scraping():
    """Demonstrate enhanced single-page scraping capabilities."""
    print("🚀 Demo: Enhanced Single-Page Scraping")
    print("=" * 50)
    
    # Test with a JavaScript-heavy site
    test_url = "https://example.com"  # Replace with actual test URL
    
    print(f"Testing hybrid scraping on: {test_url}")
    print("This will automatically detect if JavaScript rendering is needed...")
    
    try:
        # Use hybrid scraping
        result = fetch_html_hybrid(
            test_url,
            capture_screenshot=True,
            screenshot_dir="demo_screenshots"
        )
        
        print(f"\n✅ Scraping Results:")
        print(f"  📄 HTML Length: {len(result.html):,} characters")
        print(f"  🖥️  JavaScript Required: {result.needs_js}")
        print(f"  ⏱️  Response Time: {result.response_time_ms:.0f}ms" if result.response_time_ms else "  ⏱️  Response Time: N/A")
        
        if result.screenshot_path:
            print(f"  📸 Screenshot: {result.screenshot_path}")
        
        # Show interaction data if captured
        if result.interaction_data:
            print(f"\n🖱️  Behavioral Data Captured:")
            for event_type, events in result.interaction_data.items():
                if isinstance(events, list):
                    print(f"    • {event_type}: {len(events)} events")
                    
                    # Show some sample events
                    if events and len(events) > 0:
                        sample = events[0]
                        if isinstance(sample, dict):
                            if 'x' in sample and 'y' in sample:
                                print(f"      Sample: Click at ({sample['x']}, {sample['y']})")
                            elif 'depth' in sample:
                                print(f"      Sample: Scroll to {sample['depth']:.1f}%")
        
        # Extract structured content
        print(f"\n🔍 Content Analysis:")
        structured = extract_structured_content(result.html)
        
        if 'error' not in structured:
            print(f"  📊 Word Count: {structured.get('word_count', 0):,}")
            print(f"  🔗 Links: {structured.get('link_count', 0)}")
            print(f"  📝 Forms: {structured.get('form_count', 0)}")
            print(f"  🏗️  Sections: {len(structured.get('sections', {}))}")
            print(f"  🛡️  Trust Signals: {len(structured.get('trust_signals', []))}")
        else:
            print(f"  ⚠️  Content extraction failed: {structured['error']}")
            
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("Make sure you have Playwright installed: pip install playwright && playwright install")


def demo_site_analysis():
    """Demonstrate full site analysis with behavioral insights."""
    print("\n\n🌐 Demo: Full Site Analysis & Friction Detection")
    print("=" * 60)
    
    # Test with a small site crawl
    test_url = "https://example.com"  # Replace with actual test URL
    
    print(f"Starting enhanced site analysis for: {test_url}")
    print("This will crawl multiple pages and analyze friction patterns...")
    
    try:
        # Crawl the site
        site_graph = crawl_same_host_enhanced(
            start_url=test_url,
            max_pages=5,  # Keep it small for demo
            max_depth=1,
            capture_screenshots=True,
            screenshot_dir="demo_screenshots"
        )
        
        print(f"\n✅ Site Analysis Complete!")
        print(f"  📊 Pages Analyzed: {site_graph.total_pages}")
        print(f"  📱 JavaScript Pages: {site_graph.js_pages_count}")
        print(f"  ⚡ Static Pages: {site_graph.static_pages_count}")
        print(f"  ⏱️  Avg Response Time: {site_graph.avg_response_time:.0f}ms")
        print(f"  🖱️  Total Interactions: {site_graph.total_interactions}")
        
        # Analyze friction patterns
        print(f"\n🔍 Friction Pattern Analysis:")
        analysis = analyze_friction_patterns(site_graph)
        
        # Show high friction pages
        if analysis['high_friction_pages']:
            print(f"  🚨 High Friction Pages:")
            for page in analysis['high_friction_pages'][:3]:  # Top 3
                print(f"    • {page['url']} (Score: {page['score']:.1f})")
        
        # Show performance issues
        if analysis['performance_issues']:
            print(f"  🐌 Performance Issues:")
            for issue in analysis['performance_issues'][:2]:  # Top 2
                print(f"    • {issue['url']} ({issue['response_time']:.0f}ms)")
        
        # Show interaction insights
        insights = analysis['interaction_insights']
        if insights['total_clicks'] > 0:
            print(f"  🖱️  Interaction Insights:")
            print(f"    • Total Clicks: {insights['total_clicks']}")
            print(f"    • Rage Clicks: {insights['total_rage_clicks']}")
            print(f"    • Rage Click Rate: {insights['rage_click_rate']:.1f}%")
            print(f"    • Avg Interactions/Page: {insights['avg_interactions_per_page']:.1f}")
        
        # Show recommendations
        if analysis['recommendations']:
            print(f"  💡 Recommendations:")
            for rec in analysis['recommendations']:
                print(f"    • {rec}")
        
        # Export results
        export_file = "demo_site_analysis.json"
        export_site_graph(site_graph, export_file)
        print(f"\n💾 Full analysis exported to: {export_file}")
        
    except Exception as e:
        print(f"❌ Error during site analysis: {e}")
        print("Make sure you have Playwright installed: pip install playwright && playwright install")


def main():
    """Run the enhanced scraping demo."""
    print("🎯 Microbehaviour Enhanced Scraping Demo")
    print("=" * 50)
    print("This demo showcases the enhanced scraping capabilities including:")
    print("• Hybrid scraping (static + dynamic)")
    print("• Behavioral interaction tracking")
    print("• Friction pattern analysis")
    print("• Site graph building")
    print("• Screenshot capture")
    print("• Structured content extraction")
    print()
    
    # Create screenshots directory
    Path("demo_screenshots").mkdir(exist_ok=True)
    
    try:
        # Demo 1: Single page scraping
        demo_single_page_scraping()
        
        # Demo 2: Full site analysis
        demo_site_analysis()
        
        print("\n🎉 Demo completed successfully!")
        print("Check the 'demo_screenshots' directory for captured screenshots")
        print("Check 'demo_site_analysis.json' for the full analysis data")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        print("playwright install")


if __name__ == "__main__":
    main()
