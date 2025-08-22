## Microbehavior Extraction & Analysis (Python + Streamlit)

This project scrapes page content, cleans it, and sends it to an LLM to extract UX insights and hypothesized microbehaviors. Includes a Streamlit UI and a CLI.

### Quickstart

1) Create a virtual environment in this project and install deps:

```bash
cd "$(dirname "$0")"
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

2) Set your OpenAI API key (or use a `.env` file):

```bash
export OPENAI_API_KEY=YOUR_KEY
# or copy .env.example → .env and set it there
```

3) Run the Streamlit app:

```bash
. .venv/bin/activate
streamlit run app/streamlit_app.py
```

4) Or run once via CLI:

```bash
. .venv/bin/activate
python -m microbehaviour.cli experience --url https://example.com
```

### User Journey Analysis

The library now includes specialized functionality for analyzing user journeys and conversion funnels. This is particularly useful for understanding how users move through your website from landing to conversion.

#### What It Analyzes

The user journey analysis maps out the 9-step conversion funnel pattern:

1. **Landing** - User arrives via ad, social link, or referral
2. **Headline** - User reads main headline + subheadline
3. **Credibility** - User glances at credibility elements (logos, revenue, success rate)
4. **Process** - User understands the framework ("How It Works")
5. **Social Proof** - User reviews testimonials and case studies
6. **Pricing** - User checks pricing table and compares features
7. **CTA** - User clicks conversion buttons
8. **Form** - User fills out booking/contact forms
9. **Confirmation** - User confirms calendar slots or completes action

#### Usage Examples

**Command Line:**
```bash
# Analyze user journey and conversion funnel
python -m microbehaviour.cli journey --url https://example.com --max-pages 5

# Analyze user experience (original functionality)
python -m microbehaviour.cli experience --url https://example.com --goal "Book a call"
```

**Python Script:**
```python
from microbehaviour.analysis import analyze_user_journey

# Analyze a website's conversion funnel
report = analyze_user_journey("https://example.com", max_pages=3, max_depth=1)

# Access journey insights
print(f"Found {report.total_steps} journey steps")
print(f"Primary goal: {report.primary_goal}")
print(f"Journey complexity: {report.journey_complexity}")

# Examine each step
for step in report.journey_steps:
    print(f"Step {step.step_number}: {step.step_name}")
    print(f"Description: {step.description}")
    print(f"Friction points: {step.friction_points}")
    print(f"Optimization suggestions: {step.optimization_suggestions}")
```

**Example Script:**
```bash
# Run the interactive example
python example_journey_analysis.py
```

#### Output Structure

The analysis returns a `UserJourneyReport` with:

- **Journey Steps**: Detailed breakdown of each step with content elements, user actions, and friction points
- **Journey Insights**: Overall funnel type, complexity, and optimization priorities
- **Key Moments of Truth**: Critical decision points in the user journey
- **Optimization Priorities**: Top areas to improve for better conversion

### Notes

- The scraper defaults to static fetch with `requests + BeautifulSoup`. Dynamic rendering (Playwright/Selenium) can be added later if needed.
- The LLM returns structured JSON with hypothesized microbehaviors, hesitation level, friction points, and recommendations.
- User journey analysis is optimized for conversion-focused websites and landing pages.





