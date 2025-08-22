#!/usr/bin/env python3
"""
Test script to validate the microbehavior analysis is working properly.
This script loads the environment and tests the analysis function directly.
"""

import sys
import os
import logging
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from microbehaviour.analysis import analyze_user_journey

def test_analysis():
    """Test the analysis function with a known working URL."""
    print("=" * 60)
    print("TESTING MICROBEHAVIOR ANALYSIS")
    print("=" * 60)
    
    # Check environment
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"OpenAI API Key: {'✓ SET' if api_key else '✗ NOT SET'}")
    
    if not api_key:
        print("❌ Cannot run test - OpenAI API Key not found!")
        return False
    
    test_url = "https://www.apple.com"
    print(f"Testing with URL: {test_url}")
    print("-" * 60)
    
    try:
        # Run the analysis
        result = analyze_user_journey(test_url, max_pages=2, max_depth=1)
        
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        print(f"✓ URL: {result.url}")
        print(f"✓ Total Steps: {result.total_steps}")
        print(f"✓ Funnel Type: {result.conversion_funnel_type}")
        print(f"✓ Primary Goal: {result.primary_goal}")
        print(f"✓ Complexity: {result.journey_complexity}")
        
        # Count total microbehaviors
        total_microbehaviors = sum(len(step.microbehaviors) for step in result.journey_steps)
        print(f"✓ Total Microbehaviors: {total_microbehaviors}")
        
        print("\nJourney Steps:")
        for i, step in enumerate(result.journey_steps, 1):
            print(f"  {i}. {step.step_name} ({len(step.microbehaviors)} microbehaviors)")
            for j, micro in enumerate(step.microbehaviors[:2], 1):  # Show first 2
                print(f"     - {micro['behavior']}")
            if len(step.microbehaviors) > 2:
                print(f"     ... and {len(step.microbehaviors) - 2} more")
        
        if result.total_steps > 0 and total_microbehaviors > 0:
            print("\n🎉 SUCCESS: Analysis working correctly!")
            print(f"   Generated {result.total_steps} steps with {total_microbehaviors} microbehaviors")
            return True
        else:
            print("\n❌ FAILURE: No steps or microbehaviors generated")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: Analysis failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analysis()
    exit(0 if success else 1)
