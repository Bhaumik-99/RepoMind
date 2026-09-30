from .store import RepoIndex
from ..llm.client import LLMClient

def build_context(results: list[dict]) -> str:
    blocks = []
    for i, r in enumerate(results, 1):
        blocks.append(f"SOURCE {i}: [{r['path']}:{r['start_line']}-{r['end_line']}]\n{r['content']}")
    return "\n\n".join(blocks)

def answer(repo_id: str, question: str, top_k: int = 6):
    store = RepoIndex(repo_id)
    results = store.search(question, top_k)
    context = build_context(results)
    prompt = f"""Repository context:
{context}

Question:
{question}

Give a concise engineering answer. Reference the exact supplied sources using [path:start-end]."""
    response = LLMClient().generate(prompt)
    return response, results

def review(repo_id: str, path: str, start_line: int | None = None, end_line: int | None = None):
    store = RepoIndex(repo_id)
    hits = store.search(f"code review for {path}", 10)
    hits = [h for h in hits if h["path"] == path] or hits[:3]
    if start_line and end_line:
        hits = [h for h in hits if not (h["end_line"] < start_line or h["start_line"] > end_line)] or hits
    context = build_context(hits)
    prompt = f"Review this repository code for correctness, security, reliability, performance, and maintainability. Do not invent findings.\n\n{context}"
    return LLMClient().generate(prompt)

def generate_docs(repo_id: str, path: str):
    store = RepoIndex(repo_id)
    hits = [h for h in store.search(f"documentation for {path}", 10) if h["path"] == path]
    context = build_context(hits[:6] or store.search(path, 6))
    prompt = f"Generate concise developer documentation for module {path}. Include purpose, inputs/outputs, important functions/classes, dependencies, and usage notes. Cite the supplied sources.\n\n{context}"
    return LLMClient().generate(prompt)
