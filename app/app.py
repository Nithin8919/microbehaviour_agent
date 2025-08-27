import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template
from microbehaviour.analysis import analyze_user_journey, analyze_granular_actions
import json
import logging

# Load environment variables from .env file
print("=== ENVIRONMENT SETUP ===")
try:
    from dotenv import load_dotenv
    import os
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for .env file...")
    
    # Try to load .env from current directory and parent directory
    env_loaded = load_dotenv()
    if not env_loaded:
        env_loaded = load_dotenv(dotenv_path="../.env")
    
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"✓ .env file loaded: {env_loaded}")
    print(f"✓ OpenAI API Key status: {'SET' if api_key else 'NOT SET'}")
    if api_key:
        print(f"✓ API Key length: {len(api_key)}")
        print(f"✓ API Key preview: {api_key[:10]}...")
    else:
        print("✗ No OpenAI API Key found - analysis will fail!")
        
except ImportError:
    print("✗ python-dotenv not installed, using system environment variables")
print("=== END ENVIRONMENT SETUP ===\n")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')

# Initialize Flask app with explicit template folder
app = Flask(__name__, template_folder=template_dir)

# Log template directory for debugging
print(f"=== FLASK APP SETUP ===")
print(f"Current directory: {current_dir}")
print(f"Template directory: {template_dir}")
print(f"Template directory exists: {os.path.exists(template_dir)}")
print(f"Template files: {os.listdir(template_dir) if os.path.exists(template_dir) else 'N/A'}")
print("=== END FLASK APP SETUP ===\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        logger.info("=== NEW ANALYZE REQUEST ===")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        url = data.get('url')
        goal = data.get('goal')
        
        logger.info(f"URL: {url}, Goal: {goal}")
        
        if not url:
            logger.error("URL is required but not provided")
            return jsonify({'error': 'URL is required'}), 400
        
        # Check if OpenAI API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        logger.info(f"API Key present: {'Yes' if api_key else 'No'}")
        
        if not api_key:
            logger.error("OpenAI API key not configured")
            return jsonify({
                'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.',
                'details': 'The analysis requires an OpenAI API key to function. Please check your configuration.'
            }), 500
        
        logger.info(f"Starting analysis for URL: {url}")
        
        # Analyze the user journey with default parameters
        report = analyze_user_journey(url)
        logger.info(f"Analysis completed, generating response...")
        
        report_dict = report.model_dump()
        
        # Add the goal to the response for context
        report_dict['goal'] = goal
        
        logger.info(f"Analysis completed successfully for {url}")
        logger.info(f"Report has {len(report_dict.get('journey_steps', []))} journey steps")
        
        return jsonify({
            'success': True,
            'data': report_dict
        })
        
    except RuntimeError as e:
        logger.error(f"Runtime error during analysis: {e}", exc_info=True)
        if "OPENAI_API_KEY not set" in str(e):
            return jsonify({
                'error': 'OpenAI API key not configured',
                'details': 'Please set the OPENAI_API_KEY environment variable to use this service.'
            }), 500
        else:
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/analyze-granular', methods=['POST'])
def analyze_granular():
    """Endpoint for granular step-by-step action analysis"""
    try:
        logger.info("=== NEW GRANULAR ANALYZE REQUEST ===")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        url = data.get('url')
        goal = data.get('goal')
        
        logger.info(f"URL: {url}, Goal: {goal}")
        
        if not url:
            logger.error("URL is required but not provided")
            return jsonify({'error': 'URL is required'}), 400
        
        # Check if OpenAI API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        logger.info(f"API Key present: {'Yes' if api_key else 'No'}")
        
        if not api_key:
            logger.error("OpenAI API key not configured")
            return jsonify({
                'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.',
                'details': 'The granular analysis requires an OpenAI API key to function. Please check your configuration.'
            }), 500
        
        logger.info(f"Starting granular action analysis for URL: {url}")
        
        # Analyze the granular actions with default parameters
        report = analyze_granular_actions(url, goal=goal)
        logger.info(f"Granular analysis completed, generating response...")
        
        report_dict = report.model_dump()
        
        logger.info(f"Granular analysis completed successfully for {url}")
        logger.info(f"Report has {len(report_dict.get('action_sequence', []))} action steps")
        
        return jsonify({
            'success': True,
            'data': report_dict
        })
        
    except RuntimeError as e:
        logger.error(f"Runtime error during granular analysis: {e}", exc_info=True)
        if "OPENAI_API_KEY not set" in str(e):
            return jsonify({
                'error': 'OpenAI API key not configured',
                'details': 'Please set the OPENAI_API_KEY environment variable to use this service.'
            }), 500
        else:
            return jsonify({'error': f'Granular analysis failed: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Unexpected error during granular analysis: {e}", exc_info=True)
        return jsonify({'error': f'Granular analysis failed: {str(e)}'}), 500

@app.route('/demo-data')
def demo_data():
    """Return sample demo data for the user journey analysis"""
    # Use a real example URL for demo
    try:
        # Check if OpenAI API key is available
        if not os.getenv('OPENAI_API_KEY'):
            return jsonify({
                'error': 'OpenAI API key not configured',
                'details': 'Demo data requires an OpenAI API key to function. Please check your configuration.',
                'url': 'https://www.apple.com',
                'goal': 'Increase conversions',
                'journey_steps': [],
                'total_steps': 0,
                'conversion_funnel_type': 'Demo (API Key Required)',
                'primary_goal': 'Demo Analysis',
                'journey_complexity': 'Demo',
                'key_moments_of_truth': [],
                'optimization_priorities': []
            }), 500
        
        demo_url = "https://www.apple.com"  # Use a well-known site that should work
        goal = "Increase conversions"
        
        logger.info(f"Starting demo analysis for URL: {demo_url}")
        
        report = analyze_user_journey(demo_url)
        report_dict = report.model_dump()
        report_dict['goal'] = goal
        
        logger.info(f"Demo analysis completed successfully")
        
        return jsonify(report_dict)
    except RuntimeError as e:
        if "OPENAI_API_KEY not set" in str(e):
            logger.error("Demo failed: OpenAI API key not set")
            return jsonify({
                'error': 'OpenAI API key not configured',
                'details': 'Demo data requires an OpenAI API key to function.',
                'url': 'https://www.apple.com',
                'goal': 'Increase conversions',
                'journey_steps': [],
                'total_steps': 0,
                'conversion_funnel_type': 'Demo (API Key Required)',
                'primary_goal': 'Demo Analysis',
                'journey_complexity': 'Demo',
                'key_moments_of_truth': [],
                'optimization_priorities': []
            }), 500
        else:
            logger.error(f"Demo failed with runtime error: {e}")
            return jsonify({
                'error': f'Demo analysis failed: {str(e)}',
                'url': 'https://www.apple.com',
                'goal': 'Increase conversions',
                'journey_steps': [],
                'total_steps': 0,
                'conversion_funnel_type': 'Demo (Error)',
                'primary_goal': 'Demo Analysis',
                'journey_complexity': 'Demo',
                'key_moments_of_truth': [],
                'optimization_priorities': []
            }), 500
    except Exception as e:
        logger.error(f"Demo failed with unexpected error: {e}")
        # Fallback to minimal demo structure if analysis fails
        return jsonify({
            'error': f'Demo analysis failed: {str(e)}',
            'url': 'https://www.apple.com',
            'goal': 'Increase conversions',
            'journey_steps': [],
            'total_steps': 0,
            'conversion_funnel_type': 'Demo (Error)',
            'primary_goal': 'Demo Analysis',
            'journey_complexity': 'Demo',
            'key_moments_of_truth': [],
            'optimization_priorities': []
        }), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/test')
def test():
    """Simple test endpoint to verify the backend is working"""
    return jsonify({
        'status': 'working',
        'message': 'Backend is running successfully',
        'timestamp': time.time()
    })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5003)
