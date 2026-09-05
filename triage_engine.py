import os
import json
import google.genai as genai
from google.genai import types

class TriageEngine:
    def __init__(self, rules_path="data/triage_rules.json"):
        with open(rules_path, "r") as f:
            self.rules = json.load(f)
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        self.client = genai.Client(api_key=api_key)

    def evaluate_triage(self, patient_description: str, follow_up_answers: str = "") -> dict:
        rules_text = json.dumps(self.rules, indent=2)
        
        prompt = f"""
You are a Healthcare Patient Intake Triage Assistant.
You MUST adhere strictly to these rules:
1. NEVER diagnose the patient.
2. Ground all recommendations in the provided triage rules database.
3. Cite the exact rule_id for every recommendation.
4. If details are missing or risk triggers are present, escalate to human or ask targeted follow-ups.

RULES DATABASE:
{rules_text}

PATIENT DESCRIPTION:
"{patient_description}"

ADDITIONAL PATIENT ANSWERS TO FOLLOW-UPS:
"{follow_up_answers}"

Analyze the case and return a VALID JSON response matching this structure:
{{
  "urgency_level": "Low | Moderate | High | Immediate Escalation",
  "recommended_department": "Department Name or Human Triage Escalation",
  "cited_rule_id": "RULE_ID or NONE",
  "reasoning": "Explanation based on rules",
  "patient_reported_vs_established": "Summary of initial vs follow-up details",
  "missing_or_unknown_info": "Information still required",
  "follow_up_questions": ["Question 1", "Question 2"],
  "escalate_to_human": true/false
}}
"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )
        
        return json.loads(response.text)
