from fastapi import FastAPI

app = FastAPI(title="Symptom Checker API")

@app.get("/")
async def health():
    return {"message": "✅ API is running", "status": "healthy"}
