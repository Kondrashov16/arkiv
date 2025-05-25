# file_processing/chunking.py
import tiktoken
from core.config import settings # To use default CHUNK_SIZE and CHUNK_OVERLAP

# Global tokenizer cache to avoid reloading it multiple times
_tokenizer_cache = {}

def get_tiktoken_tokenizer(model_name: str = "cl100k_base"): # cl100k_base is for gpt-4, gpt-3.5-turbo, text-embedding-ada-002
    """
    Retrieves a TikToken tokenizer.
    Uses a cache to avoid re-initializing the tokenizer if called multiple times.
    Defaults to "cl100k_base" which is common for OpenAI models.
    """
    if model_name not in _tokenizer_cache:
        try:
            _tokenizer_cache[model_name] = tiktoken.get_encoding(model_name)
        except Exception:
            # Fallback if a specific model tokenizer isn't found, though cl100k_base is standard.
            # For sentence-transformers, token counting might differ slightly, but tiktoken is a good general proxy.
            print(f"Warning: Tiktoken model '{model_name}' not found. Using 'cl100k_base'.")
            _tokenizer_cache[model_name] = tiktoken.get_encoding("cl100k_base")
    return _tokenizer_cache[model_name]


def chunk_text_by_tokens(
    text: str, 
    tokenizer, # Pass the tokenizer instance
    chunk_size: int = settings.CHUNK_SIZE, 
    chunk_overlap: int = settings.CHUNK_OVERLAP
) -> list[str]:
    """
    Splits text into chunks based on token count using a TikToken tokenizer.

    Args:
        text: The input text to chunk.
        tokenizer: An initialized TikToken tokenizer instance.
        chunk_size: The desired maximum number of tokens per chunk.
        chunk_overlap: The number of tokens to overlap between consecutive chunks.

    Returns:
        A list of text chunks.
    """
    if not text.strip():
        return []

    tokens = tokenizer.encode(text)
    
    if not tokens:
        return []

    chunks = []
    current_pos = 0
    while current_pos < len(tokens):
        end_pos = min(current_pos + chunk_size, len(tokens))
        chunk_tokens = tokens[current_pos:end_pos]
        chunks.append(tokenizer.decode(chunk_tokens))
        
        if end_pos == len(tokens): # Reached the end
            break
        
        current_pos += (chunk_size - chunk_overlap)
        if current_pos >= len(tokens): # Ensure we don't go past the end with overlap logic
            break
        # Safety check: if overlap is too large or chunk_size too small, prevent infinite loop
        if (chunk_size - chunk_overlap) <= 0 and len(tokens) > chunk_size :
            print("Warning: chunk_size - chunk_overlap is not positive. Advancing by chunk_size/2 to prevent infinite loop.")
            current_pos = end_pos - chunk_size // 2 # Fallback to ensure progress
            if current_pos <= (end_pos - chunk_size): # If still no progress
                 current_pos = end_pos # Force break
    
    return chunks


if __name__ == '__main__':
    sample_text = (
        "This is a long sample text designed to test the chunking functionality. "
        "It contains multiple sentences and should be split into several chunks. "
        "The tokenizer will count the tokens, and the chunker will divide the text "
        "based on the specified chunk size and overlap. We hope this works correctly. "
        "Let's add more content to ensure it's long enough. Natural language processing "
        "often involves breaking down large documents into smaller pieces for easier analysis. "
        "This process, known as chunking or segmentation, is crucial for many NLP tasks, "
        "including information retrieval, text summarization, and question answering. "
        "The choice of chunk size and overlap can significantly impact the performance of "
        "downstream models. Too small chunks might lose context, while too large chunks "
        "might exceed model input limits or be computationally expensive to process."
    )

    print(f"--- Text Chunking Test (Token-based with TikToken) ---")
    print(f"Original text length (chars): {len(sample_text)}")

    # Get the default tokenizer (cl100k_base)
    tokenizer_instance = get_tiktoken_tokenizer()
    tokens = tokenizer_instance.encode(sample_text)
    print(f"Original text length (tokens using cl100k_base): {len(tokens)}")

    # Test with default settings from config (or override for test)
    test_chunk_size = 50  # Smaller for easier inspection
    test_chunk_overlap = 10

    print(f"\nChunking with size={test_chunk_size}, overlap={test_chunk_overlap}:")
    
    chunked_texts = chunk_text_by_tokens(
        sample_text, 
        tokenizer_instance,
        chunk_size=test_chunk_size, 
        chunk_overlap=test_chunk_overlap
    )

    if not chunked_texts:
        print("No chunks were generated. The text might be too short or empty.")
    else:
        for i, chunk in enumerate(chunked_texts):
            chunk_token_count = len(tokenizer_instance.encode(chunk))
            print(f"Chunk {i+1} (tokens: {chunk_token_count}):\n\"{chunk}\"\n")

    print("\n--- Edge Case: Empty Text ---")
    empty_chunks = chunk_text_by_tokens("", tokenizer_instance)
    print(f"Chunks from empty text: {empty_chunks}")

    print("\n--- Edge Case: Short Text (shorter than chunk_size) ---")
    short_text = "This is a short text."
    short_chunks = chunk_text_by_tokens(short_text, tokenizer_instance, chunk_size=test_chunk_size, chunk_overlap=test_chunk_overlap)
    print(f"Chunks from short text: {short_chunks}")
    if short_chunks:
        print(f"Token count of short text chunk: {len(tokenizer_instance.encode(short_chunks[0]))}")

    print("\n--- Edge Case: Text slightly larger than chunk_size ---")
    slightly_larger_text = "This is a text that is just a little bit longer than the chunk size we have set for this particular test case."
    # Ensure it's actually slightly larger in tokens
    target_tokens = test_chunk_size + 5
    encoded_slightly_larger = tokenizer_instance.encode(slightly_larger_text)
    if len(encoded_slightly_larger) > test_chunk_size:
        slightly_larger_chunks = chunk_text_by_tokens(slightly_larger_text, tokenizer_instance, chunk_size=test_chunk_size, chunk_overlap=test_chunk_overlap)
        print(f"Original slightly larger text tokens: {len(encoded_slightly_larger)}")
        for i, chunk in enumerate(slightly_larger_chunks):
            chunk_token_count = len(tokenizer_instance.encode(chunk))
            print(f"Slightly larger Chunk {i+1} (tokens: {chunk_token_count}):\n\"{chunk}\"\n")
    else:
        print(f"Skipping 'slightly larger' test as sample text tokens ({len(encoded_slightly_larger)}) not > chunk_size ({test_chunk_size})")

