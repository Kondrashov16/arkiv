// preload.js

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
    // Expose a function to get environment variables from the main process
    getEnv: (key) => ipcRenderer.invoke('get-env-variable', key),
    // If you need more IPC interactions (e.g., native dialogs), expose them here.
    // Example: showOpenDialog: () => ipcRenderer.invoke('show-open-dialog')
});

// Expose the RAG_SERVICE_URL directly to the renderer's global process.env
// This is a simplification for this example; in a more complex app,
// you might pass specific configs via contextBridge.
window.process = window.process || {};
window.process.env = window.process.env || {};

// Fetch the RAG_SERVICE_URL from main process and make it available
ipcRenderer.invoke('get-env-variable', 'RAG_SERVICE_URL')
    .then(url => {
        window.process.env.RAG_SERVICE_URL = url;
    })
    .catch(error => {
        console.error("Failed to load RAG_SERVICE_URL from main process:", error);
    });