# imports
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
OLLAMA_URL = "http://ollama:11434/api/generate"  # container-to-container

class GenerateRequest(BaseModel):
    prompt: Optional[str] = None
    query: Optional[str] = None
    model: Optional[str] = "llama3.1:8b"
    stream: Optional[bool] = False  # default to non-streaming for easy JSON parsing

    def text(self) -> str:
        return self.prompt or self.query or (_ for _ in ()).throw(ValueError("Missing prompt/query"))

@router.post("/generate")
def generate(req: GenerateRequest):
    try:
        payload = {"model": req.model, "prompt": req.text(), "stream": bool(req.stream)}
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        r.raise_for_status()

        if req.stream:
            # NDJSON streaming: concatenate chunks' "response" fields
            out = []
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = __import__("json").loads(line)
                    part = obj.get("response", "")
                    if part:
                        out.append(part)
                except Exception:
                    # ignore parse errors on keepalive lines
                    pass
            return {"output": "".join(out)}
        else:
            # Single JSON with "response"
            data = r.json()
            return {"output": data.get("response", "")}

    except requests.HTTPError as e:
        # Surface upstream text to help debugging
        detail = f"Ollama HTTP {e.response.status_code}: {e.response.text}"
        raise HTTPException(status_code=502, detail=detail)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Ollama network error: {e}")
    except Exception as e:
        # (temp) print traceback into container logs
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
