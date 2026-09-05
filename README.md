TRACK_ID $ID=PS1$

# Patient Intake Triage Assistant

An AI-powered clinical triage helper designed to parse patient descriptions in natural language, evaluate them against a structured rulebook, generate grounded triage notes with citations, and escalate complex or high-risk cases to medical professionals.

## Features
- **Deterministic Rule Grounding:** Rules stored in JSON for structured verification.
- **Rule Citations:** Cites the exact rule ID triggering the triage recommendation.
- **No Direct Diagnosis:** Focuses strictly on intake, departmental routing, and urgency determination.
- **Safety Escalation:** Explicitly flags high-risk or uncertain cases to human operators.

## Setup & Running

Set your Gemini API Key:
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

Run the single-command starter:
```bash
pip install -r requirements.txt
python app.py
```
Open `http://localhost:8000` in your browser.

## Data & Documents
- `data/triage_rules.json`: Structured triage knowledge base containing urgency levels, target departments, criteria, and high-risk escalation triggers.

## Demo Video
[Link to your 3-minute video]
