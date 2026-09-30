from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import hashlib
import io
import zipfile
import httpx

EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".kts", ".go", ".rs",
    ".cpp", ".cc", ".cxx", ".c", ".h", ".hpp", ".cs", ".php", ".rb", ".swift",
    ".scala", ".sql", ".sh", ".md", ".mdx", ".json", ".yaml", ".yml", ".toml",
    ".ini", ".cfg", ".xml", ".html", ".css", ".scss", ".dockerfile"
}
SKIP_DIRS = {
    ".git", "node_modules", "venv", ".venv", "dist", "build", "target",
    "__pycache__", ".next", "coverage"
}
SKIP_NAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Cargo.lock"
}

@dataclass
class SourceFile:
    path: str
    content: str

def parse_github(url: str) -> tuple[str, str]:
    p = urlparse(url)
    if p.netloc.lower() not in {"github.com", "www.github.com"}:
        raise ValueError("Only github.com repository URLs are supported")
    parts = [x for x in p.path.split("/") if x]
    if len(parts) < 2:
        raise ValueError("Expected https://github.com/<owner>/<repo>")
    return parts[0], parts[1].removesuffix(".git")

def repo_id(url: str) -> str:
    return hashlib.sha1(url.rstrip("/").encode()).hexdigest()[:12]

def fetch_repository(url: str, branch: str | None = None) -> tuple[str, str, str]:
    owner, repo = parse_github(url)
    ref = branch or "HEAD"
    api = f"https://api.github.com/repos/{owner}/{repo}/zipball/{ref}"
    with httpx.Client(
        timeout=60,
        follow_redirects=True,
        headers={"User-Agent": "RepoMind/1.0"},
    ) as client:
        r = client.get(api)
        r.raise_for_status()
        return owner, repo, r.content

def extract_source_files(blob: bytes, max_file_bytes: int) -> list[SourceFile]:
    files: list[SourceFile] = []
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for name in z.namelist():
            p = Path(name)
            parts = set(p.parts)
            if parts & SKIP_DIRS or p.name in SKIP_NAMES or p.is_dir():
                continue
            if (
                p.suffix.lower() not in EXTENSIONS
                and p.name.lower() not in {"dockerfile", "makefile"}
            ):
                continue
            info = z.getinfo(name)
            if info.file_size > max_file_bytes:
                continue
            raw = z.read(name)
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
            rel = "/".join(p.parts[1:]) if len(p.parts) > 1 else p.name
            files.append(SourceFile(rel, text))
    return files
