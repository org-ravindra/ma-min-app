import os
import time
import uuid
from typing import Dict, Any

from .prompts import build_prompt
from .retriever import Retriever
from .llm import LLMClient
from .postprocess import to_sections
from .storage import ArtifactStore


class Orchestrator:
    def __init__(self):
        self.retriever = Retriever()
        self.llm = LLMClient()
        self.store = ArtifactStore()

    def run(self, prompt: str, k: int = 4, model: str | None = None) -> Dict[str, Any]:
        run_id = str(uuid.uuid4())
        t0 = time.time()

        # 1) Retrieve context
        ctx_chunks = self.retriever.search(query=prompt, k=k)

        # 2) Build prompt
        full_prompt = build_prompt(user_prompt=prompt, context_chunks=ctx_chunks)

        # 3) Call LLM
        completion = self.llm.complete(prompt=full_prompt, model=model)

        # 4) Post-process
        sections = to_sections(completion)

        # 5) Persist artifacts
        files = self.store.save_run(
            run_id=run_id,
            prompt=prompt,
            context=ctx_chunks,
            prompt_built=full_prompt,
            output_md=completion,
            sections=sections,
        )

        latency_ms = int((time.time() - t0) * 1000)
        return {
            "run_id": run_id,
            "latency_ms": latency_ms,
            "sections": sections,
            "files": files,
        }

