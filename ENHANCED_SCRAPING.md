# Enhanced Scraping Capabilities

Your microbehaviour scraping stack has been significantly enhanced to provide **"best of the best" accuracy** for behavioral analysis and friction detection. Here's what's new:

## 🚀 What's Enhanced

### 1. **Hybrid Rendering (Automatic)**
- **Smart Detection**: Automatically detects when JavaScript rendering is needed
- **Performance Boost**: Uses fast `requests` for static pages, Playwright only when necessary
- **Heuristic Logic**: Detects SPAs, empty bodies, and JavaScript-heavy content

### 2. **Behavioral Interaction Tracking**
- **Click Analytics**: Position, timing, target elements, and text content
- **Scroll Depth**: Tracks how far users scroll on each page
- **Hover Behavior**: Dwell time and element targeting
- **Input Focus**: Form field interactions and completion rates
- **Rage Click Detection**: Identifies user frustration patterns

### 3. **Visual Context Preservation**
- **Full-Page Screenshots**: Captures complete page layout
- **DOM Snapshots**: Preserves exact HTML state
- **Performance Metrics**: Response times and loading performance
- **Viewport Context**: 1920x1080 desktop simulation

### 4. **Structured Content Extraction**
- **Main Content**: Uses `readability-lxml` for clean text extraction
- **Section Analysis**: Hero, features, pricing, CTAs, footer identification
- **Clickable Elements**: Buttons, links, forms with context
- **Trust Signals**: Testimonials, reviews, badges, security indicators
- **Content Metrics**: Word count, link density, form complexity

### 5. **Friction Pattern Analysis**
- **Scoring Algorithm**: 0-100 friction score (lower = more friction)
- **Performance Penalties**: Slow response times, JavaScript dependencies
- **Interaction Analysis**: Low engagement, rage clicks, poor scroll depth
- **Content Quality**: Short content, missing CTAs, lack of trust signals

### 6. **Site Graph Building**
- **Page Relationships**: Maps site structure and navigation flow
- **Behavioral Annotations**: Each page gets friction score and interaction data
- **Pattern Recognition**: Identifies site-wide friction trends
- **Export Capabilities**: JSON export for further analysis

## 🛠️ How to Use

### Install Dependencies
```bash
# Activate your virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install new dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### Command Line Interface

#### Test Enhanced Scraping
```bash
python -m microbehaviour.cli test-scraping --url "https://example.com"
```

#### Full Site Analysis
```bash
python -m microbehaviour.cli analyze-site \
  --url "https://example.com" \
  --max-pages 20 \
  --max-depth 2 \
  --output "analysis_results.json"
```

### Python API

#### Single Page Scraping
```python
from microbehaviour.scraper import fetch_html_hybrid

# Automatically chooses best scraping method
result = fetch_html_hybrid(
    "https://example.com",
    capture_screenshot=True,
    screenshot_dir="screenshots"
)

print(f"HTML length: {len(result.html)}")
print(f"Needs JavaScript: {result.needs_js}")
print(f"Response time: {result.response_time_ms}ms")
print(f"Screenshot: {result.screenshot_path}")
```

#### Full Site Crawling
```python
from microbehaviour.crawler import crawl_same_host_enhanced, analyze_friction_patterns

# Crawl site with behavioral tracking
site_graph = crawl_same_host_enhanced(
    start_url="https://example.com",
    max_pages=15,
    max_depth=2,
    capture_screenshots=True
)

# Analyze friction patterns
analysis = analyze_friction_patterns(site_graph)

print(f"High friction pages: {len(analysis['high_friction_pages'])}")
print(f"Performance issues: {len(analysis['performance_issues'])}")
print(f"Recommendations: {analysis['recommendations']}")
```

## 📊 What You Get

### Behavioral Data
```json
{
  "clicks": [
    {
      "timestamp": 1703123456789,
      "x": 150,
      "y": 200,
      "target": "BUTTON",
      "targetClass": "cta-button",
      "text": "Get Started"
    }
  ],
  "scrolls": [
    {
      "timestamp": 1703123456789,
      "depth": 75.5,
      "position": 1200
    }
  ],
  "rageClicks": [
    {
      "timestamp": 1703123456789,
      "x": 150,
      "y": 200,
      "count": 5
    }
  ]
}
```

### Friction Analysis
```json
{
  "high_friction_pages": [
    {
      "url": "https://example.com/checkout",
      "score": 25.0,
      "rank": 1
    }
  ],
  "performance_issues": [
    {
      "url": "https://example.com/dashboard",
      "response_time": 4500
    }
  ],
  "recommendations": [
    "High rage click rate detected - investigate UI responsiveness",
    "Many JavaScript-heavy pages - consider optimizing loading performance"
  ]
}
```

## 🎯 Use Cases

### 1. **Conversion Funnel Analysis**
- Identify where users drop off in the funnel
- Detect performance bottlenecks affecting conversions
- Map user behavior patterns through the journey

### 2. **UX Research & Testing**
- Compare different page versions for friction
- A/B test performance and engagement metrics
- Validate design changes with behavioral data

### 3. **Performance Optimization**
- Find slow-loading pages affecting user experience
- Identify JavaScript-heavy pages for optimization
- Track response time improvements over time

### 4. **Content Strategy**
- Analyze content engagement patterns
- Identify missing trust signals or CTAs
- Optimize content length and structure

### 5. **Competitive Analysis**
- Benchmark your site against competitors
- Identify industry best practices
- Find opportunities for differentiation

## 🔧 Configuration

### Screenshot Settings
```python
# Custom screenshot directory
result = fetch_html_hybrid(
    url,
    capture_screenshot=True,
    screenshot_dir="custom_screenshots"
)
```

### Browser Settings
```python
# Custom viewport and user agent
context = browser.new_context(
    viewport={'width': 1440, 'height': 900},
    user_agent="Custom User Agent",
    locale='en-GB',
    timezone_id='Europe/London'
)
```

### Crawling Limits
```python
# Respectful crawling with delays
site_graph = crawl_same_host_enhanced(
    start_url=url,
    max_pages=50,      # Maximum pages to crawl
    max_depth=3,       # Maximum link depth
    capture_screenshots=True
)
```

## 🚨 Best Practices

### 1. **Respectful Crawling**
- Use reasonable delays between requests
- Respect robots.txt and rate limits
- Don't overwhelm target servers

### 2. **Data Storage**
- Store raw HTML, screenshots, and behavioral data
- Export structured analysis for further processing
- Keep historical data for trend analysis

### 3. **Performance Monitoring**
- Monitor response times and success rates
- Track JavaScript vs static page ratios
- Analyze friction score trends over time

### 4. **Privacy & Compliance**
- Only crawl publicly accessible pages
- Don't capture sensitive user data
- Comply with website terms of service

## 🔍 Troubleshooting

### Common Issues

#### Playwright Not Installed
```bash
pip install playwright
playwright install
```

#### Screenshot Directory Issues
```python
# Ensure directory exists
from pathlib import Path
Path("screenshots").mkdir(exist_ok=True)
```

#### Memory Issues with Large Sites
```python
# Reduce page limits for large sites
site_graph = crawl_same_host_enhanced(
    start_url=url,
    max_pages=10,  # Start small
    max_depth=1
)
```

### Performance Tips

1. **Start Small**: Begin with 5-10 pages to test
2. **Monitor Resources**: Watch memory usage during large crawls
3. **Use Delays**: Add delays between requests to be respectful
4. **Export Regularly**: Save results periodically for large crawls

## 🎉 What's Next?

Your enhanced scraping stack now provides:
- ✅ **Human-like behavior simulation**
- ✅ **Visual context preservation**
- ✅ **Automatic method selection**
- ✅ **Comprehensive friction analysis**
- ✅ **Structured data extraction**
- ✅ **Site-wide pattern recognition**

This gives you the most accurate behavioral analysis possible for detecting user friction and optimizing conversion experiences!
