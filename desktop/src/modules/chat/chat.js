// rag_desktop_client/src/modules/chat/chat.js

import { getActiveChatId, getChatHistory, addMessageToHistory, setActiveChatId, createChatSession, getAllChatSessionIds } from '../chat_manager/chat_manager.js';
import { queryLLM } from '../api_client/api_client.js';

let chatContainer;
let messageInput;
let sendMessageButton;
let newChatButton;
let chatListContainer;
let uploadStatusDisplay; // Reference to the status display from file_upload module

/**
 * Initializes the chat UI components and event listeners.
 * @param {string} chatContainerId - ID of the element where messages are displayed.
 * @param {string} messageInputId - ID of the text input for messages.
 * @param {string} sendMessageButtonId - ID of the button to send messages.
 * @param {string} newChatButtonId - ID of the button to create a new chat.
 * @param {string} chatListContainerId - ID of the container for chat session list.
 * @param {string} uploadStatusDisplayId - ID of the element displaying upload status.
 */
export function initChat(chatContainerId, messageInputId, sendMessageButtonId, newChatButtonId, chatListContainerId, uploadStatusDisplayId) {
    console.log("initChat called with IDs:", { chatContainerId, messageInputId, sendMessageButtonId, newChatButtonId, chatListContainerId, uploadStatusDisplayId });
    
    chatContainer = document.getElementById(chatContainerId);
    messageInput = document.getElementById(messageInputId);
    sendMessageButton = document.getElementById(sendMessageButtonId);
    newChatButton = document.getElementById(newChatButtonId);
    chatListContainer = document.getElementById(chatListContainerId);
    uploadStatusDisplay = document.getElementById(uploadStatusDisplayId);

    console.log("Found elements:", { 
        chatContainer: !!chatContainer, 
        messageInput: !!messageInput, 
        sendMessageButton: !!sendMessageButton, 
        newChatButton: !!newChatButton, 
        chatListContainer: !!chatListContainer, 
        uploadStatusDisplay: !!uploadStatusDisplay 
    });

    if (!chatContainer || !messageInput || !sendMessageButton || !newChatButton || !chatListContainer || !uploadStatusDisplay) {
        console.error('One or more chat UI elements not found. Check IDs.');
        return;
    }

    sendMessageButton.addEventListener('click', () => {
        console.log("Send button clicked");
        handleSendMessage();
    });
    
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            console.log("Enter key pressed in message input");
            e.preventDefault(); // Prevent new line in input
            handleSendMessage();
        }
    });

    newChatButton.addEventListener('click', () => {
        console.log("New chat button clicked");
        const newChatId = createChatSession();
        setActiveChatId(newChatId);
        renderChatHistory(newChatId);
        updateChatList();
    });

    // Initial render of chat list and active chat
    updateChatList();
    renderChatHistory(getActiveChatId()); // Render the initial active chat
}

/**
 * Renders the entire chat history for the currently active chat.
 * Clears existing messages and re-adds them.
 * @param {string} chatId - The ID of the chat to render.
 */
export function renderChatHistory(chatId) {
    chatContainer.innerHTML = ''; // Clear current messages
    const history = getChatHistory(chatId);
    history.forEach(msg => displayMessage(msg));
    scrollToBottom();
    highlightActiveChatInList(chatId);
}

/**
 * Displays a single message in the chat container.
 * @param {Object} message - The message object to display.
 */
function displayMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', message.role); // 'user', 'assistant', 'system'

    const contentElement = document.createElement('div');
    contentElement.classList.add('message-content');

    if (message.type === 'file_upload_status') {
        contentElement.innerHTML = `
            <p>${message.content}</p>
            <small class="${message.status}">Status: ${message.status.toUpperCase()}</small>
        `;
    } else {
        contentElement.textContent = message.content;
    }

    messageElement.appendChild(contentElement);

    if (message.role === 'assistant' && message.sources && message.sources.length > 0) {
        const sourcesElement = document.createElement('div');
        sourcesElement.classList.add('message-sources');
        const sourceTitle = document.createElement('strong');
        sourceTitle.textContent = 'Sources:';
        sourcesElement.appendChild(sourceTitle);

        message.sources.forEach(source => {
            const sourceItem = document.createElement('div');
            sourceItem.classList.add('source-item');
            sourceItem.innerHTML = `
                <span>${source.document_name} (Chunk ${source.chunk_id})</span>
                <p>"${source.text_preview}..."</p>
            `;
            sourcesElement.appendChild(sourceItem);
        });
        messageElement.appendChild(sourcesElement);
    }

    chatContainer.appendChild(messageElement);
    scrollToBottom();
}

/**
 * Handles sending a message to the LLM.
 */
async function handleSendMessage() {
    console.log("handleSendMessage");
    const queryText = messageInput.value.trim();
    if (!queryText) return;

    const activeChatId = getActiveChatId();
    if (!activeChatId) {
        alert('Please create or select a chat session.');
        return;
    }

    // Add user message to history and display immediately
    const userMessage = { role: 'user', content: queryText, type: 'text' };
    addMessageToHistory(activeChatId, userMessage);
    displayMessage(userMessage);

    messageInput.value = ''; // Clear input

    // Display a "typing" or "thinking" indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.classList.add('message', 'assistant', 'thinking');
    typingIndicator.textContent = 'Assistant is typing...';
    chatContainer.appendChild(typingIndicator);
    scrollToBottom();

    try {
        const chatHistoryForLLM = getChatHistory(activeChatId);
        // We might need to filter or format chatHistoryForLLM for the LLM if it gets too long
        // The backend README mentions sending "chat_history", so we assume it handles it.
        const response = await queryLLM(queryText, chatHistoryForLLM);

        // Remove typing indicator
        chatContainer.removeChild(typingIndicator);

        const assistantMessage = {
            role: 'assistant',
            content: response.llm_response,
            type: 'text',
            sources: response.sources
        };
        addMessageToHistory(activeChatId, assistantMessage);
        displayMessage(assistantMessage);

    } catch (error) {
        console.error('Error querying LLM:', error);
        // Remove typing indicator
        if (chatContainer.contains(typingIndicator)) {
            chatContainer.removeChild(typingIndicator);
        }
        const errorMessage = {
            role: 'system',
            content: `Error: ${error.message}. Please try again.`,
            type: 'text'
        };
        addMessageToHistory(activeChatId, errorMessage);
        displayMessage(errorMessage);
    }
}

/**
 * Scrolls the chat container to the bottom.
 */
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Updates the list of chat sessions in the sidebar.
 */
function updateChatList() {
    chatListContainer.innerHTML = ''; // Clear existing list
    const chatIds = getAllChatSessionIds();

    chatIds.forEach(chatId => {
        const chatItem = document.createElement('div');
        chatItem.classList.add('chat-item');
        chatItem.textContent = `Chat Session ${chatIds.indexOf(chatId) + 1}`; // Simple naming
        chatItem.dataset.chatId = chatId;

        chatItem.addEventListener('click', () => {
            setActiveChatId(chatId);
            renderChatHistory(chatId);
            updateChatList(); // Re-render to update active highlight
        });
        chatListContainer.appendChild(chatItem);
    });
    highlightActiveChatInList(getActiveChatId());
}

/**
 * Highlights the active chat session in the list.
 * @param {string} activeId - The ID of the currently active chat.
 */
function highlightActiveChatInList(activeId) {
    Array.from(chatListContainer.children).forEach(item => {
        if (item.dataset.chatId === activeId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}