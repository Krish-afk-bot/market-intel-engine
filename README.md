<div align="center">

# 🎯 Market Narrative Intelligence (MNI)

**AI-powered market research that runs in minutes, not days**

*Multi-agent system that collects live data, analyzes markets in parallel, and self-refines reports before delivery*

<br/>

![Status](https://img.shields.io/badge/Status-Active%20MVP-brightgreen?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![LLM](https://img.shields.io/badge/LLM-Groq%20Llama--3.1--8b-orange?style=flat-square)
![UI](https://img.shields.io/badge/UI-Streamlit-red?style=flat-square&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

[Quick Start](#-quick-start) • [Features](#-key-features) • [Architecture](#-system-architecture) • [Roadmap](#-mvp-roadmap)

</div>

---

## 🧭 Mission

Make professional-grade market intelligence accessible to everyone — founders, analysts, students, and researchers — without expensive subscriptions or manual data collection. MNI uses coordinated AI agents and real-time public data to generate structured reports grounded in actual sources, not hallucinations.

---

## 🔴 The Challenge

Traditional market research is:
- **Slow**: Analysts spend 4-8 hours manually collecting data from news sites, job boards, Wikipedia, and forums
- **Fragmented**: Information scattered across dozens of sources with no unified view
- **Expensive**: Professional reports cost $500-$5,000 per market
- **Stale**: By the time a report is finished, parts are already outdated

Existing AI tools either:
- Summarize a single source (limited scope)
- Generate confident-sounding text with no real data backing (hallucinations)
- Require manual prompt engineering for each section (not automated)

---

## ✅ Our Solution

MNI runs an **8-stage autonomous pipeline** with specialized AI agents:

1. **Research Agent** — Fetches live data from DuckDuckGo, Wikipedia, and HackerNews (no LLM calls)
2. **Market + Capability Agents** — Run in parallel via ThreadPoolExecutor to analyze market dynamics and required skills
3. **Strategy Agent** — Synthesizes entry paths, opportunities, and risks
4. **Critic Agent** — Reviews all sections for weak claims and contradictions, provides structured feedback
5. **Refinement Loop** — Automatically reruns flagged sections with critic's improvement instructions
6. **Visualization Agent** — Extracts chart-ready JSON for 7 interactive Plotly visualizations
7. **TL;DR Agent** — Generates executive summary card with key metrics and verdict

Every section is grounded in data collected at runtime. No hardcoded content. No simulated results.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **7 Specialized Agents** | Each agent has one job: research, market analysis, capability mapping, strategy, critique, refinement, visualization, or executive summary |
| ⚡ **Parallel Execution** | Market and Capability agents run concurrently, cutting pipeline time by ~40% |
| 🔄 **Self-Refinement Loop** | Critic agent scores each section (1-10); sections scoring <7 are automatically rewritten with specific improvement instructions |
| 🎯 **TL;DR Summary Card** | Executive brief with market size, growth rate, entry difficulty, time-to-revenue, best opportunity, biggest risk, and verdict |
| 🔍 **Market Disambiguation** | Vague inputs like "trading" or "AI" are automatically clarified before search to avoid irrelevant results |
| 💾 **SHA-256 LLM Cache** | Identical prompts served from memory — no duplicate API calls within a session |
| 📊 **7 Interactive Charts** | Market metrics, trend momentum, skills radar, risk matrix, quality gauges, learning timeline, key players |
| 🖥️ **Intelligence War Room UI** | Dark obsidian theme with amber accents, real-time pipeline progress, inline charts in tabs |
| 💻 **CLI Runner** | Headless mode for scripting, automation, or CI pipelines |
| 📥 **Export Options** | Download full report as Markdown or research data separately |
| ⏱️ **Timestamp Tracking** | Every report shows generation time, data freshness, sources fetched, and refinement count |
| 🎨 **Inline Visualizations** | Charts embedded directly in relevant tabs (trends in Market, skills in Capabilities, risks in Strategy) |

---

## ⚙️ How It Works

```
Input: "Cybersecurity"
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 1 — Research Agent                               │
│  Fetches live data from DuckDuckGo, Wikipedia,          │
│  and HackerNews. No LLM calls — pure data collection.   │
│  Stores everything in shared AgentMemory.               │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌─────────────────┐             ┌─────────────────────┐
│  Stage 2a       │             │  Stage 2b            │
│  Market Agent   │  PARALLEL   │  Capability Agent    │
│  Market size,   │◄──────────►│  Skills, tools,      │
│  players,       │             │  salaries, hiring    │
│  funding,       │             │  trends, learning    │
│  disruption     │             │  roadmap             │
└────────┬────────┘             └──────────┬──────────┘
         └───────────────┬─────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 3 — Strategy Agent                               │
│  Synthesizes market-entry plan from both analyses.      │
│  Identifies entry paths, risks, and unfair advantages.  │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 4 — Critic Agent (Backend Only)                  │
│  Reviews all sections for contradictions and weak       │
│  claims. Returns structured JSON feedback with scores.  │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 5 — Refinement Loop                              │
│  Automatically reruns agents for sections scoring <7.   │
│  Injects critic's improvement instructions into prompt. │
│  User never sees critic feedback — only improved output.│
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 6 — Visualization Agent                          │
│  Makes one LLM call to extract chart-ready JSON         │
│  from the full report for all 7 Plotly charts.          │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 7 — TL;DR Agent                                  │
│  Generates executive summary card with key metrics,     │
│  verdict, sentiment, and top 3 companies.               │
└────────────────────────┬────────────────────────────────┘
                         ▼
              Output: Structured Report
              + TL;DR Summary Card
              + 7 Interactive Charts
              + Markdown Export
```

---

## 🏗️ System Architecture

```
market-narrative-intelligence/
│
├── agents/
│   ├── base_agent.py          # Abstract base: cache-aware LLM call + memory helpers
│   ├── research_agent.py      # Stage 1: live data collection (no LLM)
│   ├── market_agent.py        # Stage 2a: market size, players, funding, disruption
│   ├── capability_agent.py    # Stage 2b: skills, tools, salaries, hiring trends
│   ├── strategy_agent.py      # Stage 3: market-entry strategy synthesis
│   ├── critic_agent.py        # Stage 4: quality review with structured JSON feedback
│   ├── visualization_agent.py # Stage 6: chart-ready JSON extraction
│   └── tldr_agent.py          # Stage 7: executive summary card generation
│
├── app/
│   ├── streamlit_app.py       # Intelligence War Room UI (dark theme, inline charts)
│   └── charts.py              # 7 Plotly chart functions + render_all_charts()
│
├── core/
│   ├── orchestrator.py        # 8-stage pipeline coordinator (ThreadPoolExecutor)
│   ├── cache.py               # SHA-256 in-memory LLM response cache
│   └── memory.py              # Shared key-value store for inter-agent communication
│
├── llm/
│   └── groq_client.py         # Groq API wrapper (call tracking + token counting)
│
├── mcp/
│   └── tools.py               # Tool dispatcher: DuckDuckGo, Wikipedia, HackerNews
│
├── .env.example               # Environment variable template
├── requirements.txt           # Python dependencies
└── run_analysis.py            # CLI runner (argparse, markdown/json output)
```

**Key Design Decisions:**

- **Agent Isolation**: Agents communicate exclusively through `AgentMemory` — no direct agent-to-agent calls
- **Cache Strategy**: LLM responses cached via SHA-256 hash of prompt+system; tool calls never cached (always fresh data)
- **Parallel Stage 2**: Market and Capability agents run concurrently via `ThreadPoolExecutor` to reduce total pipeline time
- **Backend-Only Critic**: Critic feedback and refinement details never shown to user — only the improved final report
- **Single Orchestrator**: Only `Orchestrator` knows the pipeline order; agents are stateless and reusable

---

## 🗺️ User Journey

| Step | Action | What Happens |
|------|--------|--------------|
| 1 | Open dashboard | Intelligence War Room UI loads at `localhost:8501` |
| 2 | Enter market name | Type "Cybersecurity" or click suggested market button |
| 3 | Click **INITIATE ANALYSIS** | 8-stage pipeline starts; real-time progress updates |
| 4 | View TL;DR card | Executive summary with market size, growth, difficulty, verdict |
| 5 | Read sections | **Research**, **Market**, **Capabilities**, **Strategy** tabs |
| 6 | Explore inline charts | Trends in Market tab, skills radar in Capabilities, risk matrix in Strategy |
| 7 | View all charts | **Charts Overview** tab shows all 7 visualizations together |
| 8 | Check full report | **Full Report** tab shows complete Markdown document |
| 9 | Export | Download as `.md` with one click |

---

## 🛠️ Technology Stack

### AI & LLM

| Component | Technology | Notes |
|-----------|------------|-------|
| LLM Provider | [Groq](https://console.groq.com) | Free tier: 14,400 requests/day |
| Model | `llama-3.1-8b-instant` | Fast inference, high rate limits |
| Temperature | `0.3` | Low for factual, consistent output |
| Max Tokens | `2048` per call | Per agent call |

### Data Sources *(all free, no API keys required)*

| Source | Used For | API |
|--------|----------|-----|
| DuckDuckGo Search | Market size, news, skills, tools, salaries, hiring data | `duckduckgo-search` library |
| Wikipedia | Background context and industry overviews | `wikipedia` library |
| HackerNews | Developer sentiment and trending discussions | Algolia public API |

### Application Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Web UI | Streamlit 1.35+ | Intelligence War Room dashboard |
| Charts | Plotly 5.18+ | 7 interactive visualizations |
| Concurrency | Python `ThreadPoolExecutor` | Parallel Stage 2 execution |
| Caching | SHA-256 in-memory | Custom `SimpleCache` for LLM responses |
| HTTP | `requests` library | API calls to HackerNews |
| Environment | `python-dotenv` | `.env` file management |

---

## 🚀 Quick Start

**Requirements:** Python 3.10+, a free [Groq API key](https://console.groq.com)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/market-narrative-intelligence.git
cd market-narrative-intelligence
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your API key

```bash
cp .env.example .env
```

Open `.env` and set your key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the web dashboard

```bash
python -m streamlit run app/streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### 5. Or use the CLI

```bash
# Output to terminal (Markdown)
python run_analysis.py "Cybersecurity"

# Save as Markdown file
python run_analysis.py "FinTech" --output report.md

# Save as JSON
python run_analysis.py "AI SaaS" --format json --output report.json
```

---

## 🎨 UI Features

### Intelligence War Room Theme
- **Obsidian black background** (`#0c0c0c`) with dot-grid texture
- **Amber/gold accents** (`#f59e0b`) for highlights and borders
- **Typography**: Courier Prime (headings), IBM Plex Sans (body), IBM Plex Mono (metrics)
- **Custom metric cards** with amber top borders (no default Streamlit metrics)
- **Animated pipeline progress** with stage numbers `[00]` through `[07]`

### TL;DR Summary Card
Appears immediately after metrics row, before tabs:
- Market size and growth rate
- Entry difficulty with explanation
- Time to revenue estimate
- Best opportunity and biggest risk
- Opinionated verdict
- Sentiment badge (BULLISH/NEUTRAL/BEARISH)
- Top 3 key players

### Inline Charts
Charts embedded directly in relevant tabs:
- **Market Analysis tab**: Trend momentum chart
- **Capabilities tab**: Skills radar + learning timeline (2 columns)
- **Strategy tab**: Risk matrix + company relevance (2 columns)
- **Charts Overview tab**: All 7 charts in one view

### Error Handling
8 error types with clear explanations and actionable guidance:
- API key required/invalid
- Rate limit reached
- Network error
- Empty/too short market name
- Analysis failed

---

## 🤝 Contributing

Contributions are welcome! A few guidelines to keep the codebase clean:

### Core Principles
- **One agent, one job**: Each agent reads from and writes to `AgentMemory`. Agents must not call other agents directly.
- **No hardcoded data**: All data must come from live tool calls in `mcp/tools.py`.
- **Keep the pipeline order**: The 8-stage sequence in `core/orchestrator.py` is intentional — don't reorder stages without understanding memory dependencies.
- **Test with real markets**: Before opening a PR, run the full pipeline against at least one market and verify output quality.

### Development Workflow

```bash
# Fork → branch → commit → PR
git checkout -b feature/your-feature-name
git commit -m "feat: describe your change"
# Open a pull request against main
```

### Testing

```bash
# Run a full analysis to test changes
python run_analysis.py "test market" --output test_report.md

# Or use the dashboard
python -m streamlit run app/streamlit_app.py
```

---

## 📊 Example Output

**Input:** `"Cybersecurity"`

**TL;DR Card:**
- Market Size: $190B
- Growth Rate: 12% CAGR
- Entry Difficulty: HIGH (Requires deep technical expertise and security certifications)
- Time to Revenue: 12-18 months
- Best Opportunity: Cloud security for SMB segment
- Biggest Risk: Regulatory compliance complexity
- Verdict: Attractive for well-funded teams with domain expertise — avoid if bootstrapping
- Sentiment: BULLISH
- Key Players: CrowdStrike · Palo Alto Networks · Fortinet

**Report Sections:**
1. Research Summary (data sources and counts)
2. Market Analysis (size, players, funding, disruption)
3. Capability Analysis (skills, tools, salaries, learning roadmap)
4. Strategic Entry Plan (entry paths, opportunities, risks)

**Charts:**
1. Market Metrics Overview (bar chart)
2. Trend Momentum (horizontal bar)
3. Skills Demand Radar (spider chart)
4. Risk Assessment Matrix (scatter plot)
5. Section Quality Scores (gauge charts)
6. Learning Timeline (Gantt-style)
7. Key Market Players (horizontal bar)

---

## 📄 License

MIT License — free to use, modify, and distribute. See `LICENSE` for details.

---

## 🙏 Acknowledgments

Built with:
- [Groq](https://groq.com) — Ultra-fast LLM inference
- [DuckDuckGo](https://duckduckgo.com) — Privacy-focused search
- [Wikipedia](https://www.wikipedia.org) — Free knowledge base
- [HackerNews](https://news.ycombinator.com) — Developer community
- [Streamlit](https://streamlit.io) — Rapid web app framework
- [Plotly](https://plotly.com) — Interactive visualizations

---

<div align="center">

**Built with 🤖 AI agents · 📊 Live data · 🔄 Self-refinement**

*No hallucinations. No hardcoded data. Just real intelligence.*

</div>
