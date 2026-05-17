# 🔍 LogLens — Complete Setup Guide (Mac)

---

## WHAT YOU'LL HAVE WHEN DONE

A web app where you upload a Google Cloud audit log JSON file,
and an AI agent (powered by Gemini) reads it and writes a full
security threat report — like a senior analyst would.

---

## STEP 1 — Get Your Gemini API Key (5 minutes)

This key lets your code talk to Google's Gemini AI. It's free.

1. Open your browser and go to: **https://aistudio.google.com/apikey**
2. Sign in with any Google account
3. Click **"Create API Key"**
4. Copy the key — it looks like: `AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
5. Keep this tab open or paste the key in a notes file temporarily

> ⚠️ Never share this key publicly or put it in your GitHub code.

---

## STEP 2 — Check Python Is Installed (2 minutes)

Open **Terminal** on your Mac:
- Press `Cmd + Space`, type `Terminal`, press Enter

Type this and press Enter:
```bash
python3 --version
```

You should see something like `Python 3.11.x` or `Python 3.12.x`.
If you see an error, download Python from: **https://www.python.org/downloads/**

---

## STEP 3 — Open VS Code and the Project (3 minutes)

1. Open **VS Code**
2. Go to **File → Open Folder**
3. Navigate to and select the `loglens` folder (wherever you saved it)
4. VS Code will open the project

Now open a Terminal **inside VS Code**:
- Press `` Ctrl + ` `` (backtick key, top-left of keyboard)
- A terminal panel opens at the bottom — use this for all commands below

---

## STEP 4 — Create a Virtual Environment (3 minutes)

A virtual environment is just an isolated box for your project's Python packages.
It keeps your LogLens packages separate from other Python stuff on your Mac.

In the VS Code terminal, type these ONE AT A TIME, pressing Enter after each:

```bash
python3 -m venv venv
```

Now activate it (you must do this every time you open a new terminal):
```bash
source venv/bin/activate
```

You'll see `(venv)` appear at the start of your terminal line. That means it's working.

---

## STEP 5 — Install Packages (2 minutes)

Still in the terminal with `(venv)` active:

```bash
pip install -r requirements.txt
```

This installs:
- `google-genai` → lets Python talk to Gemini
- `streamlit` → creates the web UI automatically

You'll see a lot of text scrolling. Wait for it to finish (1-2 minutes).

Verify it worked:
```bash
python3 -c "from google import genai; print('google-genai OK')"
python3 -c "import streamlit; print('streamlit OK')"
```

Both should print OK. If either fails, run: `pip install google-genai streamlit`

---

## STEP 6 — Set Your API Key (1 minute)

In the terminal, type this (replace the placeholder with your real key):

```bash
export GEMINI_API_KEY="AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

> ⚠️ This only lasts for the current terminal session.
> If you close the terminal, you'll need to run this again.
> 
> NEVER hardcode your API key directly in Python files.

---

## STEP 7 — Test the Agent First (terminal only)

Before opening the web UI, let's make sure the agent brain works:

```bash
python3 test_agent.py
```

You should see:
```
🔍 LogLens Agent Test
==================================================
✅ API key loaded (39 characters)
📂 Loading sample audit log...
🤖 Sending to Gemini for analysis... (please wait 20-40 seconds)
==================================================

✅ Success! Analysed 7 log entries.

──────────────────────────────────────────────────
## 🔍 Individual Findings
...
(full security report appears here)
...
✅ Test passed. Your agent is working correctly.
```

If this works, your agent is 100% functional.

---

## STEP 8 — Launch the Web UI

```bash
streamlit run app.py
```

Your browser will automatically open to: **http://localhost:8501**

You'll see the LogLens interface.

**To use it:**
1. Paste your Gemini API key in the sidebar (left side)
2. Click **"Run Demo"** to test with the sample attack log
3. OR upload your own GCP audit log JSON file
4. Click **"Analyse Logs with LogLens AI"**
5. Wait ~30 seconds — your report appears!

To stop the server: press `Ctrl + C` in the terminal.

---

## STEP 9 — Every Time You Come Back

Next time you open VS Code and want to run LogLens:

```bash
# 1. Activate your venv (always do this first)
source venv/bin/activate

# 2. Set your API key
export GEMINI_API_KEY="your-key-here"

# 3. Run the app
streamlit run app.py
```

---

## PROJECT FILE STRUCTURE

```
loglens/
├── app.py                    ← Web UI (Streamlit)
├── test_agent.py             ← Quick terminal test
├── requirements.txt          ← Packages list
├── SETUP.md                  ← This file
├── agent/
│   ├── __init__.py
│   └── analyzer.py           ← Core Gemini agent logic
└── logs/
    └── sample_audit_log.json ← Sample attack scenario for demo
```

---

## COMMON ERRORS AND FIXES

**"ModuleNotFoundError: No module named 'google'"**
→ You forgot to activate venv. Run: `source venv/bin/activate`

**"API key not valid"**
→ Re-copy your key from aistudio.google.com/apikey. Make sure no spaces.

**"streamlit: command not found"**
→ Venv not active. Run `source venv/bin/activate` first.

**"FileNotFoundError: logs/sample_audit_log.json"**
→ Make sure you're running commands from inside the `loglens/` folder.
→ Check with: `pwd` (should end in `/loglens`)

---

## WHAT THE SAMPLE LOG CONTAINS

The demo log (`sample_audit_log.json`) simulates a realistic attack:

| Time | Event |
|------|-------|
| 02:13 AM | Unknown external IP tries to read IAM policy → DENIED |
| 02:14 AM | Admin account (from suspicious IP) downloads sensitive files |
| 02:15 AM | Same IP downloads financial reports |
| 02:16 AM | Creates a new service account called "backdoor-sa" |
| 02:17 AM | Gives that backdoor account OWNER permissions (full control) |
| 09:05 AM | Normal developer activity (benign) |
| 09:06 AM | Normal developer activity (benign) |

LogLens should identify the 02:13–02:17 window as a coordinated attack chain.
