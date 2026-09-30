import httpx
from openai import OpenAI
from ..config import get_settings

SYSTEM = """You are RepoMind, a codebase analysis assistant. Answer only from the supplied repository context when possible. Be explicit when context is insufficient. Cite files using [path:start-end] markers that correspond to supplied context. Do not invent file paths or code."""

class LLMClient:
    def __init__(self):
        self.s = get_settings()

    def generate(self, prompt: str) -> str:
        if self.s.llm_provider == "ollama":
            return self._ollama(prompt)
        if not self.s.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured. Set LLM_PROVIDER=ollama for local inference.")
        client = OpenAI(api_key=self.s.openai_api_key, base_url=self.s.openai_base_url)
        resp = client.chat.completions.create(
            model=self.s.openai_model,
            temperature=0.1,
            messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or "No answer generated."

    def _ollama(self, prompt: str) -> str:
        r = httpx.post(
            f"{self.s.ollama_base_url.rstrip('/')}/api/chat",
            json={"model": self.s.ollama_model, "stream": False,
                  "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]},
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]
