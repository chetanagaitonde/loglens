# 🔍 LogLens — Autonomous Cloud Audit Log Investigator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Built with Gemini](https://img.shields.io/badge/Built%20with-Google%20Gemini-blue)](https://aistudio.google.com/)
[![Powered by Elastic](https://img.shields.io/badge/Powered%20by-Elastic-005571)](https://elastic.co)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://loglens-scgeakccvhijnu2vpqinyi.streamlit.app)
[![Google Cloud Rapid Agent Hackathon](https://img.shields.io/badge/Hackathon-Google%20Cloud%20Rapid%20Agent%202026-orange)](https://rapid-agent.devpost.com/)

> **Google Cloud Rapid Agent Hackathon 2026 — Elastic Track**

LogLens is an autonomous AI agent that investigates Google Cloud Platform audit logs and produces structured security threat reports — the way a senior analyst would, without any human hand-holding.

Upload a GCP audit log JSON file, and LogLens reasons over every event, identifies attack chains, assigns risk levels, and writes an executive summary. Powered by **Google Gemini** for reasoning and **Elasticsearch** for log storage and search.

---

## 🎬 Demo Video

> [▶ Watch the 3-minute demo on YouTube](#) 

---

## 🌐 Live Hosted App

> [🚀 Try LogLens Live](https://loglens-scgeakccvhijnu2vpqinyi.streamlit.app)

No installation needed — paste your Gemini API key in the sidebar and click Run Demo.

---

## 🧠 What LogLens Does

Most cloud security tools tell you *what* happened. LogLens tells you *why it matters*.

Given a set of GCP audit log entries, the Gemini agent:

1. **Reads every log entry** and flattens it into analyst-readable format
2. **Reasons about suspicion** — not just description, but analysis of *why* something is risky
3. **Groups events into attack chains** — connecting recon → data theft → persistence as one narrative
4. **Assigns risk levels** — CRITICAL / HIGH / MEDIUM / LOW / BENIGN per finding
5. **Writes an executive summary** — 3-5 sentences a non-technical manager can act on
6. **Stores and retrieves logs via Elasticsearch** — enabling scalable log search and future querying

### What It Detects

| Threat Type | Example |
|---|---|
| 🔴 Credential theft | Admin account used from suspicious external IP at 2 AM |
| 🔴 Privilege escalation | New service account granted Owner role within minutes |
| 🟠 Data exfiltration | Multiple sensitive files downloaded in rapid succession |
| 🟠 Suspicious IAM changes | Unknown service account created with unusual naming |
| 🟡 Off-hours access | Activity from 2–4 AM by accounts normally active 9–5 |
| 🟡 External domain access | User from `@external-domain.xyz` attempting IAM reads |
| 🟢 Benign activity | Normal developer activity during business hours from internal IPs |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Browser)                        │
│              Uploads GCP Audit Log JSON                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              STREAMLIT WEB UI (app.py)                   │
│         File upload · Stats · Report display            │
└────────┬───────────────────────────────┬────────────────┘
         │                               │
┌────────▼────────┐             ┌────────▼────────────────┐
│  ELASTIC MODULE │             │    GEMINI AI AGENT       │
│ elastic_tools.py│             │      analyzer.py         │
│                 │             │                          │
│ • index_logs()  │◄────────────│ • load_logs()            │
│ • search_logs() │             │ • flatten_log_entry()    │
│ • search_by_ip()│─────────────►• prepare_log_summary()  │
│ • delete_index()│             │ • build_prompt()         │
└────────┬────────┘             │ • run_agent()            │
         │                     └────────────┬─────────────┘
┌────────▼────────┐                         │
│  ELASTICSEARCH  │             ┌────────────▼─────────────┐
│  (Elastic Cloud)│             │    GOOGLE GEMINI API      │
│                 │             │   gemini-2.5-flash        │
│  audit-logs     │             │                          │
│  index          │             │  Reasons about threats   │
└─────────────────┘             │  Writes analyst report   │
                                └──────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| AI Reasoning | Google Gemini 2.5 Flash |
| Log Storage & Search | Elasticsearch (Elastic Cloud) |
| Web UI | Streamlit |
| Language | Python 3.11+ |
| Hosting | Streamlit Community Cloud |
| Data | GCP Cloud Audit Logs (JSON format) |

---

## 📁 Project Structure

```
loglens/
├── app.py                     # Streamlit web interface
├── test_agent.py              # Terminal test script
├── requirements.txt           # Python dependencies
├── SETUP.md                   # Local setup guide
├── README.md                  # This file
├── LICENSE                    # MIT License
├── .gitignore                 # Keeps secrets off GitHub
├── agent/
│   ├── __init__.py
│   ├── analyzer.py            # Core Gemini agent logic
│   └── elastic_tools.py       # Elasticsearch integration
└── logs/
    └── sample_audit_log.json  # Sample attack scenario for demo
```

---

## 🚀 Run Locally

### Prerequisites
- Python 3.9 or higher
- A free Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Setup (Mac/Linux)

```bash
# 1. Clone the repository
git clone https://github.com/chetanagaitonde/loglens.git
cd loglens

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Gemini API key
export GEMINI_API_KEY="your-key-here"

# 5. Run the app
streamlit run app.py
```

### Setup (Windows)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set GEMINI_API_KEY=your-key-here
streamlit run app.py
```

Open your browser at `http://localhost:8501`

### Quick Test (Terminal Only)

```bash
python3 test_agent.py
```

This runs the agent on the sample log and prints the report to your terminal — no browser needed.

---

## 🔵 Elastic Integration (Optional)

LogLens integrates with **Elasticsearch** via the Elastic Python client to store and retrieve audit logs from a real search database — replacing simple file reads with scalable log indexing.

### Setup

1. Create a free account at [cloud.elastic.co](https://cloud.elastic.co)
2. Create a deployment and copy your **Cloud ID** and **password**
3. In the LogLens sidebar, enter your Cloud ID and password
4. Check **"Store & query logs via Elasticsearch"**
5. LogLens will index your logs, retrieve them back, and run analysis

### What Elastic Adds

- Logs are indexed in Elasticsearch before analysis (not just read from a file)
- Enables `search_by_ip()`, `search_by_user()`, `search_errors()` queries
- Architecture is now: **File → Elasticsearch → Gemini** rather than **File → Gemini**
- Scales to real production log volumes (millions of events)

---

## 📊 Sample Attack Scenario

The bundled `logs/sample_audit_log.json` simulates a realistic cloud breach:

| Time | Event | Risk |
|------|-------|------|
| 02:13 AM | External IP `198.51.100.200` attempts IAM policy read → DENIED | 🟡 Recon |
| 02:14 AM | `admin@company.com` from suspicious IP downloads `employee_records.csv` | 🔴 Data theft |
| 02:15 AM | Same IP downloads `financial_reports_Q1.xlsx` | 🔴 Data theft |
| 02:16 AM | Creates new service account `backdoor-sa` | 🔴 Persistence |
| 02:17 AM | Grants `backdoor-sa` Owner role (full project control) | 🔴 Privilege escalation |
| 09:05 AM | `developer@company.com` lists compute instances (internal IP) | 🟢 Benign |
| 09:06 AM | Same developer lists storage buckets | 🟢 Benign |

LogLens identifies the 02:13–02:17 window as a coordinated attack chain and the 09:05–09:06 entries as normal activity.

---

## 📦 Dependencies

```
google-genai>=1.0.0      # Google Gemini API client
streamlit>=1.35.0        # Web UI framework
elasticsearch>=8.0.0     # Elastic integration
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Chetan Agaitonde**
- GitHub: [@chetanagaitonde](https://github.com/chetanagaitonde)
- Built for: Google Cloud Rapid Agent Hackathon 2026 — Elastic Track

---

## 🙏 Acknowledgements

- [Google Gemini](https://deepmind.google/technologies/gemini/) — AI reasoning engine
- [Elastic](https://elastic.co) — Search and log storage platform
- [Streamlit](https://streamlit.io) — Web app framework
- [Google Cloud](https://cloud.google.com) — Audit log format and infrastructure
