#!/usr/bin/env python3
"""
Demo script showing the enhanced goal-oriented action flow
This demonstrates what the new conversion-focused analysis looks like
"""

def demo_conversion_flows():
    """Show examples of goal-oriented conversion flows"""
    
    print("\n" + "="*80)
    print("🎯 GOAL-ORIENTED USER ACTION FLOWS")
    print("="*80)
    
    # Example 1: Book consultation call
    print(f"\n📞 GOAL: Book a consultation call")
    print("-" * 50)
    call_booking_flow = [
        "1. Land on homepage from Google search",
        "2. First glance at hero section and main image",
        "3. Read headline: 'Transform Your Business in 30 Days'",
        "4. Scan 3 key benefits in hero section",
        "5. Scroll down to view services section",
        "6. Read service descriptions and packages",
        "7. Scroll to testimonials section",
        "8. Read 2-3 client testimonial quotes",
        "9. Scroll to pricing section",
        "10. Check pricing: 'Free consultation, then $2500/month'",
        "11. Scroll back up to CTA section",
        "12. Click 'Book Free Consultation' CTA button",
        "13. Fill 'Full Name' field: 'John Smith'",
        "14. Fill 'Business Email' field: 'john@company.com'",
        "15. Fill 'Phone Number' field: '+1-555-0123'",
        "16. Select 'Company Size': '10-50 employees'",
        "17. Choose time slot: 'Tomorrow 2:00 PM'",
        "18. Click 'Confirm Booking' button",
        "19. See confirmation: 'Your call is booked!'",
        "20. Receive calendar invite email"
    ]
    
    for step in call_booking_flow:
        if "Click" in step and ("CTA" in step or "Confirm" in step):
            print(f"    🎯 {step}")  # Mark main CTA
        elif "Fill" in step or "Select" in step or "Choose" in step:
            print(f"    📝 {step}")  # Mark form interactions  
        elif "Scroll" in step:
            print(f"    📜 {step}")  # Mark scrolling behavior
        elif "confirmation" in step.lower() or "booked" in step.lower() or "calendar" in step.lower():
            print(f"    ✅ {step}")  # Mark success
        else:
            print(f"    👀 {step}")  # Mark viewing/reading
    
    # Example 2: Purchase product
    print(f"\n🛒 GOAL: Purchase online course")
    print("-" * 50)
    purchase_flow = [
        "1. Land on product page from Facebook ad",
        "2. First look at product hero image and title",
        "3. Watch 2-minute product demo video",
        "4. Scroll down to read course curriculum",
        "5. Read curriculum outline and modules",
        "6. Scroll to testimonials section",
        "7. Read 3-4 student success stories",
        "8. Scroll to FAQ section",
        "9. Read common questions and answers",
        "10. Scroll to pricing section", 
        "11. Check pricing: '$497 one-time payment'",
        "12. Read guarantee: '30-day money back'",
        "13. Scroll back up to main CTA",
        "14. Click 'Enroll Now' button",
        "15. Select payment plan: 'Pay in full'",
        "16. Fill billing name: 'Sarah Johnson'",
        "17. Fill billing email: 'sarah@email.com'",
        "18. Enter credit card number",
        "19. Fill expiry date and CVV",
        "20. Click 'Complete Purchase' button",
        "21. See order confirmation page",
        "22. Get course access email instantly"
    ]
    
    for step in purchase_flow:
        if "Click" in step and ("Enroll" in step or "Purchase" in step):
            print(f"    🎯 {step}")  # Mark main CTA
        elif "Fill" in step or "Enter" in step or "Select" in step:
            print(f"    💳 {step}")  # Mark payment/form steps
        elif "Scroll" in step:
            print(f"    📜 {step}")  # Mark scrolling behavior
        elif "confirmation" in step.lower() or "access" in step.lower():
            print(f"    ✅ {step}")  # Mark success
        else:
            print(f"    👀 {step}")  # Mark viewing/reading
    
    # Example 3: Download lead magnet
    print(f"\n📥 GOAL: Download free guide")
    print("-" * 50)
    download_flow = [
        "1. Land on blog post from LinkedIn",
        "2. Read article headline and intro paragraph",
        "3. Scroll through article content",
        "4. Read key statistics and insights",
        "5. View report preview image/screenshots",
        "6. Scroll to bottom of article",
        "7. See CTA: 'Download Full Industry Report'",
        "8. Read CTA description: 'Get the complete 50-page report'",
        "9. Click 'Get Free Report' button",
        "10. Fill 'First Name': 'Mike'",
        "11. Fill 'Work Email': 'mike@company.com'",
        "12. Select 'Job Title': 'Marketing Manager'",
        "13. Choose 'Company Size': '100-500 employees'",
        "14. Click 'Send Download Link' button",
        "15. See success message: 'Check your email'",
        "16. Open email with download link",
        "17. Click download link to get PDF"
    ]
    
    for step in download_flow:
        if "Click" in step and ("Get" in step or "Send" in step or "download link" in step):
            print(f"    🎯 {step}")  # Mark main CTA
        elif "Fill" in step or "Select" in step or "Choose" in step:
            print(f"    📋 {step}")  # Mark form interactions
        elif "Scroll" in step:
            print(f"    📜 {step}")  # Mark scrolling behavior
        elif "success" in step.lower() or "email" in step.lower() and "Open" in step:
            print(f"    ✅ {step}")  # Mark success
        else:
            print(f"    👀 {step}")  # Mark viewing/reading
    
    print(f"\n💡 KEY IMPROVEMENTS:")
    print("   • FOCUSED approach: 6-9 critical behaviors only (quality over quantity)")
    print("   • Realistic browsing behavior BEFORE clicking CTAs")
    print("   • Natural scrolling patterns and content exploration")
    print("   • Trust-building moments (reading reviews, checking guarantees)")
    print("   • Complete conversion paths from landing to goal achievement")
    print("   • Realistic form field interactions with example data")
    print("   • Clear success confirmations and next steps")
    print("   • Strictly below 10 microbehaviors - most essential actions only")
    print("   📜 Scroll actions: 📝 Form filling: 🎯 CTA clicks: ✅ Success steps")
    
    print("\n" + "="*80)
    print("✨ Enhanced goal-oriented analysis ready!")
    print("="*80)

if __name__ == "__main__":
    demo_conversion_flows()
