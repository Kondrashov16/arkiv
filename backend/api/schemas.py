# api/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    """
    Request model for querying the LLM.
    """
    query_text: str = Field(..., min_length=1, description="The query text to send to the LLM.")
    # top_k: Optional[int] = Field(default=None, ge=1, le=20, description="Number of context chunks to retrieve. Overrides server default if set.")


class Source(BaseModel):
    """
    Represents a source chunk used as context for the LLM.
    """
    document_name: str
    chunk_id: int # Sequential ID of the chunk within its document
    text_preview: str
    score: Optional[float] = None # Similarity score from vector search (e.g., L2 distance)


class QueryResponse(BaseModel):
    """
    Response model for an LLM query.
    """
    llm_response: str
    sources: List[Source]


class UploadResponse(BaseModel):
    """
    Response model for a file upload.
    """
    filename: str
    message: str
    chunks_added: int
    total_vectors_in_store: int

class ResetResponse(BaseModel):
    """
    Response model for resetting the vector store.
    """
    message: str
    total_vectors_in_store: int
