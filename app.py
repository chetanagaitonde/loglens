"""
LogLens - Web Interface (Streamlit)
Run with: streamlit run app.py
"""

import streamlit as st
import os
import json
import tempfile
import sys

sys.path.insert(0, os.path.dirname(__file__))
from agent.analyzer import run_agent_from_file, load_logs, run_agent
from agent.elastic_tools import (
    connect_to_elastic, index_logs, search_logs,
    search_by_ip, search_errors, delete_index
)

st.set_page_config(page_title="LogLens – Cloud Audit Investigator", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .loglens-header { background: linear-gradient(135deg, #1a1f2e 0%, #0d1b2a 100%); border: 1px solid #00d4ff33; border-radius: 12px; padding: 24px 32px; margin-bottom: 24px; text-align: center; }
    .loglens-header h1 { color: #00d4ff; font-size: 2.4rem; margin: 0; font-family: 'Courier New', monospace; letter-spacing: 2px; }
    .loglens-header p  { color: #8892a4; margin: 6px 0 0 0; font-size: 1rem; }
    .stat-card { background: #1a1f2e; border: 1px solid #2d3447; border-radius: 8px; padding: 16px; text-align: center; }
    .stat-number { font-size: 2rem; font-weight: bold; color: #00d4ff; }
    .stat-label  { color: #8892a4; font-size: 0.85rem; margin-top: 4px; }
    .report-container { background: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 24px; font-family: 'Segoe UI', sans-serif; line-height: 1.7; color: #e2e8f0; }
    [data-testid="stFileUploader"] { background: #1a1f2e; border: 2px dashed #00d4ff44; border-radius: 8px; padding: 8px; }
    .stButton > button { background: linear-gradient(135deg, #00d4ff, #0080ff); color: #000; font-weight: bold; border: none; border-radius: 6px; padding: 10px 24px; font-size: 1rem; width: 100%; cursor: pointer; }
    [data-testid="stSidebar"] { background-color: #111827; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="loglens-header">
    <h1>🔍 LOGLENS</h1>
    <p>Autonomous Cloud Audit Log Investigator · Powered by Google Gemini + Elastic</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key_input = st.text_input("Gemini API Key", type="password", placeholder="Paste your Gemini API key here")
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        secret_key = ""
    api_key = api_key_input or secret_key or os.getenv("GEMINI_API_KEY", "")

    st.markdown("---")
    st.markdown("### 🔵 Elastic Integration (Optional)")
    elastic_cloud_id = st.text_input("Elastic Cloud ID", type="password", placeholder="Your Elastic Cloud ID")
    elastic_password = st.text_input("Elastic Password", type="password", placeholder="Your Elastic password")
    use_elastic = st.checkbox("Store & query logs via Elasticsearch", value=False)

    st.markdown("---")
    st.markdown("### 📖 How to use LogLens")
    st.markdown("1. Paste your **Gemini API key** above\n2. Upload a **GCP Audit Log** JSON file\n3. Click **Analyse Logs**\n4. Read the AI threat report")
    st.markdown("---")
    st.markdown("### 🎯 What LogLens detects")
    st.markdown("- 🔴 Credential theft\n- 🔴 Privilege escalation\n- 🟠 Data exfiltration\n- 🟠 Suspicious IAM changes\n- 🟡 Off-hours access\n- 🟢 Normal activity")
    st.markdown("---")
    st.caption("LogLens v1.0 · Google Cloud Rapid Agent Hackathon 2026 · Elastic Track")

col1, col2 = st.columns([3, 2])
with col1:
    st.markdown("### 📁 Upload Audit Log")
    uploaded_file = st.file_uploader("Drop your GCP audit log JSON file here", type=["json"])
with col2:
    st.markdown("### ⚡ Quick Start")
    st.markdown("No logs? Try the built-in sample — it contains a realistic simulated attack chain.")
    use_demo = st.button("🎮 Run Demo (Sample Attack Scenario)")

st.markdown("---")

log_entries = None
source_label = "GCP Audit Log"

if use_demo:
    demo_path = os.path.join(os.path.dirname(__file__), "logs", "sample_audit_log.json")
    if os.path.exists(demo_path):
        try:
            log_entries = load_logs(demo_path)
            source_label = "GCP Audit Log (Demo)"
            st.info("✅ Using sample audit log — contains a simulated credential theft + privilege escalation attack.")
        except Exception as e:
            st.error(f"❌ Failed to load demo log: {e}")
    else:
        st.error("Sample log file not found. Make sure logs/sample_audit_log.json exists.")

elif uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()
        log_entries = json.loads(file_bytes.decode("utf-8"))
        if not isinstance(log_entries, list):
            st.error("❌ Your JSON file must contain a list (array) of log entries at the top level.")
            log_entries = None
        else:
            st.success(f"✅ File uploaded: **{uploaded_file.name}** — {len(log_entries)} entries found.")
    except json.JSONDecodeError as e:
        st.error(f"❌ Could not parse JSON file: {e}")
        log_entries = None
    except Exception as e:
        st.error(f"❌ Unexpected error reading file: {e}")
        log_entries = None

if log_entries is not None:
    entry_count = len(log_entries)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{entry_count}</div><div class="stat-label">Log Entries Found</div></div>', unsafe_allow_html=True)
    with c2:
        services = set()
        for e in log_entries:
            s = e.get("protoPayload", {}).get("serviceName", "")
            if s: services.add(s.split(".")[0])
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(services)}</div><div class="stat-label">Cloud Services Touched</div></div>', unsafe_allow_html=True)
    with c3:
        errors = sum(1 for e in log_entries if e.get("severity") in ("ERROR", "CRITICAL", "ALERT"))
        st.markdown(f'<div class="stat-card"><div class="stat-number">{errors}</div><div class="stat-label">Error / Alert Entries</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("👁️ Preview raw log (first 3 entries)"):
        st.json(log_entries[:3])
    st.markdown("<br>", unsafe_allow_html=True)

    if use_elastic:
        if not elastic_cloud_id or not elastic_password:
            st.warning("⚠️ Please enter your Elastic Cloud ID and password in the sidebar.")
        else:
            with st.spinner("🔵 Connecting to Elasticsearch and indexing logs..."):
                try:
                    es_client = connect_to_elastic(elastic_cloud_id, "elastic", elastic_password)
                    delete_index(es_client)
                    count = index_logs(es_client, log_entries)
                    log_entries = search_logs(es_client)
                    source_label = f"Elasticsearch (indexed {count} entries)"
                    st.success(f"✅ {count} log entries indexed in Elasticsearch and retrieved for analysis.")
                except Exception as e:
                    st.error(f"❌ Elastic connection failed: {e}")
                    st.info("Falling back to direct analysis without Elasticsearch.")

    if not api_key:
        st.warning("⚠️ Please enter your Gemini API key in the sidebar before analysing.")
    else:
        if st.button("🔍 Analyse Logs with LogLens AI"):
            with st.spinner("🤖 LogLens is investigating your logs... This may take 20-40 seconds."):
                result = run_agent(log_entries, api_key, source_label=source_label)
            if result["status"] == "error":
                st.error(f"❌ Analysis failed: {result['error']}")
            else:
                st.success(f"✅ Analysis complete! Examined **{result['log_count']}** log entries.")
                st.markdown("---")
                st.markdown("## 🛡️ Security Analysis Report")
                st.markdown(f'<div class="report-container">{result["report"]}</div>', unsafe_allow_html=True)
                st.download_button(
                    label="⬇️ Download Report as Markdown",
                    data=result["report"],
                    file_name="loglens_security_report.md",
                    mime="text/markdown",
                )
else:
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px; color: #4a5568;">
        <div style="font-size: 4rem;">🔍</div>
        <h3 style="color: #6b7280;">Upload a GCP Audit Log or run the Demo to begin</h3>
        <p>LogLens will autonomously investigate your cloud activity and generate a full threat report.</p>
    </div>
    """, unsafe_allow_html=True)
