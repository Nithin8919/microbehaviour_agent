#!/usr/bin/env python3
"""
Main entry point for the Microbehaviour Backend API
"""

import os
from flask import Flask, request, jsonify
from microbehaviour.analysis import analyze_user_journey
from microbehaviour.scraper import scrape_website
from microbehaviour.llm import get_llm_analysis

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "microbehaviour-backend"})

@app.route('/api/analyze', methods=['POST'])
def analyze_endpoint():
    """Analyze user journey data"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        # Scrape the website
        scraped_data = scrape_website(url)
        
        # Analyze the journey
        analysis = analyze_user_journey(scraped_data)
        
        return jsonify({
            "url": url,
            "analysis": analysis,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/scrape', methods=['POST'])
def scrape_endpoint():
    """Scrape website data"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        # Scrape the website
        scraped_data = scrape_website(url)
        
        return jsonify({
            "url": url,
            "data": scraped_data,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
