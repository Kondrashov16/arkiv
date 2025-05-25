# api/endpoints.py
import os
import shutil
import traceback # For detailed error logging

from fastapi import APIRouter, File, UploadFile, HTTPException, Body
from fastapi.responses import JSONResponse

from core.config import settings
from .schemas import QueryRequest, QueryResponse, Source, UploadResponse, ResetResponse

from file_processing.extractor import extract_text
from file_processing.chunking import chunk_text_by_tokens, get_tiktoken_tokenizer
from vector_store.store import VectorStore
from llm_interface.openrouter_client import OpenRouterClient

# --- Initialize shared components ---
# These are initialized once when the module is loaded (i.e., when the app starts)

try:
    # Initialize tokenizer globally for chunking
    tokenizer = get_tiktoken_tokenizer() # Uses default from chunking.py (cl100k_base)
    
    # Initialize VectorStore
    # This will load the embedding model, which can take a few seconds
    print("Initializing VectorStore...")
    vector_db = VectorStore(embedding_model_name=settings.EMBEDDING_MODEL_NAME)
    print("VectorStore initialized.")

    # Initialize LLM Client
    print("Initializing OpenRouterClient...")
    llm_client = OpenRouterClient(
        api_key=settings.OPENROUTER_API_KEY,
        model_name=settings.OPENROUTER_MODEL_NAME
    )
    print("OpenRouterClient initialized.")

except Exception as e:
    print(f"FATAL: Error during initialization of shared components: {e}")
    print(traceback.format_exc())
    # Depending on the app's resilience strategy, you might want to exit or raise a specific error
    # For now, if these fail, subsequent API calls will likely fail.
    # A more robust app might have health checks.
    tokenizer = None
    vector_db = None
    llm_client = None
    print("WARNING: One or more critical components failed to initialize. API may not function correctly.")


router = APIRouter(prefix="/api/v1")


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a file (PDF, DOCX, MD), processes it, and adds its content to the vector store.
    """
    if not all([vector_db, tokenizer]): # Check if critical components initialized
        raise HTTPException(status_code=503, detail="Service temporarily unavailable due to initialization error.")

    # Ensure the upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    temp_file_path = os.path.join(settings.UPLOAD_DIR, file.filename)

    try:
        # Save the uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"File '{file.filename}' saved to '{temp_file_path}'")

        # 1. Extract text
        print(f"Extracting text from '{file.filename}'...")
        raw_text = extract_text(temp_file_path, file.filename) # Pass original filename for type detection
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail=f"No text could be extracted from file '{file.filename}'. It might be empty or corrupted.")
        print(f"Extracted {len(raw_text)} characters.")

        # 2. Chunk text
        print("Chunking text...")
        text_chunks = chunk_text_by_tokens(
            raw_text,
            tokenizer, # Pass the global tokenizer instance
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        if not text_chunks:
            # This could happen if raw_text was only whitespace after strip, or some other edge case
            return UploadResponse(
                filename=file.filename,
                message="File processed, but no valid text chunks were generated (text might be too short or only whitespace).",
                chunks_added=0,
                total_vectors_in_store=vector_db.get_total_vectors()
            )
        print(f"Created {len(text_chunks)} chunks.")

        # 3. Add to VectorStore
        print("Adding chunks to VectorStore...")
        vector_db.add_documents(text_chunks, file.filename)
        
        return UploadResponse(
            filename=file.filename,
            message="File processed and content added to vector store successfully.",
            chunks_added=len(text_chunks),
            total_vectors_in_store=vector_db.get_total_vectors()
        )

    except ValueError as ve: # Specific errors from our processing (e.g., unsupported file type)
        print(f"ValueError during upload: {ve}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException: # Re-raise HTTPExceptions
        raise
    except Exception as e:
        print(f"Unexpected error during file upload and processing: {e}")
        print(traceback.format_exc())
        # Log the full error for debugging
        # logger.error(f"Error processing {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred processing the file: {str(e)}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                print(f"Temporary file '{temp_file_path}' removed.")
            except OSError as oe:
                print(f"Error removing temporary file '{temp_file_path}': {oe}")
                # logger.warning(f"Could not remove temp file {temp_file_path}: {oe}")


@router.post("/query", response_model=QueryResponse)
async def query_llm_with_context(request: QueryRequest = Body(...)):
    """
    Queries the LLM with context retrieved from the vector store based on the query text.
    """
    if not all([vector_db, llm_client]): # Check if critical components initialized
        raise HTTPException(status_code=503, detail="Service temporarily unavailable due to initialization error.")

    query_text = request.query_text
    # top_k_override = request.top_k # If you add top_k to QueryRequest

    print(f"Received query: '{query_text[:100]}...'")

    try:
        # 1. Search VectorStore for relevant context
        # k_to_retrieve = top_k_override if top_k_override is not None else settings.MAX_CONTEXT_CHUNKS
        k_to_retrieve = settings.MAX_CONTEXT_CHUNKS
        
        context_chunks_data = []
        if vector_db.get_total_vectors() > 0:
            context_chunks_data = vector_db.search(query_text, k=k_to_retrieve)
            print(f"Retrieved {len(context_chunks_data)} context chunks from VectorStore.")
        else:
            print("VectorStore is empty. Querying LLM without document context.")
        
        # Prepare sources for the response (even if LLM call fails later)
        sources_for_response = [
            Source(
                document_name=chunk["document_name"],
                chunk_id=chunk["chunk_id"],
                text_preview=chunk["text_preview"],
                score=chunk.get("score") 
            ) for chunk in context_chunks_data
        ]

        # 2. Query LLM with context
        print("Querying LLM...")
        # context_chunks_data is already in the format needed by llm_client.query_llm
        # (list of dicts with 'document_name', 'chunk_id', 'text_preview')
        llm_response_text = llm_client.query_llm(query_text, context_chunks_data)
        print("LLM query successful.")

        return QueryResponse(
            llm_response=llm_response_text,
            sources=sources_for_response
        )

    except HTTPException: # Re-raise HTTPExceptions
        raise
    except Exception as e:
        print(f"Error during LLM query processing: {e}")
        print(traceback.format_exc())
        # logger.error(f"Error processing query '{query_text}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred while processing your query: {str(e)}")


@router.post("/reset-vector-store", response_model=ResetResponse)
async def reset_vector_store_endpoint():
    """
    Resets the in-memory vector store, clearing all loaded documents and embeddings.
    Useful for testing purposes.
    """
    if not vector_db:
         raise HTTPException(status_code=503, detail="VectorStore not initialized.")
    try:
        vector_db.reset()
        return ResetResponse(
            message="Vector store has been successfully reset.",
            total_vectors_in_store=vector_db.get_total_vectors()
        )
    except Exception as e:
        print(f"Error resetting vector store: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Could not reset vector store: {str(e)}")

# You might want to add a health check endpoint
@router.get("/health")
async def health_check():
    # Basic health check, can be expanded
    if vector_db and llm_client and tokenizer:
        return {"status": "ok", "message": "All core components seem initialized."}
    
    missing = []
    if not vector_db: missing.append("VectorStore")
    if not llm_client: missing.append("LLMClient")
    if not tokenizer: missing.append("Tokenizer")
    return JSONResponse(
        status_code=503,
        content={"status": "error", "message": f"Core components not initialized: {', '.join(missing)}"}
    )

