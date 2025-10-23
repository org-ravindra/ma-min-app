import os
from typing import Optional
import httpx
from openai import OpenAI


class LLMClient:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        else:
            # Ollama (local): assumes daemon on localhost:11434
            self.client = None
            self.default_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            self.ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")

    def complete(self, prompt: str, model: Optional[str] = None) -> str:
        if self.provider == "openai":
            mdl = model or self.default_model
            resp = self.client.chat.completions.create(
                model=mdl,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return resp.choices[0].message.content or ""
        else:
            # Ollama simple generate
            mdl = model or self.default_model
            payload = {"model": mdl, "prompt": prompt, "stream": False, "options": {"temperature": 0.2}}
            with httpx.Client(timeout=120) as s:
                r = s.post(self.ollama_url, json=payload)
                r.raise_for_status()
                data = r.json()
                return data.get("response", "")

