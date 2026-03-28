

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
