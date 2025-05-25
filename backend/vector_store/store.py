# vector_store/store.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from core.config import settings # For MAX_CONTEXT_CHUNKS default

class VectorStore:
    """
    Manages text chunks, their embeddings, and similarity search using FAISS.
    """
    def __init__(self, embedding_model_name: str = settings.EMBEDDING_MODEL_NAME):
        """
        Initializes the VectorStore.

        Args:
            embedding_model_name (str): The name of the SentenceTransformer model to use.
        """
        print(f"Loading embedding model: {embedding_model_name}")
        try:
            self.model = SentenceTransformer(embedding_model_name)
        except Exception as e:
            print(f"Error loading SentenceTransformer model '{embedding_model_name}': {e}")
            print("Please ensure the model name is correct and you have an internet connection "
                  "if the model needs to be downloaded.")
            raise
        
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index. IndexFlatL2 uses Euclidean distance.
        # For cosine similarity, you might normalize vectors and use IndexFlatIP (Inner Product).
        # SentenceTransformer models often produce normalized embeddings, making L2 and IP effectively similar.
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # doc_map stores metadata: {faiss_index_id: {"text": chunk_text, "document_name": name, "chunk_id_in_doc": id}}
        self.doc_map = {}
        self.vector_count = 0 # Total number of vectors added to FAISS
        self._next_chunk_id_per_doc = {} # Tracks next chunk_id for each document: {"doc_name": next_id}

        print(f"VectorStore initialized with model {embedding_model_name} (dim: {self.embedding_dim}). FAISS index ready.")

    def add_documents(self, chunks: list[str], document_name: str):
        """
        Adds text chunks from a document to the vector store.

        Args:
            chunks (list[str]): A list of text chunks.
            document_name (str): The name of the source document for these chunks.
        """
        if not chunks:
            print(f"No chunks provided for document: {document_name}")
            return

        print(f"Generating embeddings for {len(chunks)} chunks from '{document_name}'...")
        try:
            embeddings = self.model.encode(chunks, convert_to_tensor=False, show_progress_bar=False)
            # Ensure embeddings are float32, as FAISS expects.
            embeddings = np.array(embeddings, dtype='float32')
        except Exception as e:
            print(f"Error generating embeddings for '{document_name}': {e}")
            return

        if embeddings.shape[0] == 0:
            print(f"Embeddings generation resulted in an empty array for '{document_name}'. Skipping.")
            return
            
        current_doc_chunk_id_start = self._next_chunk_id_per_doc.get(document_name, 0)

        for i, chunk_text in enumerate(chunks):
            faiss_id = self.vector_count + i
            self.doc_map[faiss_id] = {
                "text_preview": chunk_text, # Storing the actual chunk text
                "document_name": document_name,
                "chunk_id": current_doc_chunk_id_start + i # Sequential ID within this document batch
            }
        
        self.index.add(embeddings)
        self.vector_count += embeddings.shape[0]
        self._next_chunk_id_per_doc[document_name] = current_doc_chunk_id_start + len(chunks)
        
        print(f"Added {len(chunks)} chunks from '{document_name}' to VectorStore. Total vectors: {self.vector_count}")

    def search(self, query_text: str, k: int = settings.MAX_CONTEXT_CHUNKS) -> list[dict]:
        """
        Searches for the k most similar text chunks to the query_text.

        Args:
            query_text (str): The query text.
            k (int): The number of top similar chunks to retrieve.

        Returns:
            list[dict]: A list of dictionaries, each containing:
                        {'document_name': str, 'chunk_id': int, 'text_preview': str, 'score': float}
        """
        if self.index.ntotal == 0:
            print("VectorStore is empty. Cannot perform search.")
            return []

        print(f"Searching for top {k} chunks for query: '{query_text[:50]}...'")
        try:
            query_embedding = self.model.encode([query_text], convert_to_tensor=False, show_progress_bar=False)
            query_embedding = np.array(query_embedding, dtype='float32')
        except Exception as e:
            print(f"Error generating embedding for query: {e}")
            return []

        # Ensure k is not greater than the total number of vectors in the index
        actual_k = min(k, self.index.ntotal)
        if actual_k == 0:
            return []

        # FAISS search returns distances (D) and indices (I)
        distances, indices = self.index.search(query_embedding, actual_k)
        
        results = []
        if indices.size > 0:
            for i in range(indices.shape[1]): # Iterate through the k results for the single query
                idx = indices[0, i]
                dist = distances[0, i]
                if idx in self.doc_map:
                    doc_info = self.doc_map[idx]
                    results.append({
                        "document_name": doc_info["document_name"],
                        "chunk_id": doc_info["chunk_id"],
                        "text_preview": doc_info["text_preview"],
                        "score": float(dist) # L2 distance, smaller is better
                    })
                else:
                    print(f"Warning: Index {idx} found by FAISS but not in doc_map.")
        
        print(f"Found {len(results)} relevant chunks.")
        return results

    def get_total_vectors(self) -> int:
        """Returns the total number of vectors in the store."""
        return self.index.ntotal
        
    def reset(self):
        """Resets the vector store to an empty state."""
        print("Resetting VectorStore...")
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.doc_map = {}
        self.vector_count = 0
        self._next_chunk_id_per_doc = {}
        print("VectorStore has been reset.")

if __name__ == '__main__':
    # This basic test assumes you have sentence-transformers and faiss-cpu installed.
    print("--- VectorStore Test ---")
    
    # Use a lightweight model for testing if available, or the default
    test_embedding_model = settings.EMBEDDING_MODEL_NAME 
    try:
        store = VectorStore(embedding_model_name=test_embedding_model)
    except Exception as e:
        print(f"Failed to initialize VectorStore for test: {e}")
        print("Skipping VectorStore tests.")
        exit()


    print(f"\nTotal vectors initially: {store.get_total_vectors()}")

    # Test adding documents
    doc1_chunks = [
        "The quick brown fox jumps over the lazy dog.",
        "Apples are a type of fruit, often red or green.",
        "The weather in Spain is usually sunny."
    ]
    doc1_name = "document1.txt"
    store.add_documents(doc1_chunks, doc1_name)

    doc2_chunks = [
        "Paris is the capital of France.",
        "Large language models are powerful AI tools.",
        "The sky is blue on a clear day."
    ]
    doc2_name = "document2.md"
    store.add_documents(doc2_chunks, doc2_name)

    print(f"\nTotal vectors after adding docs: {store.get_total_vectors()}")
    assert store.get_total_vectors() == len(doc1_chunks) + len(doc2_chunks)

    # Test searching
    print("\n--- Search Test 1 ---")
    query1 = "What is the color of the sky?"
    results1 = store.search(query1, k=2)
    print(f"Query: '{query1}'")
    for res in results1:
        print(f"  Source: {res['document_name']}, Chunk ID: {res['chunk_id']}, Score: {res['score']:.4f}")
        print(f"  Text: '{res['text_preview'][:50]}...'")
    
    # Expect "The sky is blue..." to be a top result
    assert any("sky is blue" in res['text_preview'] for res in results1)

    print("\n--- Search Test 2 ---")
    query2 = "Information about European capitals"
    results2 = store.search(query2, k=2)
    print(f"Query: '{query2}'")
    for res in results2:
        print(f"  Source: {res['document_name']}, Chunk ID: {res['chunk_id']}, Score: {res['score']:.4f}")
        print(f"  Text: '{res['text_preview'][:50]}...'")
    
    # Expect "Paris is the capital..." to be a top result
    assert any("Paris is the capital" in res['text_preview'] for res in results2)

    print("\n--- Search Test with k > num_docs ---")
    query3 = "fox"
    results3 = store.search(query3, k=10) # k is larger than total docs
    print(f"Query: '{query3}' (k=10, total_vectors={store.get_total_vectors()})")
    assert len(results3) == store.get_total_vectors() # Should return all docs if k is high enough
    for res in results3:
        print(f"  Source: {res['document_name']}, Chunk ID: {res['chunk_id']}, Score: {res['score']:.4f}")
        print(f"  Text: '{res['text_preview'][:50]}...'")


    print("\n--- Test Reset ---")
    store.reset()
    print(f"Total vectors after reset: {store.get_total_vectors()}")
    assert store.get_total_vectors() == 0
    results_after_reset = store.search(query1, k=2)
    print(f"Search results after reset: {results_after_reset}")
    assert len(results_after_reset) == 0
    
    print("\nVectorStore tests completed.")
