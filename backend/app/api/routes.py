from fastapi import APIRouter, HTTPException
from ..schemas import *
from ..config import get_settings
from ..ingestion.repository import fetch_repository, extract_source_files, repo_id
from ..ingestion.chunker import chunk_file
from ..rag.store import RepoIndex
from ..rag.pipeline import answer, review, generate_docs

router = APIRouter(prefix="/api")

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/repos/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    try:
        rid = repo_id(str(req.repo_url))
        _, _, blob = fetch_repository(str(req.repo_url), req.branch)
        files = extract_source_files(blob, get_settings().max_file_bytes)
        chunks = []
        for f in files:
            chunks.extend(chunk_file(
                f.path,
                f.content,
                get_settings().chunk_lines,
                get_settings().chunk_overlap,
            ))
        if not chunks:
            raise ValueError("No supported source files were found")
        RepoIndex(rid).build(chunks)
        return IngestResponse(
            repo_id=rid,
            repo_url=str(req.repo_url),
            files_indexed=len(files),
            chunks_indexed=len(chunks),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/repos/{repo_id}/files")
def files(repo_id: str):
    try:
        items = RepoIndex(repo_id).metadata
        return {"files": sorted({x["path"] for x in items})}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        text, results = answer(req.repo_id, req.question, req.top_k)
        return ChatResponse(
            answer=text,
            citations=[
                Citation(
                    path=r["path"],
                    start_line=r["start_line"],
                    end_line=r["end_line"],
                    score=r["score"],
                )
                for r in results
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/review")
def code_review(req: ReviewRequest):
    try:
        return {"review": review(req.repo_id, req.path, req.start_line, req.end_line)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/docs/generate")
def docs(req: DocumentationRequest):
    try:
        return {"documentation": generate_docs(req.repo_id, req.path)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
