#!/usr/bin/env python3
"""
Test script for granular action analysis
This demonstrates the new step-by-step user action functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from microbehaviour.analysis import analyze_granular_actions
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_granular_analysis():
    """Test the granular action analysis with a sample URL"""
    
    # Test URL - using a simple, well-structured site
    test_url = "https://calendly.com"
    test_goal = "Book a consultation call"
    
    logger.info(f"🚀 Testing granular action analysis")
    logger.info(f"URL: {test_url}")
    logger.info(f"Goal: {test_goal}")
    
    try:
        # Run the granular analysis
        report = analyze_granular_actions(test_url, goal=test_goal, max_pages=2, max_depth=1)
        
        # Display results in a step-by-step format
        print("\n" + "="*80)
        print("📋 GRANULAR ACTION ANALYSIS RESULTS")
        print("="*80)
        
        print(f"\n🎯 Goal: {report.goal}")
        print(f"🌐 URL: {report.url}")
        print(f"📊 Total Steps: {report.interaction_details.total_steps}")
        
        print(f"\n📈 STEP-BY-STEP USER ACTION SEQUENCE")
        print("-" * 50)
        
        for i, action in enumerate(report.action_sequence, 1):
            friction_icon = "🔥" * action.friction_level  # Visual friction indicator
            
            print(f"\n{i:2d}. {action.action_type.upper()}: {action.action_description}")
            print(f"    🎯 Target: {action.content_target}")
            print(f"    {friction_icon} Friction Level: {action.friction_level}/5")
            
            if action.success_indicators:
                print(f"    ✅ Success Signs: {', '.join(action.success_indicators[:2])}")
            
            if action.failure_points:
                print(f"    ⚠️  Risk Points: {', '.join(action.failure_points[:2])}")
        
        # Show critical path
        if report.interaction_details.critical_path_steps:
            print(f"\n🎯 CRITICAL PATH STEPS (Essential for conversion):")
            critical_steps = report.interaction_details.critical_path_steps
            for step_num in critical_steps[:5]:  # Show first 5
                if step_num <= len(report.action_sequence):
                    action = report.action_sequence[step_num - 1]
                    print(f"    {step_num}. {action.action_description}")
        
        # Show optimization opportunities
        if report.interaction_details.optimization_sequence:
            print(f"\n🔧 OPTIMIZATION OPPORTUNITIES:")
            for i, opt in enumerate(report.interaction_details.optimization_sequence[:3], 1):
                print(f"    {i}. {opt}")
        
        # Show drop-off risks
        if report.interaction_details.drop_off_risks:
            print(f"\n⚠️  DROP-OFF RISK POINTS:")
            for risk in report.interaction_details.drop_off_risks[:3]:
                print(f"    Step {risk.step_number}: {risk.risk_description}")
        
        print("\n" + "="*80)
        print("✅ Analysis completed successfully!")
        print("="*80)
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise

def format_action_sequence_simple(action_sequence):
    """Format action sequence in simple arrow format like: Click ad > Read headline > Fill form"""
    
    if not action_sequence:
        return "No actions found"
    
    # Take first 8 steps for a concise overview
    key_actions = action_sequence[:8]
    
    # Extract just the main action part
    simple_actions = []
    for action in key_actions:
        # Extract the main action from the description
        desc = action.action_description
        
        # Simplify common patterns
        if "Read headline:" in desc:
            simple_actions.append("Read headline")
        elif "Click" in desc:
            simple_actions.append(f"Click {action.content_target}")
        elif "Fill" in desc:
            simple_actions.append(f"Fill {action.content_target}")
        elif "Submit" in desc:
            simple_actions.append("Submit form")
        elif "Scroll" in desc:
            simple_actions.append("Scroll page")
        elif "Land" in desc:
            simple_actions.append("Land on page")
        else:
            # Use first 3 words for other actions
            words = desc.split()[:3]
            simple_actions.append(" ".join(words))
    
    return " > ".join(simple_actions)

if __name__ == "__main__":
    print("🔍 Granular Action Analysis Test")
    print("This will analyze user micro-interactions step by step")
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key to run this test")
        sys.exit(1)
    
    try:
        report = test_granular_analysis()
        
        # Show simple format at the end
        print(f"\n🎯 SIMPLE ACTION FLOW:")
        simple_flow = format_action_sequence_simple(report.action_sequence)
        print(f"   {simple_flow}")
        
    except KeyboardInterrupt:
        print("\n👋 Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
