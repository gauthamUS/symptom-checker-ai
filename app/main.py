# app/main.py
from fastapi import FastAPI, HTTPException
from app.models import SymptomInput, SymptomResponse
from app.llm_client import call_llm
from app.db import save_query
import json, re, os

app = FastAPI(title="Symptom Checker API", version="1.1")

# Load system prompt from file
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/system_prompt.txt")
with open(SYSTEM_PROMPT_PATH, "r") as f:
    SYSTEM_PROMPT = f.read()

# --- Emergency keywords for pre-filtering ---
EMERGENCY_KEYWORDS = [
    "chest pain", "severe shortness of breath", "fainting",
    "unconscious", "severe bleeding", "stroke", "heart attack"
]

def check_emergency(symptoms: str):
    """Return True if text includes high-risk emergency indicators."""
    text = symptoms.lower()
    return any(word in text for word in EMERGENCY_KEYWORDS)


# --- Health Check Route ---
@app.get("/")
async def root():
    return {"message": "✅ API is running", "version": "1.1"}


# --- Core API Route ---
@app.post("/api/symptom-check", response_model=SymptomResponse)
async def symptom_check(input_data: SymptomInput):
    """
    Accepts symptom input, checks for emergencies,
    queries the LLM, parses JSON, stores in DB, and returns structured response.
    """

    # ✅ Basic input validation
    if not input_data.symptoms or len(input_data.symptoms.strip()) < 3:
        raise HTTPException(status_code=400, detail="Please describe your symptoms in detail.")

    # 🚨 Check for emergency cases first
    if check_emergency(input_data.symptoms):
        emergency_response = SymptomResponse(
            conditions=[],
            recommendations=[
                "Call your local emergency number immediately.",
                "Avoid physical exertion until help arrives."
            ],
            triage="🚨 EMERGENCY: Possible life-threatening symptoms detected.",
            disclaimer="This information is for educational purposes only. Seek professional medical care immediately.",
            notes="Detected emergency keyword(s) in symptom input."
        )
        # Log emergency query too
        save_query(input_data.symptoms, emergency_response.dict())
        return emergency_response

    # 🧠 Construct user prompt
    user_prompt = f"""
    Patient info:
    - Symptoms: {input_data.symptoms}
    - Age: {input_data.age or 'unknown'}
    - Sex: {input_data.sex or 'unknown'}
    - Duration: {input_data.duration or 'unknown'}

    Output ONLY valid JSON following the schema in the system prompt.
    """

    # 🔗 Call the LLM
    try:
        raw_output = call_llm(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    # 🧩 Try extracting JSON text from the model output
    match = re.search(r"(\{.*\})", raw_output, re.S)
    if not match:
        raise HTTPException(status_code=500, detail="Failed to parse LLM response as JSON.")
    json_text = match.group(1)

    # 🔍 Parse JSON safely
    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="LLM returned invalid JSON format.")

    # 💾 Save to MongoDB (query + response)
    try:
        save_query(input_data.symptoms, parsed)
    except Exception as e:
        print(f"⚠️ DB Save Warning: {e}")

    # ✅ Return structured response
    return parsed
