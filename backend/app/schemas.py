from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

class IngestRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = None

class IngestResponse(BaseModel):
    repo_id: str
    repo_url: str
    files_indexed: int
    chunks_indexed: int

class ChatRequest(BaseModel):
    repo_id: str
    question: str = Field(min_length=3)
    top_k: int = Field(default=6, ge=1, le=15)

class Citation(BaseModel):
    path: str
    start_line: int
    end_line: int
    score: float

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]

class ReviewRequest(BaseModel):
    repo_id: str
    path: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None

class DocumentationRequest(BaseModel):
    repo_id: str
    path: str
