from __future__ import annotations

import os
from typing import Any, List

import pandas as pd
import streamlit as st

from microbehaviour.analysis import analyze_user_journey


st.set_page_config(page_title="User Journey Analyzer", page_icon="🔄", layout="wide")
st.title("🔄 User Journey Analysis & Conversion Funnel Mapping")
st.caption("Crawl → Map journey steps → Identify conversion patterns → Optimization insights")


with st.sidebar:
    st.header("Settings")
    st.caption("API key is read from your .env (OPENAI_API_KEY)")
    model_name = st.text_input("Model", value="gpt-4o-mini")
    max_pages = st.slider("Max pages to crawl", 1, 10, 3)
    max_depth = st.slider("Max crawl depth", 1, 3, 1)
    st.markdown("""
    - Analyzes conversion funnel patterns
    - Maps user journey steps
    - Identifies friction points and optimization opportunities
    """)


url = st.text_input("Website URL", placeholder="https://example.com")
analyze_clicked = st.button("Analyze User Journey")


def render_journey_step(step: dict[str, Any]) -> None:
    """Render a single journey step with all its details."""
    st.markdown(f"#### 📋 Step {step['step_number']}: {step['step_name']}")
    st.markdown(f"**Description:** {step['description']}")
    
    # Content elements
    if step.get('content_elements'):
        st.markdown(f"**Content elements:** {', '.join(step['content_elements'])}")
    
    # User actions
    if step.get('user_actions'):
        st.markdown(f"**User actions:** {', '.join(step['user_actions'])}")
    
    # Conversion indicators
    if step.get('conversion_indicators'):
        st.markdown(f"**Conversion indicators:** {', '.join(step['conversion_indicators'])}")
    
    # Friction points
    if step.get('friction_points'):
        st.markdown(f"⚠️ **Friction points:** {', '.join(step['friction_points'])}")
    
    # Optimization suggestions
    if step.get('optimization_suggestions'):
        st.markdown(f"💡 **Optimization suggestions:** {', '.join(step['optimization_suggestions'])}")
    
    st.divider()


if analyze_clicked and url:
    try:
        with st.spinner("🔍 Analyzing user journey (crawl + LLM analysis)..."):
            report = analyze_user_journey(url, max_pages, max_depth)
        report_dict = report.model_dump()

        # Header summary
        st.subheader("🎯 Journey Analysis Overview")
        cols = st.columns(4)
        with cols[0]:
            st.metric(label="Total Steps", value=report_dict.get("total_steps", 0))
        with cols[1]:
            st.metric(label="Primary Goal", value=report_dict.get("primary_goal", "N/A"))
        with cols[2]:
            st.metric(label="Funnel Type", value=report_dict.get("conversion_funnel_type", "N/A"))
        with cols[3]:
            st.metric(label="Complexity", value=report_dict.get("journey_complexity", "N/A"))

        # Main content tabs
        tab_journey, tab_insights, tab_raw = st.tabs(["Journey Steps", "Key Insights", "Raw Data"])

        with tab_journey:
            st.markdown("### 🔄 User Journey Steps")
            st.markdown("Detailed breakdown of each step in the conversion funnel:")
            
            for step in report_dict.get("journey_steps", []):
                render_journey_step(step)

        with tab_insights:
            # Key moments of truth
            if report_dict.get("key_moments_of_truth"):
                st.markdown("### 🎯 Key Moments of Truth")
                st.markdown("Critical decision points in the user journey:")
                for moment in report_dict["key_moments_of_truth"]:
                    st.markdown(f"• {moment}")
                st.divider()
            
            # Optimization priorities
            if report_dict.get("optimization_priorities"):
                st.markdown("### 🚀 Optimization Priorities")
                st.markdown("Priority areas for improving conversion:")
                for priority in report_dict["optimization_priorities"]:
                    st.markdown(f"• {priority}")
                st.divider()
            
            # Journey complexity analysis
            complexity = report_dict.get("journey_complexity", "Medium")
            st.markdown(f"### 📊 Journey Complexity: {complexity}")
            if complexity == "Simple":
                st.success("Simple journey - users can convert quickly with minimal steps")
            elif complexity == "Medium":
                st.warning("Medium complexity - balanced journey with some decision points")
            else:
                st.info("Complex journey - multiple decision points and considerations")

        with tab_raw:
            st.json(report_dict)

    except Exception as exc:  # noqa: BLE001
        st.error(f"❌ Error during analysis: {exc}")
        st.info("💡 Make sure your OPENAI_API_KEY is set in your .env file")


