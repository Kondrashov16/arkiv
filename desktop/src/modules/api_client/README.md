### Module: `api_client`

#### `rag_desktop_client/src/modules/api_client/README.md`

# API Client Module

## Architecture

The `api_client` module is responsible for abstracting all interactions with the RAG service backend. It provides a clean, promise-based interface for making HTTP requests to the backend endpoints. This module acts as the sole communication layer between the Electron renderer process (via the main process, if necessary, for security or file handling) and the remote RAG service.

It encapsulates the base URL for the backend and handles the structure of requests and responses for the specific RAG service API endpoints.

## How It Works

The `api_client.js` file exports functions that correspond to the RAG service's exposed API endpoints:

1.  **`uploadFile(file)`:**
    * **Purpose:** Sends a file to the RAG service's `/upload` endpoint.
    * **Mechanism:** It takes a `File` object (or similar file representation from the Electron context), constructs a `FormData` object, and performs a `POST` request.
    * **Error Handling:** Catches network errors and API errors, propagating them to the caller.

2.  **`queryLLM(queryText, chatHistory)`:**
    * **Purpose:** Sends a query and the current chat history to the RAG service's `/query` endpoint.
    * **Mechanism:** It takes the `queryText` and `chatHistory` array, constructs a JSON request body, and performs a `POST` request. The `chatHistory` will be formatted appropriately for the LLM context.
    * **Response:** Expects a JSON response containing the `llm_response` and `sources`.
    * **Error Handling:** Catches network errors and API errors.

### Security Considerations

In a real Electron application, direct `Workspace` calls from the renderer process to external APIs can pose security risks if not handled carefully. For this RAG client, given the scope of "single session" and direct interaction with a known backend, we will initially implement direct `Workspace` calls. For production-grade applications, such API calls involving sensitive data or complex file handling should ideally be proxied through the Electron main process using IPC, allowing for better control over network requests and credential management. However, for simplicity and adherence to the requirements, direct `Workspace` from the renderer (enabled by NodeIntegration or contextBridge in Electron) will be used for this project's scope.