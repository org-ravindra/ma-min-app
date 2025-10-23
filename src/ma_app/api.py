import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .orchestrator import Orchestrator

load_dotenv()

app = FastAPI(title="Master Architect Minimal API")

# Allow local Streamlit UI by default
origins = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost",
    "http://127.0.0.1",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orc = Orchestrator()


class GenerateRequest(BaseModel):
    prompt: str
    k: int | None = 4
    model: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
def generate(req: GenerateRequest):
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt is required")
    try:
        result = orc.run(prompt=req.prompt.strip(), k=req.k or 4, model=req.model)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

