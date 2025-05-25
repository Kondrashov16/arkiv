# llm_interface/openrouter_client.py
import requests
import json
from core.config import settings # For API key and model name

class OpenRouterClient:
    """
    A client for interacting with the OpenRouter API.
    """
    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str = settings.OPENROUTER_API_KEY, model_name: str = settings.OPENROUTER_MODEL_NAME):
        """
        Initializes the OpenRouterClient.

        Args:
            api_key (str): The OpenRouter API key.
            model_name (str): The name of the model to use (e.g., "mistralai/mistral-7b-instruct").
        """
        if not api_key:
            raise ValueError("OpenRouter API key is required.")
        self.api_key = api_key
        self.model_name = model_name
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # Optional: Set HTTP Referer for OpenRouter tracking/analytics if you have a site
            # "HTTP-Referer": "YOUR_SITE_URL", 
            # "X-Title": "YOUR_SITE_NAME",
        }
        print(f"OpenRouterClient initialized for model: {self.model_name}")

    def _prepare_prompt_with_context(self, query: str, context_chunks: list[dict]) -> str:
        """
        Prepares a detailed prompt for the LLM, including the query and context.

        Args:
            query (str): The user's original query.
            context_chunks (list[dict]): A list of context chunks, where each chunk is a dict
                                         with 'document_name', 'chunk_id', and 'text_preview'.

        Returns:
            str: The fully formatted prompt.
        """
        if not context_chunks:
            # If no context, just use the query with a basic instruction.
            # This might happen if the vector store returns no relevant chunks.
            return (
                f"You are a helpful AI assistant. Please answer the following query:\n\n"
                f"Query: {query}\n\n"
                f"Answer:"
            )

        context_str = "\n\n--- Context from Documents ---\n"
        for i, chunk_info in enumerate(context_chunks):
            context_str += (
                f"Source {i+1}:\n"
                f"  Document: {chunk_info.get('document_name', 'N/A')}\n"
                f"  Chunk ID: {chunk_info.get('chunk_id', 'N/A')}\n"
                f"  Text: \"{chunk_info.get('text_preview', '')}\"\n"
                "---\n"
            )
        
        prompt = (
            f"You are a helpful AI assistant. Your task is to answer the user's query based *solely* on the provided context from documents. "
            f"Do not use any external knowledge. If the answer cannot be found within the provided context, clearly state that. "
            f"When formulating your answer, be concise and directly address the query.\n"
            f"{context_str}\n"
            f"--- User Query ---\n"
            f"Query: {query}\n\n"
            f"--- Answer ---\n"
            f"Based on the provided context:\n"
        )
        return prompt

    def query_llm(self, user_query: str, context_chunks: list[dict]) -> str:
        """
        Sends a query (with context) to the specified OpenRouter LLM.

        Args:
            user_query (str): The user's query.
            context_chunks (list[dict]): Relevant text chunks to provide as context.

        Returns:
            str: The LLM's response text.

        Raises:
            requests.exceptions.RequestException: If the API request fails.
            ValueError: If the API response is malformed or indicates an error.
        """
        full_prompt_content = self._prepare_prompt_with_context(user_query, context_chunks)
        
        # For chat models, the prompt is typically a "user" message
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": full_prompt_content}
            ],
            # Optional parameters:
            # "temperature": 0.7,
            # "max_tokens": 1000,
        }

        print(f"Sending query to OpenRouter model: {self.model_name}")
        # print(f"Payload (first 200 chars of prompt): {json.dumps(payload, indent=2)[:200]}...") # Be careful logging full prompt if sensitive

        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=60  # seconds
            )
            response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
        except requests.exceptions.Timeout:
            print("Error: Request to OpenRouter timed out.")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Error during OpenRouter API request: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    print(f"Response content: {e.response.text}")
                except Exception:
                    pass # Ignore if response text itself is problematic
            raise

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON response from OpenRouter: {response.text}")
            raise ValueError("Malformed JSON response from OpenRouter.")

        if "error" in response_data:
            print(f"OpenRouter API Error: {response_data['error']}")
            raise ValueError(f"OpenRouter API Error: {response_data['error'].get('message', 'Unknown error')}")

        try:
            # Standard OpenAI-compatible response structure
            llm_response = response_data["choices"][0]["message"]["content"]
            print("Successfully received response from OpenRouter.")
            return llm_response.strip()
        except (KeyError, IndexError) as e:
            print(f"Error: Unexpected response structure from OpenRouter: {e}")
            print(f"Full response data: {json.dumps(response_data, indent=2)}")
            raise ValueError("Unexpected response structure from OpenRouter.")


if __name__ == '__main__':
    print("--- OpenRouterClient Test ---")
    
    # Ensure OPENROUTER_API_KEY and OPENROUTER_MODEL_NAME are in your .env for this test
    if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        print("Skipping OpenRouterClient test: OPENROUTER_API_KEY not set in .env file.")
    else:
        try:
            client = OpenRouterClient(
                api_key=settings.OPENROUTER_API_KEY,
                model_name=settings.OPENROUTER_MODEL_NAME  # Use a fast/cheap model for testing if possible
            )
            
            # Test 1: Query without context
            print("\n--- Test 1: Query without context ---")
            query_no_context = "What is the capital of France?"
            try:
                response_no_context = client.query_llm(query_no_context, [])
                print(f"Query: {query_no_context}")
                print(f"LLM Response (no context): {response_no_context}")
                assert "Paris" in response_no_context # Basic check
            except Exception as e:
                print(f"Error during no-context query test: {e}")

            # Test 2: Query with dummy context
            print("\n--- Test 2: Query with context ---")
            query_with_context = "What is the main ingredient of a widget according to the document?"
            dummy_context = [
                {
                    "document_name": "widget_manual.txt", 
                    "chunk_id": 0, 
                    "text_preview": "This document describes widgets. Widgets are made primarily of floof."
                },
                {
                    "document_name": "competitor_analysis.txt", 
                    "chunk_id": 3, 
                    "text_preview": "Our competitors use plasteel for their gadgets, which is inferior to floof."
                }
            ]
            try:
                response_with_context = client.query_llm(query_with_context, dummy_context)
                print(f"Query: {query_with_context}")
                # print(f"Context provided: {dummy_context}") # Can be verbose
                print(f"LLM Response (with context): {response_with_context}")
                assert "floof" in response_with_context.lower() # Expect it to use context
            except Exception as e:
                print(f"Error during context query test: {e}")

        except ValueError as ve:
            print(f"Initialization Error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred during testing: {e}")
