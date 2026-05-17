"""
LogLens - Web Interface (Streamlit)
Run with: streamlit run app.py
"""

import streamlit as st
import os
import json
import tempfile
import sys

# Make sure Python can find the agent folder
sys.path.insert(0, os.path.dirname(__file__))

# Existing + updated imports
from agent.elastic_tools import (
    connect_to_elastic, index_logs, search_logs,
    search_by_ip, search_errors, delete_index
)

from agent.analyzer import run_agent, run_agent_from_file, load_logs

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LogLens – Cloud Audit Investigator",
    page_icon="🔍",
    layout="wide",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  – dark security-tool aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0e1117; }

    /* Header banner */
    .loglens-header {
        background: linear-gradient(135deg, #1a1f2e 0%, #0d1b2a 100%);
        border: 1px solid #00d4ff33;
        border-radius: 12px;
        padding: 24px 32px;
        margin-bottom: 24px;
        text-align: center;
    }
    .loglens-header h1 {
        color: #00d4ff;
        font-size: 2.4rem;
        margin: 0;
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
    }
    .loglens-header p {
        color: #8892a4;
        margin: 6px 0 0 0;
        font-size: 1rem;
    }

    /* Stat cards */
    .stat-card {
        background: #1a1f2e;
        border: 1px solid #2d3447;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .stat-number { 
        font-size: 2rem; 
        font-weight: bold; 
        color: #00d4ff; 
    }

    .stat-label  { 
        color: #8892a4; 
        font-size: 0.85rem; 
        margin-top: 4px; 
    }

    /* Report box */
    .report-container {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 24px;
        font-family: 'Segoe UI', sans-serif;
        line-height: 1.7;
        color: #e2e8f0;
    }

    /* Risk level badges */
    .risk-critical { 
        color: #ff4444; 
        font-weight: bold; 
    }

    .risk-high { 
        color: #ff8800; 
        font-weight: bold; 
    }

    .risk-medium { 
        color: #ffcc00; 
        font-weight: bold; 
    }

    .risk-low { 
        color: #44ff88; 
        font-weight: bold; 
    }

    /* Upload zone */
    [data-testid="stFileUploader"] {
        background: #1a1f2e;
        border: 2px dashed #00d4ff44;
        border-radius: 8px;
        padding: 8px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #0080ff);
        color: #000;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 10px 24px;
        font-size: 1rem;
        width: 100%;
        cursor: pointer;
    }

    .stButton > button:hover { 
        opacity: 0.9; 
    }

    /* Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #111827; 
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="loglens-header">
    <h1>🔍 LOGLENS</h1>
    <p>Autonomous Cloud Audit Log Investigator · Powered by Google Gemini</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR – API key + instructions
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Paste your Gemini API key here",
        help="Get your free key from: https://aistudio.google.com/apikey"
    )

    # If user hasn't typed a key, also check environment variable
    api_key = api_key_input or os.getenv("GEMINI_API_KEY", "")

    # ─────────────────────────────────────────
    #  ELASTICSEARCH INTEGRATION SECTION
    # ─────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔵 Elastic Integration (Optional)")

    elastic_cloud_id = st.text_input(
        "Elastic Cloud ID",
        type="password",
        placeholder="Your Elastic Cloud ID"
    )

    elastic_password = st.text_input(
        "Elastic Password",
        type="password",
        placeholder="Your Elastic password"
    )

    use_elastic = st.checkbox(
        "Use Elasticsearch as data source",
        value=False,
        help="When checked, logs are stored in and retrieved from Elasticsearch"
    )

    st.markdown("---")
    st.markdown("### 📖 How to use LogLens")

    st.markdown("""
1. Paste your **Gemini API key** above  
2. Upload a **GCP Audit Log** JSON file  
   *(or click Demo to use sample data)*  
3. Click **Analyse Logs**  
4. Read the AI-generated threat report  
    """)

    st.markdown("---")
    st.markdown("### 🎯 What LogLens detects")

    st.markdown("""
- 🔴 Credential theft patterns  
- 🔴 Privilege escalation  
- 🟠 Sensitive data exfiltration  
- 🟠 Suspicious IAM changes  
- 🟡 Off-hours access  
- 🟡 Unknown IP addresses  
- 🟢 Normal activity baseline  
    """)

    st.markdown("---")
    st.caption("LogLens v1.0 · Google Cloud Rapid Agent Hackathon 2026")

# ─────────────────────────────────────────────
#  MAIN AREA – Upload + Analyse
# ─────────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### 📁 Upload Audit Log")

    uploaded_file = st.file_uploader(
        "Drop your GCP audit log JSON file here",
        type=["json"],
        help="Export from GCP Console: Logging > Log Explorer > Download JSON"
    )

with col2:
    st.markdown("### ⚡ Quick Start")

    st.markdown(
        "No logs? Try the built-in sample — it contains a realistic simulated attack chain."
    )

    use_demo = st.button("🎮 Run Demo (Sample Attack Scenario)")

st.markdown("---")

# ─────────────────────────────────────────────
#  DETERMINE WHICH FILE TO ANALYZE
# ─────────────────────────────────────────────
log_filepath = None

if use_demo:
    # Use the bundled sample log
    demo_path = os.path.join(
        os.path.dirname(__file__),
        "logs",
        "sample_audit_log.json"
    )

    if os.path.exists(demo_path):
        log_filepath = demo_path

        st.info(
            "✅ Using sample audit log — contains a simulated credential theft + privilege escalation attack."
        )
    else:
        st.error(
            "Sample log file not found. Make sure logs/sample_audit_log.json exists."
        )

elif uploaded_file is not None:
    # Save the uploaded file to a temp location so we can read it
    with tempfile.NamedTemporaryFile(
        suffix=".json",
        delete=False,
        mode="wb"
    ) as tmp:

        tmp.write(uploaded_file.read())
        log_filepath = tmp.name

    st.success(f"✅ File uploaded: **{uploaded_file.name}**")

# ─────────────────────────────────────────────
#  SHOW A PREVIEW OF THE LOG FILE
# ─────────────────────────────────────────────
if log_filepath:

    with open(log_filepath) as f:
        raw = json.load(f)

    entry_count = len(raw)

    # Stats row
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{entry_count}</div>
            <div class="stat-label">Log Entries Found</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        services = set()

        for e in raw:
            s = e.get("protoPayload", {}).get("serviceName", "")

            if s:
                services.add(s.split(".")[0])

        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(services)}</div>
            <div class="stat-label">Cloud Services Touched</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        errors = sum(
            1 for e in raw
            if e.get("severity") in ("ERROR", "CRITICAL", "ALERT")
        )

        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{errors}</div>
            <div class="stat-label">Error / Alert Entries</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Raw log preview (collapsible)
    with st.expander("👁️ Preview raw log (first 3 entries)"):
        st.json(raw[:3])

    # ─────────────────────────────────────────
    #  ANALYSE BUTTON
    # ─────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)

    if not api_key:
        st.warning(
            "⚠️ Please enter your Gemini API key in the sidebar before analysing."
        )

    else:
        if st.button("🔍 Analyse Logs with LogLens AI"):

            with st.spinner(
                "🤖 LogLens is investigating your logs... This may take 20-40 seconds."
            ):
                result = run_agent(log_filepath, api_key)

            if result["status"] == "error":
                st.error(f"❌ Analysis failed: {result['error']}")

            else:
                st.success(
                    f"✅ Analysis complete! Examined **{result['log_count']}** log entries."
                )

                st.markdown("---")
                st.markdown("## 🛡️ Security Analysis Report")

                st.markdown(
                    f'<div class="report-container">{result["report"]}</div>',
                    unsafe_allow_html=True
                )

                # Download button for the report
                st.download_button(
                    label="⬇️ Download Report as Markdown",
                    data=result["report"],
                    file_name="loglens_security_report.md",
                    mime="text/markdown",
                )

# ─────────────────────────────────────────────
#  EMPTY STATE
# ─────────────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px; color: #4a5568;">
        <div style="font-size: 4rem;">🔍</div>
        <h3 style="color: #6b7280;">
            Upload a GCP Audit Log or run the Demo to begin
        </h3>
        <p>
            LogLens will autonomously investigate your cloud activity
            and generate a full threat report.
        </p>
    </div>
    """, unsafe_allow_html=True)