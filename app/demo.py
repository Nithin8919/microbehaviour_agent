from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo-data')
def demo_data():
    """Return sample data for demonstration purposes"""
    demo_data = {
        "timeline": [
            {
                "index": 1,
                "stage": "Landing Page",
                "observed": "User arrives at homepage and scans for value proposition",
                "items": [
                    {
                        "behavior": "Hero section scan",
                        "nudge": "Clear value proposition with CTA button",
                        "explanation": "Users spend 2-3 seconds scanning hero section",
                        "frictionScore": 3,
                        "priority": 8,
                        "section": "Hero"
                    },
                    {
                        "behavior": "Navigation exploration",
                        "nudge": "Simplified navigation with clear labels",
                        "explanation": "Complex navigation increases cognitive load",
                        "frictionScore": 6,
                        "priority": 7,
                        "section": "Navigation"
                    }
                ]
            },
            {
                "index": 2,
                "stage": "Product Discovery",
                "observed": "User explores product features and benefits",
                "items": [
                    {
                        "behavior": "Feature comparison",
                        "nudge": "Side-by-side feature comparison table",
                        "explanation": "Users need clear feature differentiation",
                        "frictionScore": 4,
                        "priority": 9,
                        "section": "Features"
                    }
                ]
            },
            {
                "index": 3,
                "stage": "Conversion",
                "observed": "User decides to take action",
                "items": [
                    {
                        "behavior": "Pricing evaluation",
                        "nudge": "Transparent pricing with no hidden fees",
                        "explanation": "Pricing clarity reduces purchase anxiety",
                        "frictionScore": 8,
                        "priority": 10,
                        "section": "Pricing"
                    },
                    {
                        "behavior": "Checkout process",
                        "nudge": "Streamlined 3-step checkout",
                        "explanation": "Complex checkout increases abandonment",
                        "frictionScore": 9,
                        "priority": 10,
                        "section": "Checkout"
                    }
                ]
            }
        ],
        "items": [
            {
                "behavior": "Checkout process",
                "nudge": "Streamlined 3-step checkout",
                "explanation": "Complex checkout increases abandonment",
                "frictionScore": 9,
                "priority": 10,
                "section": "Checkout"
            },
            {
                "behavior": "Pricing evaluation",
                "nudge": "Transparent pricing with no hidden fees",
                "explanation": "Pricing clarity reduces purchase anxiety",
                "frictionScore": 8,
                "priority": 10,
                "section": "Pricing"
            },
            {
                "behavior": "Feature comparison",
                "nudge": "Side-by-side feature comparison table",
                "explanation": "Users need clear feature differentiation",
                "frictionScore": 4,
                "priority": 9,
                "section": "Features"
            },
            {
                "behavior": "Hero section scan",
                "nudge": "Clear value proposition with CTA button",
                "explanation": "Users spend 2-3 seconds scanning hero section",
                "frictionScore": 3,
                "priority": 8,
                "section": "Hero"
            },
            {
                "behavior": "Navigation exploration",
                "nudge": "Simplified navigation with clear labels",
                "explanation": "Complex navigation increases cognitive load",
                "frictionScore": 6,
                "priority": 7,
                "section": "Navigation"
            }
        ]
    }
    return jsonify(demo_data)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("🚀 Starting Microbehavior Analyzer Demo...")
    print("📍 URL: http://localhost:5001")
    print("🔄 Press Ctrl+C to stop the server")
    print()
    app.run(debug=True, host='0.0.0.0', port=5001)
