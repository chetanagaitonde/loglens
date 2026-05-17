"""
Quick terminal test for LogLens agent.
Run this FIRST to verify your API key and the agent work,
before touching the Streamlit UI.

Usage:
    python test_agent.py
"""

import os
import sys
from agent.analyzer import run_agent

def main():
    # ── Get API key ──────────────────────────────────────────────────────────
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    if not api_key:
        print("\n❌ No API key found.")
        print("   Set it like this in your terminal:")
        print("   export GEMINI_API_KEY='your-key-here'")
        print("   Then re-run: python test_agent.py\n")
        sys.exit(1)
    
    print("\n🔍 LogLens Agent Test")
    print("=" * 50)
    print(f"✅ API key loaded ({len(api_key)} characters)")
    print("📂 Loading sample audit log...")
    
    log_path = os.path.join("logs", "sample_audit_log.json")
    
    print("🤖 Sending to Gemini for analysis... (please wait 20-40 seconds)")
    print("=" * 50)
    
    result = run_agent(log_path, api_key)
    
    if result["status"] == "error":
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)
    
    print(f"\n✅ Success! Analysed {result['log_count']} log entries.\n")
    print("─" * 50)
    print(result["report"])
    print("─" * 50)
    print("\n✅ Test passed. Your agent is working correctly.")
    print("   Now run the full UI with: streamlit run app.py\n")

if __name__ == "__main__":
    main()
