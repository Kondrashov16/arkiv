// renderer.js - Electron Renderer Process

console.log("Starting to import modules...");

import { initChat } from './modules/chat/chat.js';
console.log("initChat imported:", typeof initChat);

import { initFileUpload } from './modules/file_upload/file_upload.js';
console.log("initFileUpload imported:", typeof initFileUpload);

import { createChatSession, setActiveChatId, getActiveChatId } from './modules/chat_manager/chat_manager.js';
console.log("Chat manager functions imported:", { 
    createChatSession: typeof createChatSession, 
    setActiveChatId: typeof setActiveChatId, 
    getActiveChatId: typeof getActiveChatId 
});

document.addEventListener('DOMContentLoaded', async () => {
    console.log("DOMContentLoaded event fired");
    console.log("Available globals:", { electron: !!window.electron, appConfig: !!window.appConfig });
    
    try {
        // Load RAG_SERVICE_URL from main process
        console.log("Getting RAG_SERVICE_URL from main process...");
        const ragServiceUrl = await window.electron.getEnv('RAG_SERVICE_URL');
        
        // Use fallback URL if environment variable is not set
        const finalUrl = ragServiceUrl || 'http://127.0.0.1:8000';
        
        // Set the URL in global config
        if (window.appConfig && window.appConfig.setRagServiceUrl) {
            window.appConfig.setRagServiceUrl(finalUrl);
        }
        
        console.log("RAG Service URL from env:", ragServiceUrl);
        console.log("Final RAG Service URL:", finalUrl);
        console.log("appConfig after setting URL:", window.appConfig);

        // Initialize chat and file upload modules
        console.log("Initializing chat module...");
        initChat(
            'chat-container',
            'message-input',
            'send-message-button',
            'new-chat-button',
            'chat-list',
            'upload-status'
        );
        
        console.log("Initializing file upload module...");
        initFileUpload(
            'upload-button',
            'file-input',
            'upload-status'
        );
        
        console.log("Modules initialized successfully");

        // Ensure there's at least one chat session active on startup
        // This logic is also in chat_manager, but re-calling here for clarity/robustness
        if (!getActiveChatId()) {
            const initialChatId = createChatSession();
            setActiveChatId(initialChatId);
            // initChat will handle rendering the history for this active chat
        }
    } catch (error) {
        console.error('Failed to initialize application:', error);
    }
});