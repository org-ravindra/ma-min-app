from textwrap import dedent
from typing import List

SYSTEM_PRIMER = dedent(
    """
    You are Master Architect, an expert who produces concise, structured, reviewable architecture documents.
    - Prefer clear section headings.
    - Provide a short high-level diagram in Mermaid where helpful.
    - Cite assumptions explicitly.
    - Keep choices cost-aware and minimal for an initial version; call out scale-up options.
    """
)


def build_prompt(user_prompt: str, context_chunks: List[str]) -> str:
    context_block = "\n\n".join(context_chunks) if context_chunks else ""
    return dedent(
        f"""
        [SYSTEM]
        {SYSTEM_PRIMER}

        [CONTEXT]
        The following reference snippets may be useful (they can be partial excerpts):
        ---
        {context_block}
        ---

        [TASK]
        Produce a minimal, production-minded architecture for the user's request.
        Include: key components, data flow, trade-offs, a Mermaid diagram if appropriate, and a short checklist.

        [USER REQUEST]
        {user_prompt}
        """
    ).strip()

