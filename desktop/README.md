# RAG Desktop Client

This project implements a desktop client for the RAG (Retrieval Augmented Generation) service, built using the Electron framework. It provides a user-friendly interface for interacting with the backend RAG service, enabling file uploads, managing chat sessions, and engaging in contextual conversations powered by a Large Language Model (LLM) through OpenRouter.

## Features

-   **File Upload:** Easily upload PDF, DOCX, and Markdown files to the RAG service for processing and ingestion into the vector store.
-   **Multi-Chat Sessions:** Create and manage multiple independent chat sessions, allowing users to switch between different conversations.
-   **Persistent Chat History (within session):** Each chat session maintains its own history, which is sent to the LLM to preserve conversational context.
-   **ChatGPT-like Interface:** A familiar and intuitive user interface for seamless interaction.
-   **Modular Architecture:** The codebase is organized into well-defined modules for maintainability and scalability.

## Architecture

The application follows a client-server architecture, where the Electron desktop application acts as the client interacting with the FastAPI-based RAG service backend.

```
+---------------------+           +---------------------+
|                     |           |                     |
|  RAG Desktop Client |           |  RAG Service (Backend) |
|   (Electron App)    |           |                     |
|                     |           |   - FastAPI         |
|   - Renderer Process| <-------> |   - File Processing |
|   - Main Process    |           |   - Vector Store    |
|                     |           |   - LLM Integration |
+---------------------+           +---------------------+
       |
       | IPC Communication
       V
+---------------------+
|                     |
|     File System     |
| (Temporary Storage) |
+---------------------+
```

### Electron Processes

-   **Main Process:** The main process is responsible for creating and managing browser windows, handling system events, and performing privileged operations (e.g., file system access, native dialogs). It also acts as an intermediary for secure communication between the renderer process and external resources.
-   **Renderer Process:** Each browser window runs its own renderer process, which is essentially a web page. This is where the user interface (HTML, CSS, JavaScript) resides and user interactions are handled.

### Communication Flow

1.  **Renderer to Main:** User actions (e.g., "Upload File", "Send Message") initiated in the renderer process send IPC (Inter-Process Communication) messages to the main process.
2.  **Main to Backend:** The main process receives the IPC message, performs any necessary preparatory steps (e.g., reading a file), and then makes HTTP requests to the RAG service backend API.
3.  **Backend Response to Main:** The RAG service processes the request and sends an HTTP response back to the main process.
4.  **Main to Renderer:** The main process then forwards the backend's response (or a processed version of it) back to the renderer process via IPC.
5.  **Renderer Update:** The renderer process updates the UI based on the received data.

## Project Structure

```
rag_desktop_client/
├── main.js                 # Electron Main Process entry point
├── package.json            # Project dependencies and scripts
├── src/
│   ├── index.html          # Main HTML for the renderer process
│   ├── renderer.js         # Renderer Process entry point (UI logic)
│   ├── styles.css          # Application styles
│   ├── modules/            # UI components and logic
│   │   ├── chat/
│   │   │   ├── chat.js     # Chat component logic
│   │   │   ├── chat.css    # Chat component styles
│   │   │   └── README.md   # Module README
│   │   ├── file_upload/
│   │   │   ├── file_upload.js # File upload logic
│   │   │   └── README.md   # Module README
│   │   ├── api_client/
│   │   │   ├── api_client.js # Handles communication with RAG service
│   │   │   └── README.md   # Module README
│   │   └── chat_manager/
│   │       ├── chat_manager.js # Manages chat sessions and history
│   │       └── README.md   # Module README
├── .env.example            # Example for environment variables (for frontend, e.g., backend URL)
└── README.md               # This file
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    # git clone <repository_url>
    # cd rag_desktop_client
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Configure Backend URL:**
    Create a `.env` file in the root directory and add the URL of your running RAG service backend:
    ```
    RAG_SERVICE_URL="http://127.0.0.1:8000"
    ```
    *Ensure your RAG service is running as per its `README.md`.*

## Running the Application

To start the Electron application, run:

```bash
npm start
```

## How to Use

1.  **Start the RAG Backend Service:** Ensure your RAG service is running on the specified URL (default: `http://127.0.0.1:8000`).
2.  **Launch the Desktop Client:** Run `npm start` in the `rag_desktop_client` directory.
3.  **Upload Documents:** Use the "Upload File" functionality to send PDF, DOCX, or Markdown files to the RAG service.
4.  **Start a New Chat:** Create a new chat session.
5.  **Query the LLM:** Type your questions in the chat input and send them. The application will use the uploaded documents as context for the LLM.
6.  **View Responses and Sources:** The LLM's response will be displayed, along with the source document chunks used to generate the answer.