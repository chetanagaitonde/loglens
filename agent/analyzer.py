"""
LogLens - Core Agent (with Elastic MCP integration)
Reads GCP audit logs from Elasticsearch and uses Gemini to reason about threats.
"""

import json
import os
from google import genai
from google.genai import types


def load_logs(filepath: str) -> list[dict]:
    """Reads the audit log JSON file from disk."""
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def flatten_log_entry(entry: dict) -> str:
    """
    Converts one raw log entry into a clean readable one-liner for Gemini.
    """
    payload = entry.get("protoPayload", {})
    timestamp   = entry.get("timestamp", "unknown-time")
    severity    = entry.get("severity", "UNKNOWN")
    principal   = payload.get("authenticationInfo", {}).get("principalEmail", "unknown-user")
    caller_ip   = payload.get("requestMetadata", {}).get("callerIp", "unknown-ip")
    user_agent  = payload.get("requestMetadata", {}).get("callerSuppliedUserAgent", "")
    service     = payload.get("serviceName", "unknown-service")
    method      = payload.get("methodName", "unknown-method")
    resource    = payload.get("resourceName", "unknown-resource")
    status      = payload.get("status", {})
    status_msg  = f'ERROR:{status.get("message","")}' if status.get("code") else "OK"

    return (
        f"[{timestamp}] User={principal} | IP={caller_ip} | Agent={user_agent} | "
        f"Service={service} | Action={method} | Resource={resource} | "
        f"Status={status_msg} | Severity={severity}"
    )


def prepare_log_summary(log_entries: list[dict]) -> str:
    """Converts all log entries into a single text block for Gemini."""
    lines = []
    for i, entry in enumerate(log_entries, start=1):
        lines.append(f"Entry {i}: {flatten_log_entry(entry)}")
    return "\n".join(lines)


def build_prompt(log_text: str, source_label: str = "GCP Audit Log") -> str:
    """Builds the full prompt sent to Gemini."""
    return f"""
You are LogLens, an expert cloud security analyst with 10+ years experience 
investigating Google Cloud Platform incidents.

Below are {source_label} entries retrieved from Elasticsearch (via the Elastic MCP integration).
Your job is to:
1. Read every entry carefully and identify ALL suspicious or anomalous events.
2. Group related events into ATTACK CHAINS (sequences that form a bigger picture).
3. Assign a RISK LEVEL to each finding: CRITICAL / HIGH / MEDIUM / LOW / BENIGN.
4. Explain your reasoning like you're briefing a security team — clearly, in plain English.
5. At the end, write a concise EXECUTIVE SUMMARY of what happened overall.

IMPORTANT RULES:
- Do NOT just describe what happened. REASON about WHY it is or isn't suspicious.
- Point out specific timestamps, IPs, users, and resources as evidence.
- If you see an attack chain forming (e.g., recon → data theft → persistence), call it out explicitly.
- Flag anything happening at unusual hours (e.g., 2–4 AM) as higher risk.
- Flag new or external email domains that shouldn't have access.
- Flag creation of new service accounts or IAM role changes as potentially dangerous.

--- LOG ENTRIES (from Elasticsearch) ---
{log_text}
--- END OF LOGS ---

Now produce your full security analysis report. Use this structure:

## 🔍 Individual Findings

For each suspicious finding:
**Finding [N]: [Short title]**
- Risk Level: [CRITICAL/HIGH/MEDIUM/LOW/BENIGN]
- Timestamp(s): ...
- Evidence: ...
- Analysis: ...

## 🔗 Attack Chain Analysis
(Group related findings into a narrative if they form a sequence)

## 📋 Executive Summary
(3-5 sentences. What happened? How severe? What should the team do immediately?)

## ✅ Benign Activity
(List any events that are normal and not concerning)
"""


def run_agent(log_entries: list[dict], api_key: str, source_label: str = "GCP Audit Log") -> dict:
    """
    Main function. Takes log entries (already loaded) + API key.
    Works whether logs came from a local file OR from Elasticsearch.
    """
    if not log_entries:
        return {"status": "error", "error": "No log entries provided."}

    log_text = prepare_log_summary(log_entries)
    prompt = build_prompt(log_text, source_label)

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=4096,
            )
        )
        report_text = response.text
    except Exception as e:
        return {"status": "error", "error": f"Gemini API call failed: {e}"}

    return {
        "status": "success",
        "report": report_text,
        "log_count": len(log_entries),
    }


def run_agent_from_file(log_filepath: str, api_key: str) -> dict:
    """Convenience function: loads from file then runs agent."""
    try:
        log_entries = load_logs(log_filepath)
    except FileNotFoundError:
        return {"status": "error", "error": f"File not found: {log_filepath}"}
    except json.JSONDecodeError as e:
        return {"status": "error", "error": f"Invalid JSON: {e}"}
    return run_agent(log_entries, api_key, source_label="GCP Audit Log")