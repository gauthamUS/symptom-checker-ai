# app/main.py
from fastapi import FastAPI, HTTPException
from app.models import SymptomInput, SymptomResponse
from app.llm_client import call_llm
import json, re, os

app = FastAPI(title="Symptom Checker API", version="1.0")

# Load system prompt from file
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/system_prompt.txt")
with open(SYSTEM_PROMPT_PATH, "r") as f:
    SYSTEM_PROMPT = f.read()

# --- Utility: emergency keyword check ---
EMERGENCY_KEYWORDS = [
    "chest pain", "severe shortness of breath", "fainting",
    "unconscious", "severe bleeding", "stroke", "heart attack"
]

def check_emergency(symptoms: str):
    text = symptoms.lower()
    for word in EMERGENCY_KEYWORDS:
        if word in text:
            return True
    return False

# --- Routes ---
@app.get("/")
async def root():
    return {"message": "✅ API is running", "version": "1.0"}

@app.post("/api/symptom-check", response_model=SymptomResponse)
async def symptom_check(input_data: SymptomInput):
    """Analyze symptoms using the LLM and return possible conditions."""

    if not input_data.symptoms or len(input_data.symptoms.strip()) < 3:
        raise HTTPException(status_code=400, detail="Please describe your symptoms.")

    # Check for emergency
    if check_emergency(input_data.symptoms):
        return SymptomResponse(
            conditions=[],
            recommendations=[],
            triage="🚨 EMERGENCY: Please seek immediate medical care.",
            disclaimer="For educational purposes only.",
            notes="Detected possible emergency keywords."
        )

    # Prepare user prompt
    user_prompt = f"""
    Patient info:
    - Symptoms: {input_data.symptoms}
    - Age: {input_data.age or 'unknown'}
    - Sex: {input_data.sex or 'unknown'}
    - Duration: {input_data.duration or 'unknown'}

    Output ONLY valid JSON following the schema in the system prompt.
    """

    try:
        raw_output = call_llm(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    # Try extracting JSON
    match = re.search(r"(\{.*\})", raw_output, re.S)
    if not match:
        raise HTTPException(status_code=500, detail="Failed to parse LLM response as JSON.")
    json_text = match.group(1)

    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="LLM returned invalid JSON format.")

    return parsed
