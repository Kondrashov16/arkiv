# main.py
from fastapi import FastAPI
from api.endpoints import router as api_v1_router # Use the renamed import
from core.config import settings # To ensure config is loaded early, and for UPLOAD_DIR creation
import os

# --- Application Metadata (Optional) ---
description = """
RAG Service API for uploading documents and querying an LLM with context. 🚀

You can:
* **Upload documents** (PDF, DOCX, MD) to be processed and stored.
* **Query the LLM** using the content of your uploaded documents as context.
* **Reset the document store** (for testing).
"""

app = FastAPI(
    title="RAG Service with OpenRouter",
    description=description,
    version="0.1.0",
    contact={
        "name": "AI Services Team",
        "url": "http://example.com/contact", # Replace with actual contact/repo
        "email": "dev@example.com", # Replace
    },
    license_info={
        "name": "MIT License", # Or your chosen license
        "url": "https://opensource.org/licenses/MIT",
    },
)

# --- Include API Routers ---
app.include_router(api_v1_router) # This router is already prefixed with /api/v1

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint providing a welcome message and link to API docs.
    """
    return {
        "message": "Welcome to the RAG Service API!",
        "documentation": "/docs",
        "health_check": "/api/v1/health" # Assuming health is under the v1 router
    }

# --- Server Startup Event (Optional) ---
@app.on_event("startup")
async def startup_event():
    """
    Actions to perform when the application starts up.
    - Ensures upload directory exists.
    - (Components like VectorStore, LLMClient are initialized when api.endpoints is imported)
    """
    print("Application startup...")
    # Ensure upload directory exists (also done in config, but good to double-check)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    print(f"Upload directory: {settings.UPLOAD_DIR}")
    print(f"OpenRouter Model: {settings.OPENROUTER_MODEL_NAME}")
    print(f"Embedding Model: {settings.EMBEDDING_MODEL_NAME}")
    print("RAG Service is ready to accept requests.")
    print(f"API documentation available at: http://127.0.0.1:8000/docs (if running locally on port 8000)")

# --- Server Shutdown Event (Optional) ---
@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform when the application shuts down.
    (e.g., save in-memory data if persistence was implemented)
    """
    print("Application shutdown...")
    # If vector_db had a save method:
    # from api.endpoints import vector_db # Get the instance
    # if vector_db and hasattr(vector_db, 'save_to_disk'):
    #     vector_db.save_to_disk("path/to/save/index_and_map")
    #     print("VectorStore data saved.")
    print("RAG Service has shut down.")


if __name__ == "__main__":
    import uvicorn
    # This is for direct execution (python main.py)
    # Typically, you'd run with `uvicorn main:app --reload` from the terminal
    print("Starting server with Uvicorn directly from main.py (for development)...")
    uvicorn.run(app, host="127.0.0.1", port=8000)

