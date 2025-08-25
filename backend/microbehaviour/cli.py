from __future__ import annotations

import argparse
import os
import sys

from .analysis import analyze_experience, analyze_user_journey


def main() -> int:
    parser = argparse.ArgumentParser(description="Crawl, scrape signals, and analyze with LLM.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Experience analysis command
    experience_parser = subparsers.add_parser("experience", help="Analyze user experience and microbehaviors")
    experience_parser.add_argument("--url", required=True, help="Page URL to analyze")
    experience_parser.add_argument("--goal", default=None, help="Business goal, e.g., 'Book a call'")
    experience_parser.add_argument("--max-pages", type=int, default=3)
    experience_parser.add_argument("--max-depth", type=int, default=1)
    
    # User journey analysis command
    journey_parser = subparsers.add_parser("journey", help="Analyze user journey and conversion funnel")
    journey_parser.add_argument("--url", required=True, help="Page URL to analyze")
    journey_parser.add_argument("--max-pages", type=int, default=3)
    journey_parser.add_argument("--max-depth", type=int, default=1)
    
    # Enhanced site analysis command
    analyze_parser = subparsers.add_parser("analyze-site", help="Analyze website for behavioral friction and UX issues")
    analyze_parser.add_argument("--url", required=True, help="URL to crawl and analyze")
    analyze_parser.add_argument("--max-pages", type=int, default=10, help="Maximum pages to crawl")
    analyze_parser.add_argument("--max-depth", type=int, default=2, help="Maximum crawl depth")
    analyze_parser.add_argument("--screenshots", action="store_true", default=True, help="Capture screenshots")
    analyze_parser.add_argument("--output", default="site_analysis.json", help="Output file for analysis")
    
    # Test scraping command
    test_parser = subparsers.add_parser("test-scraping", help="Test enhanced hybrid scraping capabilities")
    test_parser.add_argument("--url", required=True, help="URL to test with hybrid scraping")
    test_parser.add_argument("--screenshot", action="store_true", default=True, help="Capture screenshot")
    
    args = parser.parse_args()
    
    if args.command == "experience":
        report = analyze_experience(args.url, args.goal, args.max_pages, args.max_depth)
        print(report.model_dump_json(indent=2))
    elif args.command == "journey":
        report = analyze_user_journey(args.url, args.max_pages, args.max_depth)
        print(report.model_dump_json(indent=2))
    elif args.command == "analyze-site":
        from .crawler import crawl_same_host_enhanced, export_site_graph, analyze_friction_patterns
        
        print(f"🔍 Starting enhanced site analysis for {args.url}")
        print(f"📊 Will crawl up to {args.max_pages} pages at depth {args.max_depth}")
        
        try:
            # Crawl the site with enhanced behavioral tracking
            site_graph = crawl_same_host_enhanced(
                start_url=args.url,
                max_pages=args.max_pages,
                max_depth=args.max_depth,
                capture_screenshots=args.screenshots
            )
            
            print(f"✅ Crawling complete! Analyzed {site_graph.total_pages} pages")
            print(f"📱 JavaScript pages: {site_graph.js_pages_count}")
            print(f"⚡ Static pages: {site_graph.static_pages_count}")
            print(f"⏱️  Average response time: {site_graph.avg_response_time:.0f}ms")
            print(f"🖱️  Total interactions captured: {site_graph.total_interactions}")
            
            # Analyze friction patterns
            print("\n🔍 Analyzing friction patterns...")
            analysis = analyze_friction_patterns(site_graph)
            
            # Display key insights
            print(f"\n🚨 High friction pages (top {len(analysis['high_friction_pages'])}):")
            for page in analysis['high_friction_pages']:
                print(f"  • {page['url']} (Score: {page['score']:.1f})")
            
            if analysis['performance_issues']:
                print(f"\n🐌 Performance issues ({len(analysis['performance_issues'])} slow pages):")
                for issue in analysis['performance_issues'][:3]:  # Show top 3
                    print(f"  • {issue['url']} ({issue['response_time']:.0f}ms)")
            
            if analysis['interaction_insights']['rage_click_rate'] > 0:
                print(f"\n😤 Rage click rate: {analysis['interaction_insights']['rage_click_rate']:.1f}%")
            
            # Display recommendations
            if analysis['recommendations']:
                print(f"\n💡 Recommendations:")
                for rec in analysis['recommendations']:
                    print(f"  • {rec}")
            
            # Export results
            export_site_graph(site_graph, args.output)
            print(f"\n💾 Full analysis exported to {args.output}")
            
        except Exception as e:
            print(f"❌ Error during site analysis: {e}")
            return 1
            
    elif args.command == "test-scraping":
        from .scraper import fetch_html_hybrid, extract_structured_content
        
        print(f"🧪 Testing hybrid scraping for {args.url}")
        
        try:
            # Test hybrid scraping
            result = fetch_html_hybrid(args.url, capture_screenshot=args.screenshot)
            
            print(f"✅ Scraping successful!")
            print(f"📄 HTML length: {len(result.html):,} characters")
            print(f"🖥️  Needs JavaScript: {result.needs_js}")
            print(f"⏱️  Response time: {result.response_time_ms:.0f}ms" if result.response_time_ms else "⏱️  Response time: N/A")
            
            if result.screenshot_path:
                print(f"📸 Screenshot saved: {result.screenshot_path}")
            
            if result.interaction_data:
                print(f"🖱️  Interaction data captured:")
                for key, data in result.interaction_data.items():
                    if isinstance(data, list):
                        print(f"  • {key}: {len(data)} events")
            
            # Test structured content extraction
            print(f"\n🔍 Extracting structured content...")
            structured = extract_structured_content(result.html)
            
            if 'error' not in structured:
                print(f"📊 Content analysis:")
                print(f"  • Title: {structured.get('title', 'N/A')[:100]}...")
                print(f"  • Word count: {structured.get('word_count', 0):,}")
                print(f"  • Links: {structured.get('link_count', 0)}")
                print(f"  • Forms: {structured.get('form_count', 0)}")
                print(f"  • Sections: {len(structured.get('sections', {}))}")
                print(f"  • Trust signals: {len(structured.get('trust_signals', []))}")
            else:
                print(f"⚠️  Content extraction failed: {structured['error']}")
                
        except Exception as e:
            print(f"❌ Error during scraping test: {e}")
            return 1
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


