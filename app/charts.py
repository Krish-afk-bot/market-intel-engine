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


def render_skills_radar(data: dict, key_suffix: str = "") -> None:
    """Radar/spider chart of top 6 skills by demand score."""
    skills = data.get("skills", [])
    if not skills:
        st.info("No skills data available")
        return
    

    skills_sorted = sorted(skills, key=lambda x: x.get("demand_score", 0), reverse=True)[:6]
    
    names = [s.get("name", "Unknown") for s in skills_sorted]
    scores = [s.get("demand_score", 0) for s in skills_sorted]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=names,
        fill='toself',
        fillcolor=ACCENT_COLOR,
        opacity=0.3,
        line=dict(color=ACCENT_COLOR, width=2),
        marker=dict(size=8, color=ACCENT_COLOR)
    ))
    
    fig.update_layout(
        title=dict(text="SKILLS DEMAND RADAR",
                   font=dict(family="Courier Prime, monospace", size=13, color=ACCENT_COLOR)),
        height=450,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickfont=dict(size=9, color=TEXT_COLOR),
                gridcolor=GRID_COLOR,
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color=TEXT_COLOR),
                gridcolor=GRID_COLOR,
            ),
            bgcolor=CARD_COLOR,
        ),
        showlegend=False,
        **base_layout,
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"skills_radar_{key_suffix}")


def render_risk_matrix(data: dict, key_suffix: str = "") -> None:
    """Scatter plot: x=probability, y=impact, text=risk name."""
    risks = data.get("risks", [])
    if not risks:
        st.info("No risk data available")
        return
    
    names = [r.get("name", "Unknown") for r in risks]
    probabilities = [r.get("probability", 5) for r in risks]
    impacts = [r.get("impact", 5) for r in risks]
    
    fig = go.Figure()
    

    fig.add_shape(type="rect", x0=0, y0=5, x1=5, y1=10,
                  fillcolor="rgba(16, 185, 129, 0.1)", line_width=0)  # Low prob, high impact
    fig.add_shape(type="rect", x0=5, y0=5, x1=10, y1=10,
                  fillcolor="rgba(239, 68, 68, 0.2)", line_width=0)  # High prob, high impact
    fig.add_shape(type="rect", x0=0, y0=0, x1=5, y1=5,
                  fillcolor="rgba(16, 185, 129, 0.2)", line_width=0)  # Low prob, low impact
    fig.add_shape(type="rect", x0=5, y0=0, x1=10, y1=5,
                  fillcolor="rgba(245, 158, 11, 0.1)", line_width=0)  # High prob, low impact
    

    fig.add_hline(y=5, line_dash="dash", line_color=GRID_COLOR, line_width=1)
    fig.add_vline(x=5, line_dash="dash", line_color=GRID_COLOR, line_width=1)
    

    fig.add_trace(go.Scatter(
        x=probabilities,
        y=impacts,
        mode='markers+text',
        marker=dict(size=15, color=DANGER_COLOR),
        text=names,
        textposition='top center',
        textfont=dict(size=10, color=TEXT_COLOR),
        hovertemplate='<b>%{text}</b><br>Probability: %{x}<br>Impact: %{y}<extra></extra>'
    ))
    

    annotations = [
        dict(x=2.5, y=8.5, text="Monitor",
             font=dict(size=13, color="white", family="Space Mono"),
             showarrow=False,
             bgcolor="rgba(245,158,11,0.4)",
             borderpad=6),
        dict(x=8, y=8.5, text="Critical",
             font=dict(size=13, color="white", family="Space Mono"),
             showarrow=False,
             bgcolor="rgba(239,68,68,0.5)",
             borderpad=6),
        dict(x=2.5, y=2, text="Accept",
             font=dict(size=13, color="white", family="Space Mono"),
             showarrow=False,
             bgcolor="rgba(16,185,129,0.4)",
             borderpad=6),
        dict(x=8, y=2, text="Manage",
             font=dict(size=13, color="white", family="Space Mono"),
             showarrow=False,
             bgcolor="rgba(59,130,246,0.4)",
             borderpad=6),
    ]
    
    fig.update_layout(
        **base_layout,
        title=dict(text="RISK ASSESSMENT MATRIX",
                   font=dict(family="Courier Prime, monospace", size=13, color=ACCENT_COLOR)),
        xaxis=dict(title="Probability", range=[0, 10], gridcolor=GRID_COLOR),
        yaxis=dict(title="Impact", range=[0, 10], gridcolor=GRID_COLOR),
        annotations=annotations,
        showlegend=False,
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"risk_matrix_{key_suffix}")

