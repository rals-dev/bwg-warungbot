# WarungBot ☕

> **WarungBot - Asisten Pintar Kedai Kopi (Rals Coffee Shop)**  
> Built with Google Cloud Vertex AI, Agent Development Kit (ADK), Gemini 2.5 Flash, Cloud Firestore, Cloud Storage, and A2UI.

![WarungBot Demo](demo.gif)

## 📌 Overview

**WarungBot** is an autonomous AI assistant designed specifically for Indonesian coffee shop owners and staff. It streamlines daily café operations by managing inventory, recording sales transactions, computing profit margins in Indonesian Rupiah (IDR), analyzing real-time weather conditions, and generating marketing visuals (promotional posters and omni videos).

---

## ✨ Features & Tools

- 📦 **Inventory & Stock Management (`get_low_stock`, `update_stock`, `list_products`)**:
  - Live queries against **Google Cloud Firestore**.
  - Automatically flags items falling below safety threshold levels (e.g. Croissant, Matcha Latte).
- 💰 **Sales Recording & Analytics (`record_sale`, `get_sales_summary`)**:
  - Records real-time transactions and computes revenue, cost of goods sold (COGS), and profit margins in IDR.
- 🌦️ **Weather Integration (`get_weather`)**:
  - Fetches current weather and temperatures to suggest weather-appropriate promotions (e.g., iced coffee on hot days).
- 🎨 **Marketing Asset Generation (`generate_poster`, `generate_video`)**:
  - Generates high-quality promotional posters using `gemini-3.1-flash-lite-image`.
  - Generates promo videos using `gemini-omni-flash-preview`.
  - Automatically stores generated assets in **Google Cloud Storage** and returns public URLs.
- 💻 **Agent Engine Code Execution Sandbox**:
  - Executes Python calculations safely in Vertex AI Reasoning Engine Code Sandbox.
- 🎴 **Rich A2UI Display**:
  - Renders interactive cards, summary tables, and product images natively in ADK Playground and web frontends.
- 🌐 **Custom Web Frontend & A2A Proxy**:
  - Includes a lightweight FastAPI proxy and responsive branded web interface communicating via the **A2A Protocol**.

---

## 🏗️ Project Structure

```
warungbot/
├── app/
│   ├── agent.py               # Root ADK agent definition & callbacks
│   ├── a2ui_utils.py          # A2UI v0.8 schema manager & response transformer
│   ├── app_utils/             # Agent helpers
│   └── tools/                 # Custom domain tools
│       ├── firestore_tools.py # Firestore inventory & sales tools
│       ├── weather_tool.py    # Live weather lookup tool
│       ├── image_tool.py      # Gemini image generation & GCS upload tool
│       └── video_tool.py      # Gemini Omni video generation & GCS upload tool
├── frontend/                  # Custom chat web frontend
│   ├── main.py                # FastAPI proxy with A2A client
│   └── static/
│       └── index.html         # Branded responsive chat interface
├── demo.gif                   # Recorded agent walkthrough
├── project_brief.md           # Project specification & brief
├── pyproject.toml             # Python dependencies
└── agents-cli-manifest.yaml   # Agent manifest
```

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) package manager
- `google-agents-cli`
- Google Cloud SDK (`gcloud`) configured with project permissions

### 2. Install Dependencies
```bash
uv sync
```

### 3. Run Agent Locally (ADK Playground)
```bash
uv run adk web . --host 127.0.0.1 --port 8080 --allow_origins '*'
```
Open `http://localhost:8080/dev-ui/?app=app` in your browser.

### 4. Run Custom Web Chat Frontend
```bash
cd frontend
export AGENT_ENGINE_RESOURCE_NAME="projects/<project-id>/locations/<region>/reasoningEngines/<id>"
export AGENT_DIRECTORY="app"
uv run python main.py
```
Open `http://localhost:8080` in your browser.

---

## 🛡️ License
Built during the **Build with Gemini** workshop.
