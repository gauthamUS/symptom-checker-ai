# app/llm_client.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

def call_llm(system_prompt: str, user_prompt: str):
    """Send prompts to the LLM and return the raw text response."""
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",   # works with GPT-4o / 3.5 / Claude-compatible APIs
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 700,
        "temperature": 0.0
    }

    response = requests.post(LLM_API_URL, json=payload, headers=headers, timeout=30)

    if response.status_code != 200:
        raise Exception(f"LLM call failed: {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]
