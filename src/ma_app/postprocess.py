import re
from typing import List, Dict, Any


MERMAID_RE = re.compile(r"```mermaid\n(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_mermaid(md: str) -> List[str]:
    return MERMAID_RE.findall(md)


def to_sections(md: str) -> List[Dict[str, Any]]:
    # naive sectionizer: split by top-level headings
    sections: List[Dict[str, Any]] = []
    current = {"title": "Overview", "body": []}
    for line in md.splitlines():
        if line.startswith("# "):
            if current["body"]:
                current["body"] = "\n".join(current["body"]).strip()
                sections.append(current)
            current = {"title": line[2:].strip(), "body": []}
        else:
            current["body"].append(line)
    if current["body"]:
        current["body"] = "\n".join(current["body"]).strip()
        sections.append(current)

    # attach mermaid blocks (if any)
    mermaid_blocks = extract_mermaid(md)
    if mermaid_blocks:
        sections.append({"title": "Diagram(s)", "body": "\n\n".join([f"```mermaid\n{x}\n```" for x in mermaid_blocks])})

    # short checklist heuristic
    checklist = [
        "Confirm assumptions & NFRs",
        "Define minimal data flow and storage",
        "Add observability (logs/metrics)",
        "Plan auth & RBAC for next iteration",
        "Write runbook and cost guardrails",
    ]
    sections.append({"title": "Checklist", "body": "\n".join([f"- [ ] {c}" for c in checklist])})
    return sections


