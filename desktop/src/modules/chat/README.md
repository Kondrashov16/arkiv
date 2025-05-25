### Module: `chat`

#### `rag_desktop_client/src/modules/chat/README.md`

# Chat Module

## Architecture

The `chat` module is the core UI component for displaying and interacting with a single chat session. It is responsible for rendering messages, handling user input, and integrating with other modules like `api_client` (for sending queries) and `chat_manager` (for retrieving and updating chat history). It follows a standard component-based approach to manage its internal state and render updates efficiently.

## How It Works

The `chat.js` file will contain functions and logic to:

1.  **`initChat(chatContainerId, messageInputId, sendMessageButtonId, chatListContainerId)`:**
    * **Purpose:** Initializes the chat UI elements and event listeners.
    * **Mechanism:** Attaches event listeners to the message input field (for 'Enter' key press) and the send button.
    * Calls `renderChatHistory` whenever the active chat changes or new messages are added.

2.  **`displayMessage(message)`:**
    * **Purpose:** Appends a single message to the chat display.
    * **Mechanism:** Creates appropriate HTML elements for the message (e.g., distinguishing user messages from LLM responses, and handling sources). Scrolls to the bottom of the chat.

3.  **`renderChatHistory(chatId)`:**
    * **Purpose:** Clears the current chat display and re-renders the entire history for the specified `chatId`.
    * **Mechanism:** Retrieves the history from `chat_manager.getChatHistory()` and calls `displayMessage` for each message.

4.  **`handleSendMessage()`:**
    * **Purpose:** Processes user input, sends it to the LLM, and displays the response.
    * **Mechanism:**
        * Gets the current query from the input field.
        * Retrieves the full chat history from `chat_manager.getChatHistory()` for the active session.
        * Adds the user's message to `chat_manager` and displays it immediately.
        * Calls `api_client.queryLLM()` with the current query and the full chat history.
        * Upon receiving a response, adds the LLM's message and sources to `chat_manager` and displays it.
        * Handles loading states and error messages.

5.  **`updateChatList(chatIds)`:**
    * **Purpose:** Renders or updates the list of available chat sessions for switching.
    * **Mechanism:** Takes an array of `chatId`s, creates UI elements for each, and attaches click listeners to switch active chats via `chat_manager.setActiveChatId()` and then `renderChatHistory()`.

### Message Structure

Messages will have a consistent structure to allow for proper rendering and context management:

```javascript
{
    role: 'user' | 'assistant' | 'system', // Who sent the message
    content: 'string',                     // The message text
    timestamp: 'ISO String',               // When the message was sent/received
    type: 'text' | 'file_upload_status',   // Helps in rendering different types of messages
    sources: [                             // (Optional, for assistant messages)
        {
            document_name: 'string',
            chunk_id: number,
            text_preview: 'string'
        }
    ]
}
```
