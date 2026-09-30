from functools import lru_cache
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai").lower()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))
    max_file_bytes: int = int(os.getenv("MAX_FILE_BYTES", "300000"))
    chunk_lines: int = int(os.getenv("CHUNK_LINES", "80"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "15"))

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.ensure_dirs()
    return s
