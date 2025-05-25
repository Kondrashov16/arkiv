### Module: `chat_manager`

#### `rag_desktop_client/src/modules/chat_manager/README.md`

# Chat Manager Module

## Architecture

The `chat_manager` module is designed to centralize the management of all chat sessions within the application. It acts as a single source of truth for chat data, including active sessions, their unique identifiers, and the complete message history for each session. This module ensures that chat contexts are correctly maintained as users switch between different conversations.

It employs an in-memory storage approach, consistent with the requirement for "single session" persistence (i.e., data persists only as long as the application is running).

## How It Works

The `chat_manager.js` file provides functions to:

1.  **`createChatSession()`:**
    * **Purpose:** Initializes a new, empty chat session.
    * **Mechanism:** Generates a unique ID for the new session and stores it with an empty array for messages. It returns the ID of the new session.

2.  **`getChatHistory(chatId)`:**
    * **Purpose:** Retrieves the entire message history for a specific chat session.
    * **Mechanism:** Looks up the chat ID in its internal store and returns the associated array of messages.

3.  **`addMessageToHistory(chatId, message)`:**
    * **Purpose:** Appends a new message to the history of a specified chat session.
    * **Mechanism:** Takes a `chatId` and a `message` object (e.g., `{ role: 'user', content: '...', type: 'text' }` or `{ role: 'assistant', content: '...', type: 'text', sources: [] }`) and pushes it onto the session's message array.

4.  **`getActiveChatId()` and `setActiveChatId(chatId)`:**
    * **Purpose:** Manages which chat session is currently active/displayed to the user.
    * **Mechanism:** Stores and retrieves a single `activeChatId` value.

5.  **`getAllChatSessions()`:**
    * **Purpose:** Returns a list of all available chat session IDs.
    * **Mechanism:** Iterates over the internal storage to provide a list of session IDs.

### Data Structure

The internal storage for chat sessions will be a simple JavaScript object (or `Map`) where keys are `chatId`s and values are objects containing `messages` arrays.


```javascript
// Example internal structure
const chatSessions = {
    'chat-123': {
        messages: [
            { role: 'user', content: 'Hello', timestamp: '...' },
            { role: 'assistant', content: 'Hi there!', timestamp: '...', sources: [] }
        ]
    },
    'chat-456': {
        messages: []
    }
};
```