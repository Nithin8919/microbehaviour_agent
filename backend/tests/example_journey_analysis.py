#!/usr/bin/env python3
"""
Example script demonstrating user journey analysis for conversion funnels.

This script shows how to use the microbehaviour library to analyze scraped content
and identify user journey patterns similar to the 9-step conversion funnel:

1. Land on homepage via ad, social link, or referral
2. Read the main headline + subheadline
3. Glance at credibility elements (client logos, revenue, success rate)
4. Skim through 'How It Works' section to understand the framework
5. Scroll through testimonials to see social proof
6. Check pricing table and compare plan features
7. Click 'Get Started' or 'Book a Call' CTA
8. Fill in booking form (name, email, company, goals)
9. Confirm calendar time slot for the call
"""

import json
from microbehaviour.analysis import analyze_user_journey


def analyze_conversion_funnel(url: str, max_pages: int = 3, max_depth: int = 1):
    """
    Analyze a website's conversion funnel by mapping the user journey.
    
    Args:
        url: The website URL to analyze
        max_pages: Maximum number of pages to crawl
        max_depth: Maximum depth for crawling
        
    Returns:
        UserJourneyReport object with detailed journey analysis
    """
    print(f"🔍 Analyzing user journey for: {url}")
    print(f"📊 Crawling up to {max_pages} pages at depth {max_depth}")
    print("-" * 60)
    
    try:
        # Perform the journey analysis
        report = analyze_user_journey(url, max_pages, max_depth)
        
        # Display the results
        print(f"✅ Analysis complete! Found {report.total_steps} journey steps")
        print(f"🎯 Primary goal: {report.primary_goal}")
        print(f"🔄 Conversion funnel type: {report.conversion_funnel_type}")
        print(f"📈 Journey complexity: {report.journey_complexity}")
        print("\n" + "=" * 60)
        
        # Display each journey step
        for step in report.journey_steps:
            print(f"\n📋 Step {step.step_number}: {step.step_name}")
            print(f"   Description: {step.description}")
            
            if step.content_elements:
                print(f"   Content elements: {', '.join(step.content_elements)}")
            
            if step.user_actions:
                print(f"   User actions: {', '.join(step.user_actions)}")
            
            if step.conversion_indicators:
                print(f"   Conversion indicators: {', '.join(step.conversion_indicators)}")
            
            if step.friction_points:
                print(f"   ⚠️  Friction points: {', '.join(step.friction_points)}")
            
            if step.optimization_suggestions:
                print(f"   💡 Optimization suggestions: {', '.join(step.optimization_suggestions)}")
        
        # Display key insights
        if report.key_moments_of_truth:
            print(f"\n🎯 Key Moments of Truth:")
            for moment in report.key_moments_of_truth:
                print(f"   • {moment}")
        
        if report.optimization_priorities:
            print(f"\n🚀 Optimization Priorities:")
            for priority in report.optimization_priorities:
                print(f"   • {priority}")
        
        return report
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return None


def save_report_to_file(report, filename: str = "user_journey_report.json"):
    """Save the analysis report to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(report.model_dump(), f, indent=2)
        print(f"\n💾 Report saved to: {filename}")
    except Exception as e:
        print(f"❌ Error saving report: {e}")


if __name__ == "__main__":
    # Example usage
    example_url = "https://example.com"  # Replace with actual URL
    
    print("🚀 User Journey Analysis Example")
    print("=" * 60)
    print("This script analyzes conversion funnels by mapping user journeys")
    print("from scraped website content.\n")
    
    # Get URL from user input
    url = input(f"Enter website URL to analyze (or press Enter for example): ").strip()
    if not url:
        url = example_url
        print(f"Using example URL: {url}")
    
    # Perform the analysis
    report = analyze_conversion_funnel(url)
    
    if report:
        # Optionally save to file
        save_choice = input("\nSave detailed report to JSON file? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes']:
            filename = input("Enter filename (or press Enter for default): ").strip()
            if not filename:
                filename = "user_journey_report.json"
            save_report_to_file(report, filename)
        
        print("\n🎉 Analysis complete! Use the insights to optimize your conversion funnel.")
