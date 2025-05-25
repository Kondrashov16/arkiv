// rag_desktop_client/src/modules/file_upload/file_upload.js

import { uploadFile } from '../api_client/api_client.js';
import { getActiveChatId, addMessageToHistory } from '../chat_manager/chat_manager.js';

/**
 * Initializes the file upload functionality.
 * @param {string} uploadButtonId - The ID of the button that triggers file selection.
 * @param {string} fileInputId - The ID of the hidden file input element.
 * @param {string} statusDisplayId - The ID of the element to display upload status.
 */
export function initFileUpload(uploadButtonId, fileInputId, statusDisplayId) {
    console.log("initFileUpload called with IDs:", { uploadButtonId, fileInputId, statusDisplayId });
    
    const uploadButton = document.getElementById(uploadButtonId);
    const fileInput = document.getElementById(fileInputId);
    const statusDisplay = document.getElementById(statusDisplayId);

    console.log("Found file upload elements:", { 
        uploadButton: !!uploadButton, 
        fileInput: !!fileInput, 
        statusDisplay: !!statusDisplay 
    });

    if (uploadButton && fileInput && statusDisplay) {
        uploadButton.addEventListener('click', () => {
            console.log("Upload button clicked");
            fileInput.click(); // Programmatically click the hidden file input
        });

        fileInput.addEventListener('change', (event) => {
            console.log("File input changed");
            handleFileSelection(event, statusDisplay);
        });
        
        console.log("File upload event listeners added successfully");
    } else {
        console.error('File upload elements not found. Check IDs:', { uploadButtonId, fileInputId, statusDisplayId });
    }
}

/**
 * Handles the selection of a file and initiates the upload process.
 * @param {Event} event - The change event from the file input.
 * @param {HTMLElement} statusDisplay - The DOM element to update with status messages.
 */
async function handleFileSelection(event, statusDisplay) {
    const file = event.target.files[0];
    if (!file) {
        return; // No file selected
    }

    const activeChatId = getActiveChatId();
    if (!activeChatId) {
        alert('Please create or select a chat session before uploading a file.');
        statusDisplay.textContent = '';
        return;
    }

    statusDisplay.textContent = `Uploading "${file.name}"...`;
    statusDisplay.style.color = 'orange';

    // Add a pending message to the chat history
    addMessageToHistory(activeChatId, {
        role: 'system',
        content: `Initiating upload of "${file.name}"...`,
        type: 'file_upload_status',
        status: 'pending',
        fileName: file.name
    });

    try {
        const response = await uploadFile(file);
        statusDisplay.textContent = `"${file.name}" uploaded successfully!`;
        statusDisplay.style.color = 'green';
        console.log('Upload successful:', response);

        // Update chat history with success message
        addMessageToHistory(activeChatId, {
            role: 'system',
            content: `"${file.name}" uploaded successfully! Document processed.`,
            type: 'file_upload_status',
            status: 'success',
            fileName: file.name
        });

        // Clear the file input value to allow re-uploading the same file
        event.target.value = '';

    } catch (error) {
        statusDisplay.textContent = `Error uploading "${file.name}": ${error.message}`;
        statusDisplay.style.color = 'red';
        console.error('File upload error:', error);

        // Update chat history with error message
        addMessageToHistory(activeChatId, {
            role: 'system',
            content: `Error uploading "${file.name}": ${error.message}`,
            type: 'file_upload_status',
            status: 'error',
            fileName: file.name
        });
    } finally {
        // Optionally clear status message after a few seconds
        setTimeout(() => {
            statusDisplay.textContent = '';
        }, 5000);
    }
}