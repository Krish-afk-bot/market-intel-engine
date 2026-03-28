

import json
import logging
import os
import re
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator import Orchestrator
from app.charts import render_all_charts

logging.basicConfig(level=logging.INFO)


BG_PRIMARY      = "#0c0c0c"
BG_SECONDARY    = "#111111"
BG_TERTIARY     = "#1a1a1a"
ACCENT_GOLD     = "#f59e0b"
ACCENT_GOLD_DIM = "#92400e"
SUCCESS         = "#10b981"
DANGER          = "#ef4444"
TEXT_PRIMARY    = "#f5f5f5"
TEXT_SECONDARY  = "#a3a3a3"
TEXT_DIM        = "#525252"
BORDER          = "#262626"
GRID_LINE       = "#1c1c1c"


st.set_page_config(
    page_title="MNI — Market Narrative Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


st.markdown(f"""
<style>
html, body, [class*="css"] {{
    background-color: {BG_PRIMARY};
    color: {TEXT_PRIMARY};
    font-family: 'IBM Plex Sans', sans-serif;
}}
.main .block-container {{
    background-color: {BG_PRIMARY};
    background-image: radial-gradient(circle, {BORDER} 1px, transparent 1px);
    background-size: 24px 24px;
    padding-top: 2rem;
    max-width: 1400px;
}}
[data-testid="stSidebar"] {{
    background-color: {BG_TERTIARY};
    border-right: 1px solid {BORDER};
}}
[data-testid="stSidebar"] .block-container {{ padding-top: 1.5rem; }}
h1, h2, h3 {{
    font-family: 'Courier Prime', monospace !important;
    color: {TEXT_PRIMARY} !important;
    letter-spacing: 0.05em;
}}
[data-testid="stTextInput"] input {{
    background-color: {BG_SECONDARY} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 0px !important;
    color: {TEXT_PRIMARY} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.9rem !important;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: {ACCENT_GOLD} !important;
    box-shadow: 0 0 0 1px {ACCENT_GOLD} !important;
}}
[data-testid="stPasswordInput"] input {{
    background-color: {BG_SECONDARY} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 0px !important;
    color: {TEXT_PRIMARY} !important;
    font-family: 'IBM Plex Mono', monospace !important;
}}
[data-testid="stButton"] > button {{
    background-color: {ACCENT_GOLD} !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 0px !important;
    font-family: 'Courier Prime', monospace !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
}}
[data-testid="stButton"] > button:hover {{
    background-color: #d97706 !important;
    box-shadow: 0 0 20px rgba(245,158,11,0.3) !important;
}}
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    background-color: {BG_SECONDARY};
    border-bottom: 1px solid {BORDER};
    gap: 0px;
    padding: 0;
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    background-color: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: {TEXT_SECONDARY};
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    padding: 0.75rem 1.25rem;
    text-transform: uppercase;
    transition: all 0.2s ease;
}}
[data-testid="stTabs"] [aria-selected="true"] {{
    background-color: transparent !important;
    border-bottom: 2px solid {ACCENT_GOLD} !important;
    color: {ACCENT_GOLD} !important;
}}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {{
    color: {TEXT_PRIMARY} !important;
    background-color: {BG_TERTIARY} !important;
}}
[data-testid="stMetric"] {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-left: 3px solid {ACCENT_GOLD};
    padding: 1rem 1.25rem;
}}
[data-testid="stMetric"] label {{
    color: {TEXT_SECONDARY} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}}
[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {TEXT_PRIMARY} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.6rem !important;
    font-weight: 500 !important;
}}
hr {{ border-color: {BORDER} !important; margin: 1rem 0 !important; }}
.stMarkdown h2 {{
    color: {ACCENT_GOLD} !important;
    font-family: 'Courier Prime', monospace !important;
    font-size: 1rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid {BORDER} !important;
    padding-bottom: 0.4rem !important;
    margin-top: 1.5rem !important;
}}
.stMarkdown h3 {{
    color: {TEXT_PRIMARY} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.9rem !important;
}}
.stMarkdown p {{
    color: {TEXT_SECONDARY} !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.95rem !important;
    line-height: 1.7 !important;
}}
.stMarkdown li {{
    color: {TEXT_SECONDARY} !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
}}
.stMarkdown strong {{ color: {TEXT_PRIMARY} !important; }}
[data-testid="stAlert"] {{
    border-radius: 0px !important;
    border-left: 3px solid {DANGER} !important;
    background-color: rgba(239,68,68,0.08) !important;
}}
[data-testid="stInfo"] {{
    border-radius: 0px !important;
    border-left: 3px solid {ACCENT_GOLD} !important;
    background-color: rgba(245,158,11,0.08) !important;
}}
[data-testid="stDownloadButton"] > button {{
    background-color: transparent !important;
    border: 1px solid {ACCENT_GOLD} !important;
    color: {ACCENT_GOLD} !important;
    border-radius: 0px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.05em !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    background-color: rgba(245,158,11,0.1) !important;
}}
[data-testid="stSelectbox"] > div > div {{
    background-color: {BG_SECONDARY} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 0px !important;
}}
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
header {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)



def safe_markdown(text: str) -> None:
    """Render markdown safely — escapes $ to prevent LaTeX rendering."""
    if not text:
        st.info("This section has no content.")
        return
    safe_text = re.sub(r'(?<!\\)\$', r'\\$', text)
    st.markdown(safe_text, unsafe_allow_html=False)


def show_error(error_type: str, detail: str = "") -> None:
    """Shows a user-friendly error with plain English explanation and specific action to take."""
    error_map = {
        "no_api_key": {
            "title": "API KEY REQUIRED",
            "message": "Enter your Groq API key in the sidebar to start analysis.",
            "action": "Get a free key at console.groq.com — takes 30 seconds.",
            "color": "#f59e0b"
        },
        "invalid_api_key": {
            "title": "INVALID API KEY",
            "message": "The Groq API key you entered was rejected.",
            "action": "Check that you copied the full key from console.groq.com/keys",
            "color": "#ef4444"
        },
        "rate_limit": {
            "title": "RATE LIMIT REACHED",
            "message": "Too many requests sent to Groq in a short time.",
            "action": "Wait 30-60 seconds and try again. Consider upgrading your Groq plan for higher limits.",
            "color": "#f59e0b"
        },
        "network_error": {
            "title": "NETWORK ERROR",
            "message": "Could not connect to data sources or the Groq API.",
            "action": "Check your internet connection and try again.",
            "color": "#ef4444"
        },
        "empty_market": {
            "title": "NO MARKET ENTERED",
            "message": "Enter a market name before starting analysis.",
            "action": "Try: Cybersecurity, FinTech, AI SaaS, Semiconductors",
            "color": "#f59e0b"
        },
        "market_too_short": {
            "title": "MARKET NAME TOO SHORT",
            "message": "The market name you entered is too vague to analyze.",
            "action": "Use at least 2 characters. Example: 'AI' or 'FinTech'",
            "color": "#f59e0b"
        },
        "sparse_data": {
            "title": "LIMITED DATA AVAILABLE",
            "message": "Very few results found for this market. Analysis may be less accurate.",
            "action": "Try a more specific market name. Example: instead of 'Tech' try 'Cloud Security' or 'AI SaaS'",
            "color": "#f59e0b"
        },
        "analysis_failed": {
            "title": "ANALYSIS FAILED",
            "message": f"Something went wrong during analysis.{' Details: ' + detail if detail else ''}",
            "action": "Try again. If the problem persists, check your API key and internet connection.",
            "color": "#ef4444"
        }
    }
    
    error = error_map.get(error_type, error_map["analysis_failed"])
    error["message"] = error["message"].replace("{detail}", detail)
    
    st.markdown(f"""
<div style="background-color: rgba(239,68,68,0.05);border: 1px solid rgba(239,68,68,0.15);
border-left: 3px solid {error['color']};padding: 1rem 1.25rem;margin: 0.5rem 0;">
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 0.75rem;color: {error['color']};
letter-spacing: 0.1em;margin-bottom: 0.4rem;">✗ {error['title']}</div>
<div style="font-family: 'IBM Plex Sans', sans-serif;font-size: 0.85rem;color: #a3a3a3;
margin-bottom: 0.5rem;line-height: 1.5;">{error['message']}</div>
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 0.72rem;color: #525252;">
→ {error['action']}</div>
</div>""", unsafe_allow_html=True)


def render_section_header(title: str, subtitle: str = "") -> None:
    st.markdown(f"""
<div style="border-bottom:1px solid {BORDER};padding-bottom:0.75rem;margin-bottom:1.25rem;">
<div style="font-family:'Courier Prime',monospace;font-size:1rem;color:{ACCENT_GOLD};
letter-spacing:0.1em;text-transform:uppercase;">{title}</div>
<div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.8rem;color:{TEXT_DIM};
margin-top:0.2rem;">{subtitle}</div>
</div>""", unsafe_allow_html=True)


def render_tldr_card(tldr: dict, market: str, generated_at: str) -> None:
    """Renders the TL;DR summary card. Appears above tabs, below metrics."""
    if not tldr:
        return
    
    sentiment = tldr.get("sentiment", "NEUTRAL")
    sentiment_color = {
        "BULLISH": "#10b981",
        "NEUTRAL": "#f59e0b",
        "BEARISH": "#ef4444"
    }.get(sentiment, "#f59e0b")
    
    difficulty = tldr.get("entry_difficulty", "MEDIUM")
    difficulty_color = {
        "LOW": "#10b981",
        "MEDIUM": "#f59e0b",
        "HIGH": "#ef4444",
        "VERY HIGH": "#ef4444"
    }.get(difficulty, "#f59e0b")
    
    companies = tldr.get("top_3_companies", [])
    companies_clean = [c for c in companies if c.strip()]
    companies_html = " · ".join([f'<span style="color:#f5f5f5">{c}</span>' for c in companies_clean])
    
    st.markdown(f"""
<div style="background-color: #111111;border: 1px solid #262626;border-top: 2px solid #f59e0b;
padding: 1.5rem;margin-bottom: 1.5rem;">
<!-- Header row -->
<div style="display: flex;justify-content: space-between;align-items: flex-start;margin-bottom: 1.25rem;
flex-wrap: wrap;gap: 0.5rem;">
<div>
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 0.6rem;color: #525252;
letter-spacing: 0.2em;text-transform: uppercase;margin-bottom: 0.25rem;">INTELLIGENCE BRIEF</div>
<div style="font-family: 'Courier Prime', monospace;font-size: 1.1rem;color: #f5f5f5;
letter-spacing: 0.05em;">{market.upper()}</div>
</div>
<div style="text-align: right;">
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 0.65rem;color: {sentiment_color};
letter-spacing: 0.1em;border: 1px solid {sentiment_color};padding: 0.2rem 0.6rem;display: inline-block;">
{sentiment}</div>
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 0.6rem;color: #525252;
margin-top: 0.3rem;">{generated_at}</div>
</div>
</div>
<!-- Metrics grid -->
<div style="display: grid;grid-template-columns: repeat(4, 1fr);gap: 1px;background-color: #262626;
margin-bottom: 1px;">
<div style="background-color: #111111;padding: 0.75rem 1rem;">
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 0.55rem;color: #525252;
letter-spacing: 0.15em;text-transform: uppercase;margin-bottom: 0.3rem;">MARKET SIZE</div>
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 1.1rem;color: #f5f5f5;font-weight: 500;">
{tldr.get("market_size", "—")}</div>
</div>
<div style="background-color: #111111;padding: 0.75rem 1rem;">
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 0.55rem;color: #525252;
letter-spacing: 0.15em;text-transform: uppercase;margin-bottom: 0.3rem;">GROWTH RATE</div>
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 1.1rem;color: #10b981;font-weight: 500;">
{tldr.get("growth_rate", "—")}</div>
</div>
<div style="background-color: #111111;padding: 0.75rem 1rem;">
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 0.55rem;color: #525252;
letter-spacing: 0.15em;text-transform: uppercase;margin-bottom: 0.3rem;">ENTRY DIFFICULTY</div>
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 1.1rem;color: {difficulty_color};
font-weight: 500;">{difficulty}</div>
<div style="font-family: 'IBM Plex Sans', sans-serif;font-size: 0.65rem;color: #525252;
margin-top: 0.2rem;line-height: 1.3;">{tldr.get("entry_difficulty_reason", "")}</div>
</div>
<div style="background-color: #111111;padding: 0.75rem 1rem;">
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 0.55rem;color: #525252;
letter-spacing: 0.15em;text-transform: uppercase;margin-bottom: 0.3rem;">TIME TO REVENUE</div>
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 1.1rem;color: #f5f5f5;font-weight: 500;">
{tldr.get("time_to_revenue", "—")}</div>
</div>
</div>
<!-- Second row -->
<div style="display: grid;grid-template-columns: 1fr 1fr;gap: 1px;background-color: #262626;
margin-bottom: 1px;">
<div style="background-color: #111111;padding: 0.75rem 1rem;">
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 0.55rem;color: #10b981;
letter-spacing: 0.15em;text-transform: uppercase;margin-bottom: 0.3rem;">▲ BEST OPPORTUNITY</div>
<div style="font-family: 'IBM Plex Sans', sans-serif;font-size: 0.9rem;color: #f5f5f5;">
{tldr.get("best_opportunity", "—")}</div>
</div>
<div style="background-color: #111111;padding: 0.75rem 1rem;">
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 0.55rem;color: #ef4444;
letter-spacing: 0.15em;text-transform: uppercase;margin-bottom: 0.3rem;">▼ BIGGEST RISK</div>
<div style="font-family: 'IBM Plex Sans', sans-serif;font-size: 0.9rem;color: #f5f5f5;">
{tldr.get("biggest_risk", "—")}</div>
</div>
</div>
<!-- Verdict row -->
<div style="background-color: #0c0c0c;padding: 0.75rem 1rem;border-top: 1px solid #262626;
display: flex;justify-content: space-between;align-items: center;flex-wrap: wrap;gap: 0.5rem;">
<div>
<span style="font-family: 'IBM Plex Mono', monospace;font-size: 0.6rem;color: #f59e0b;
letter-spacing: 0.1em;text-transform: uppercase;margin-right: 0.75rem;">VERDICT</span>
<span style="font-family: 'IBM Plex Sans', sans-serif;font-size: 0.85rem;color: #a3a3a3;
font-style: italic;">{tldr.get("verdict", "—")}</span>
</div>
<div style="font-family: 'IBM Plex Mono', monospace;font-size: 0.65rem;color: #525252;">
KEY PLAYERS: {companies_html}</div>
</div>
</div>
""", unsafe_allow_html=True)
