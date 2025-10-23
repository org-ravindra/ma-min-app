import json
import os
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
RUNS_DIR = DATA_DIR / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)


class ArtifactStore:
    def save_run(
        self,
        run_id: str,
        prompt: str,
        context: List[str],
        prompt_built: str,
        output_md: str,
        sections: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        run_dir = RUNS_DIR / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        files = []
        (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        files.append({"name": "prompt.txt", "path": str(run_dir / "prompt.txt")})

        (run_dir / "context.json").write_text(json.dumps(context, indent=2), encoding="utf-8")
        files.append({"name": "context.json", "path": str(run_dir / "context.json")})

        (run_dir / "built_prompt.txt").write_text(prompt_built, encoding="utf-8")
        files.append({"name": "built_prompt.txt", "path": str(run_dir / "built_prompt.txt")})

        (run_dir / "output.md").write_text(output_md, encoding="utf-8")
        files.append({"name": "output.md", "path": str(run_dir / "output.md")})

        (run_dir / "sections.json").write_text(json.dumps(sections, indent=2), encoding="utf-8")
        files.append({"name": "sections.json", "path": str(run_dir / "sections.json")})

        # Optional: a simple trace
        trace = {"run_id": run_id, "files": files}
        (run_dir / "trace.json").write_text(json.dumps(trace, indent=2), encoding="utf-8")
        files.append({"name": "trace.json", "path": str(run_dir / "trace.json")})

        return files

