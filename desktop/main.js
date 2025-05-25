// main.js - Electron Main Process

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const dotenv = require('dotenv');

// Load environment variables from .env file
dotenv.config();

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1000,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            // IMPORTANT: For security, contextIsolation should be true and nodeIntegration false in production.
            // We're keeping nodeIntegration false here as a best practice, using preload for exposure.
            contextIsolation: true,
            nodeIntegration: false,
        },
    });

    mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));

    // Open the DevTools.
    // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// IPC handler for renderer to request environment variables
ipcMain.handle('get-env-variable', (event, key) => {
    return process.env[key];
});

// IPC handler for file dialog - if we wanted to handle file selection in main process
// ipcMain.handle('show-open-dialog', async (event) => {
//     const result = await dialog.showOpenDialog({
//         properties: ['openFile'],
//         filters: [
//             { name: 'Documents', extensions: ['pdf', 'docx', 'md'] }
//         ]
//     });
//     return result;
// });