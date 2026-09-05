import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from src.triage_engine import TriageEngine

app = FastAPI(title="Patient Intake Triage Assistant")

triage_engine = None

@app.on_event("startup")
def startup_event():
    global triage_engine
    if not os.getenv("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY not found in environment.")
    triage_engine = TriageEngine()

class TriageRequest(BaseModel):
    description: str
    follow_ups: str = ""

@app.post("/api/triage")
def process_triage(req: TriageRequest):
    if not triage_engine:
        raise HTTPException(status_code=500, detail="Triage engine not initialized.")
    try:
        res = triage_engine.evaluate_triage(req.description, req.follow_ups)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Patient Intake Triage Assistant</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f4f7f6; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; font-size: 24px; margin-bottom: 20px; }
            textarea, input { width: 100%; padding: 10px; margin: 8px 0 16px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
            button { background: #007bff; color: white; padding: 12px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; }
            button:hover { background: #0056b3; }
            .card { background: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin-top: 20px; border-radius: 4px; }
            .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; background: #6c757d; }
            .High, .Immediate { background: #dc3545; }
            .Moderate { background: #ffc107; color: #000; }
            .Low { background: #28a745; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Patient Intake Triage Assistant (TRACK_ID $ID=PS1$)</h1>
            <label><b>Patient Initial Complaint:</b></label>
            <textarea id="desc" rows="3" placeholder="e.g. Patient complains of chest tightness and slight dizziness since 30 mins ago."></textarea>
            
            <label><b>Follow-up Answers (Optional):</b></label>
            <textarea id="followup" rows="2" placeholder="e.g. Pain does not radiate to jaw, no fever."></textarea>
            
            <button onclick="submitTriage()">Run Triage Assessment</button>
            
            <div id="output" style="display:none;" class="card">
                <h3>Triage Summary Note</h3>
                <p><b>Urgency:</b> <span id="urgency" class="badge"></span></p>
                <p><b>Recommended Dept:</b> <span id="dept"></span></p>
                <p><b>Cited Rule ID:</b> <code id="rule"></code></p>
                <p><b>Reasoning:</b> <span id="reasoning"></span></p>
                <p><b>Reported vs Established:</b> <span id="comparison"></span></p>
                <p><b>Missing/Unknowns:</b> <span id="unknowns"></span></p>
                <p><b>Escalate to Human:</b> <strong id="escalate"></strong></p>
                <p><b>Suggested Follow-up Questions:</b></p>
                <ul id="questions"></ul>
            </div>
        </div>

        <script>
            async function submitTriage() {
                const desc = document.getElementById('desc').value;
                const followup = document.getElementById('followup').value;
                if(!desc) return alert("Please enter patient description");
                
                const res = await fetch('/api/triage', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({description: desc, follow_ups: followup})
                });
                const data = await res.json();
                
                document.getElementById('output').style.display = 'block';
                document.getElementById('urgency').innerText = data.urgency_level;
                document.getElementById('urgency').className = 'badge ' + data.urgency_level.split(' ')[0];
                document.getElementById('dept').innerText = data.recommended_department;
                document.getElementById('rule').innerText = data.cited_rule_id;
                document.getElementById('reasoning').innerText = data.reasoning;
                document.getElementById('comparison').innerText = data.patient_reported_vs_established;
                document.getElementById('unknowns').innerText = data.missing_or_unknown_info;
                document.getElementById('escalate').innerText = data.escalate_to_human ? "YES (High Risk / Uncertain)" : "NO";
                
                const qList = document.getElementById('questions');
                qList.innerHTML = '';
                (data.follow_up_questions || []).forEach(q => {
                    const li = document.createElement('li');
                    li.innerText = q;
                    qList.appendChild(li);
                });
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
