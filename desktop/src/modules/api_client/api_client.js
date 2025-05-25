// rag_desktop_client/src/modules/api_client/api_client.js

// Get RAG service URL from global config set by renderer
function getRagServiceUrl() {
    return window.appConfig?.ragServiceUrl || 'http://127.0.0.1:8000';
}

const API_VERSION = 'v1'; // Assuming backend API version

/**
 * Uploads a file to the RAG service.
 * @param {File} file - The file object to upload.
 * @returns {Promise<Object>} - A promise that resolves with the API response.
 */
export async function uploadFile(file) {
    const url = `${getRagServiceUrl()}/api/${API_VERSION}/upload`; // Backend upload endpoint
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'File upload failed');
        }

        return await response.json();
    } catch (error) {
        console.error('Error uploading file:', error);
        throw error;
    }
}

/**
 * Queries the LLM through the RAG service with context.
 * @param {string} queryText - The user's current query.
 * @param {Array<Object>} chatHistory - An array of previous messages in the chat, formatted as [{role: "user", content: "..."}].
 * @returns {Promise<Object>} - A promise that resolves with the LLM's response and sources.
 */
export async function queryLLM(queryText, chatHistory) {
    const url = `${getRagServiceUrl()}/api/${API_VERSION}/query`; // Backend query endpoint

    // Construct the messages for the LLM. The RAG service will handle the final prompt construction
    // including injecting relevant document chunks. We send the raw chat history for context.
    const messages = chatHistory.map(msg => ({
        role: msg.role,
        content: msg.content
    }));

    // Add the current user query to the messages to send as part of the context
    messages.push({ role: 'user', content: queryText });

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query_text: queryText, // Send the current query explicitly
                chat_history: messages // Send the full chat history for context
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'LLM query failed');
        }

        return await response.json();
    } catch (error) {
        console.error('Error querying LLM:', error);
        throw error;
    }
}