# 🩺 Symptom Checker AI

A simple educational healthcare symptom checker that uses an LLM (Large Language Model) to suggest **possible conditions** and **next steps** based on user symptoms.

## 🚀 How It Works
1. User enters symptoms (and optionally age, sex, duration).
2. Backend sends the data to an LLM with safety prompts.
3. LLM returns possible conditions, recommendations, and an educational disclaimer.
4. Stores the query and response in MongoDB.

## 🧠 Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **LLM:** OpenAI API / compatible endpoint
- **Frontend:** React + Tailwind 

## ⚙️ Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
