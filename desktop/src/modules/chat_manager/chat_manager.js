// rag_desktop_client/src/modules/chat_manager/chat_manager.js

// In-memory storage for all chat sessions
const chatSessions = new Map();
let activeChatId = null;

/**
 * Generates a unique ID for a new chat session.
 * @returns {string} A unique chat session ID.
 */
function generateUniqueChatId() {
    return `chat-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Creates and initializes a new chat session.
 * @returns {string} The ID of the newly created chat session.
 */
export function createChatSession() {
    const newChatId = generateUniqueChatId();
    chatSessions.set(newChatId, {
        messages: []
    });
    // Set the new chat as active if it's the first one, or if we want to immediately switch to it.
    // For now, we'll let the UI explicitly set the active chat.
    return newChatId;
}

/**
 * Retrieves the message history for a given chat session.
 * @param {string} chatId - The ID of the chat session.
 * @returns {Array<Object>} An array of message objects for the specified chat, or an empty array if not found.
 */
export function getChatHistory(chatId) {
    const session = chatSessions.get(chatId);
    return session ? [...session.messages] : []; // Return a copy to prevent external modification
}

/**
 * Adds a message to the history of a specified chat session.
 * @param {string} chatId - The ID of the chat session.
 * @param {Object} message - The message object to add. Expected format: { role: 'user'|'assistant', content: string, type: 'text'|'file_upload_status', sources?: Array<Object> }
 */
export function addMessageToHistory(chatId, message) {
    const session = chatSessions.get(chatId);
    if (session) {
        session.messages.push({ ...message, timestamp: new Date().toISOString() });
    } else {
        console.warn(`Chat session with ID ${chatId} not found. Message not added.`);
    }
}

/**
 * Gets the ID of the currently active chat session.
 * @returns {string|null} The active chat ID or null if none is active.
 */
export function getActiveChatId() {
    return activeChatId;
}

/**
 * Sets the ID of the currently active chat session.
 * @param {string} chatId - The ID of the chat session to set as active.
 */
export function setActiveChatId(chatId) {
    if (chatSessions.has(chatId)) {
        activeChatId = chatId;
    } else {
        console.warn(`Attempted to set non-existent chat ID ${chatId} as active.`);
    }
}

/**
 * Gets all chat session IDs.
 * @returns {Array<string>} An array of all chat session IDs.
 */
export function getAllChatSessionIds() {
    return Array.from(chatSessions.keys());
}

// Initialize with a default chat session on load if no active chat is set
// or if we want a fresh start each time.
// For "single session" behavior, we might want to create one default chat initially.
if (chatSessions.size === 0) {
    const defaultChatId = createChatSession();
    setActiveChatId(defaultChatId);
    console.log(`Initial chat session created: ${defaultChatId}`);
}