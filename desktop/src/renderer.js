// renderer.js - Electron Renderer Process

import { initChat } from './modules/chat/chat.js';
import { initFileUpload } from './modules/file_upload/file_upload.js';
import { createChatSession, setActiveChatId, getActiveChatId } from './modules/chat_manager/chat_manager.js';

document.addEventListener('DOMContentLoaded', async () => {
    // Dynamically set RAG_SERVICE_URL from the preload script/main process
    // This assumes `window.process.env.RAG_SERVICE_URL` is set by preload.js
    // Alternatively, you could use `window.electron.getEnv('RAG_SERVICE_URL')` here.
    // For simplicity, directly accessing `process.env` after preload has populated it.
    console.log("RAG Service URL:", process.env.RAG_SERVICE_URL);

    // Initialize chat and file upload modules
    initChat(
        'chat-container',
        'message-input',
        'send-message-button',
        'new-chat-button',
        'chat-list',
        'upload-status'
    );
    initFileUpload(
        'upload-button',
        'file-input',
        'upload-status'
    );

    // Ensure there's at least one chat session active on startup
    // This logic is also in chat_manager, but re-calling here for clarity/robustness
    if (!getActiveChatId()) {
        const initialChatId = createChatSession();
        setActiveChatId(initialChatId);
        // initChat will handle rendering the history for this active chat
    }
});