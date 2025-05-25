// preload.js

const { contextBridge, ipcRenderer } = require('electron');

// Expose electron APIs to renderer process
contextBridge.exposeInMainWorld('electron', {
    // Expose a function to get environment variables from the main process
    getEnv: async (key) => {
        try {
            return await ipcRenderer.invoke('get-env-variable', key);
        } catch (error) {
            console.error(`Error getting environment variable '${key}':`, error);
            return null;
        }
    },
    // If you need more IPC interactions (e.g., native dialogs), expose them here.
    // Example: showOpenDialog: () => ipcRenderer.invoke('show-open-dialog')
});

// Create a mutable config object
const appConfig = {
    ragServiceUrl: null
};

// Expose a global config object that will be populated by renderer
contextBridge.exposeInMainWorld('appConfig', {
    get ragServiceUrl() {
        return appConfig.ragServiceUrl;
    },
    setRagServiceUrl: (url) => {
        appConfig.ragServiceUrl = url;
    }
});