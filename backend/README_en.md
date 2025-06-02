# RAG Service with OpenRouter

This project implements a Retrieval Augmented Generation (RAG) service that allows you to upload documents (PDF, DOCX, MD), process them, store their content in a vector database, and then query a Large Language Model (LLM) via OpenRouter, using the ingested documents as context.

## Features

-   **File Upload:** Endpoint to upload and process PDF, DOCX, and Markdown files.
-   **Text Extraction & Chunking:** Extracts text from files and splits it into manageable chunks.
-   **Vector Embeddings:** Generates embeddings for text chunks using Sentence Transformers.
-   **Vector Store:** Uses FAISS for efficient similarity search of text chunks.
-   **LLM Integration:** Queries an LLM on OpenRouter, providing relevant context from your documents.
-   **Source Attribution:** Returns the LLM's response along with the specific document chunks used as sources.
-   **Modular Design:** Code is organized into logical modules, each with its own README.
-   **API-driven:** Uses FastAPI to expose endpoints for file upload and querying.

## Project Structure


rag_service/
├── main.py                 # FastAPI app initialization and server start
├── api/                    # Handles API endpoints and schemas
│   ├── endpoints.py
│   ├── schemas.py
│   └── README.md
├── file_processing/        # Handles text extraction and chunking
│   ├── extractor.py
│   ├── chunking.py
│   └── README.md
├── vector_store/           # Manages vector embeddings and search
│   ├── store.py
│   └── README.md
├── llm_interface/          # Interacts with the OpenRouter LLM
│   ├── openrouter_client.py
│   └── README.md
├── core/                   # Core configuration and shared utilities
│   ├── config.py
│   └── README.md
├── storage/                # Directory for uploaded files (created automatically)
│   └── uploads/
├── .env.example            # Example for environment variables
├── requirements.txt        # Python dependencies
└── README.md               # This file


## Setup and Installation

1.  **Clone the repository (or create the files as provided):**
    ```bash
    # If you had a git repo:
    # git clone <repository_url>
    # cd rag_service
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Copy `.env.example` to a new file named `.env` and fill in your details:
    ```
    OPENROUTER_API_KEY="your_openrouter_api_key_here"
    # You can find models at [https://openrouter.ai/docs#models](https://openrouter.ai/docs#models)
    # Example: "mistralai/mistral-7b-instruct" or "openai/gpt-3.5-turbo"
    OPENROUTER_MODEL_NAME="mistralai/mistral-7b-instruct"
    EMBEDDING_MODEL_NAME="all-MiniLM-L6-v2"
    ```
    Replace `"your_openrouter_api_key_here"` with your actual OpenRouter API key. You can choose any model available on OpenRouter.

## Running the Service

1.  **Start the FastAPI server:**
    ```bash
    uvicorn main:app --reload
    ```
    The server will typically start on `http://127.0.0.1:8000`.

## API Endpoints

The API documentation (Swagger UI) will be available at `http://127.0.0.1:8000/docs` when the server is running.

1.  **Upload File:**
    * **Endpoint:** `POST /upload`
    * **Request:** `multipart/form-data` with a file.
    * **Response:** Confirmation message.
    * **Example using cURL:**
        ```bash
        curl -X POST -F "file=@/path/to/your/document.pdf" [http://127.0.0.1:8000/api/v1/upload](http://127.0.0.1:8000/api/v1/upload)
        ```

2.  **Query LLM:**
    * **Endpoint:** `POST /query`
    * **Request Body (JSON):**
        ```json
        {
          "query_text": "What is the main topic of the document?"
        }
        ```
    * **Response Body (JSON):**
        ```json
        {
          "llm_response": "The main topic of the document appears to be...",
          "sources": [
            {
              "document_name": "document.pdf",
              "chunk_id": 0,
              "text_preview": "This document discusses various aspects of..."
            },
            // ... other relevant sources
          ]
        }
        ```
    * **Example using cURL:**
        ```bash
        curl -X POST -H "Content-Type: application/json" \
             -d '{"query_text": "What are the key findings?"}' \
             [http://127.0.0.1:8000/api/v1/query](http://127.0.0.1:8000/api/v1/query)
        ```

## Modules

Each module has its own `README.md` file in its respective directory, detailing its architecture and functionality.

-   `api/README.md`
-   `core/README.md`
-   `file_processing/README.md`
-   `llm_interface/README.md`
-   `vector_store/README.md`

## Notes

* The vector store (FAISS index and document metadata) is currently stored in memory. For persistence across server restarts, you would need to implement saving/loading the FAISS index and the document map to disk.
* The `storage/uploads` directory is used to temporarily store uploaded files during processing.
* Ensure your OpenRouter API key has enough credits and the selected model is appropriate for your needs.
