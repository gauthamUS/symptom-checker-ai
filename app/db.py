from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client.symptom_checker

def save_query(symptoms_text, response):
    db.consultations.insert_one({
        "symptoms": symptoms_text,
        "response": response,
        "timestamp": datetime.utcnow()
    })
