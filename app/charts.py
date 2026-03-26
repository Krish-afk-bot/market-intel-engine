import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import math

BG_COLOR      = "#0c0c0c"
CARD_COLOR    = "#111111"
ACCENT_COLOR  = "#f59e0b"
SUCCESS_COLOR = "#10b981"
WARNING_COLOR = "#f59e0b"
DANGER_COLOR  = "#ef4444"
TEXT_COLOR    = "#f5f5f5"
GRID_COLOR    = "#1c1c1c"
TEXT_DIM      = "#525252"
BORDER_COLOR  = "#262626"


base_layout = dict(
    paper_bgcolor=BG_COLOR,
    plot_bgcolor=CARD_COLOR,
    font=dict(color=TEXT_COLOR, family="IBM Plex Mono"),
    margin=dict(l=20, r=20, t=50, b=20),
    legend=dict(
        bgcolor=CARD_COLOR,
        bordercolor=BORDER_COLOR,
        borderwidth=1,
        font=dict(family="IBM Plex Mono", size=11),
    ),
)


def render_market_overview_chart(data: dict, key_suffix: str = "") -> None:
    """Horizontal bar chart showing 4 market metrics as scores."""
    metrics = data.get("market_metrics", {})
    

    maturity = metrics.get("market_maturity_score", 5)
    funding = metrics.get("funding_activity_score", 5)
    

    growth = metrics.get("growth_rate_percent")
    if growth is not None:
        growth_score = min(10, max(1, growth / 5))
    else:
        growth_score = 5
    

    size = metrics.get("estimated_size_billion")
    if size and size > 0:
        size_score = min(10, max(1, math.log10(size) + 1))
    else:
        size_score = 5
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=["Market Maturity", "Funding Activity", "Growth Rate", "Market Size"],
        x=[maturity, funding, growth_score, size_score],
        orientation='h',
        marker=dict(color=ACCENT_COLOR),
        text=[f"{maturity:.1f}", f"{funding:.1f}", f"{growth_score:.1f}", f"{size_score:.1f}"],
        textposition='outside'
    ))
    
    fig.update_layout(
        **base_layout,
        title=dict(text="MARKET METRICS OVERVIEW",
                   font=dict(family="Courier Prime, monospace", size=13, color=ACCENT_COLOR)),
        xaxis=dict(range=[0, 11], gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
        showlegend=False,
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"market_overview_{key_suffix}")


def render_trends_chart(data: dict, key_suffix: str = "") -> None:
    """Horizontal bar chart of trend momentum scores."""
    trends = data.get("trends", [])
    if not trends:
        st.info("No trend data available")
        return
    

    trends_sorted = sorted(trends, key=lambda x: x.get("momentum", 0), reverse=True)
    
    names = [t.get("name", "Unknown") for t in trends_sorted]
    momentums = [t.get("momentum", 0) for t in trends_sorted]
    directions = [t.get("direction", "stable") for t in trends_sorted]
    

    colors = []
    for d in directions:
        if d == "rising":
            colors.append(SUCCESS_COLOR)
        elif d == "declining":
            colors.append(DANGER_COLOR)
        else:
            colors.append(WARNING_COLOR)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=names,
        x=momentums,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{m:.1f}" for m in momentums],
        textposition='outside'
    ))
    
    fig.update_layout(
        **base_layout,
        title=dict(text="MARKET TREND MOMENTUM",
                   font=dict(family="Courier Prime, monospace", size=13, color=ACCENT_COLOR)),
        xaxis=dict(range=[0, 11], gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
        showlegend=False,
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"trends_{key_suffix}")
