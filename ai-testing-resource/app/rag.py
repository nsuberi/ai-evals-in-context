"""RAG (Retrieval Augmented Generation) with Chroma vector store"""

import os
from pathlib import Path
from typing import List, Dict, Optional

# Lazy imports - only import chromadb when needed to avoid startup errors
# This prevents chromadb telemetry from blocking Flask startup

# Initialize Chroma
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")

# Lazy initialization
_chroma_client = None
_collection = None
_embedding_function = None


def get_chroma_client():
    """Get or create Chroma client"""
    global _chroma_client
    if _chroma_client is None:
        # Import chromadb only when needed (lazy import)
        import chromadb
        import chromadb.config
        import logging

        # Suppress chromadb telemetry warnings (telemetry is disabled anyway)
        logging.getLogger('chromadb.telemetry.product.posthog').setLevel(logging.CRITICAL)

        # Disable telemetry to avoid PostHog version conflicts
        settings = chromadb.config.Settings(
            anonymized_telemetry=False,
            persist_directory=CHROMA_PATH
        )
        _chroma_client = chromadb.PersistentClient(settings=settings)
    return _chroma_client


def get_embedding_function():
    """Get the embedding function - uses sentence-transformers (local, free)"""
    global _embedding_function
    if _embedding_function is None:
        # Import chromadb embedding functions only when needed (lazy import)
        from chromadb.utils import embedding_functions
        # Use sentence-transformers for embeddings (works locally without API)
        _embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    return _embedding_function


def get_collection():
    """Get or create the knowledge base collection"""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        ef = get_embedding_function()

        _collection = client.get_or_create_collection(
            name="acme_knowledge_base",
            embedding_function=ef
        )

    return _collection


def initialize_knowledge_base(knowledge_dir: str = "data/knowledge_base"):
    """
    Load knowledge base documents into Chroma.
    Call this once during setup.
    """
    knowledge_path = Path(knowledge_dir)

    if not knowledge_path.exists():
        print(f"Knowledge base directory not found: {knowledge_dir}")
        return

    documents = []
    metadatas = []
    ids = []

    for md_file in knowledge_path.glob("*.md"):
        content = md_file.read_text()
        doc_id = md_file.stem

        # Extract title from first line if it's a header
        lines = content.strip().split('\n')
        title = lines[0].lstrip('#').strip() if lines[0].startswith('#') else doc_id.replace('_', ' ').title()

        documents.append(content)
        metadatas.append({
            'id': doc_id,
            'title': title,
            'filename': md_file.name,
            'category': categorize_doc(doc_id)
        })
        ids.append(doc_id)

    if documents:
        collection = get_collection()
        # Upsert to handle re-initialization
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Loaded {len(documents)} documents into knowledge base")


def categorize_doc(doc_id: str) -> str:
    """Categorize document based on filename"""
    if 'pricing' in doc_id or 'price' in doc_id:
        return 'pricing'
    elif 'return' in doc_id or 'refund' in doc_id:
        return 'returns'
    elif 'shipping' in doc_id or 'delivery' in doc_id:
        return 'shipping'
    elif 'product' in doc_id or 'spec' in doc_id:
        return 'products'
    else:
        return 'general'


def get_relevant_docs(query: str, n_results: int = 3) -> List[Dict]:
    """
    Query Chroma for relevant documents.

    Returns:
        List of dicts with 'id', 'title', 'content', 'distance'
    """
    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    docs = []
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i] if results['metadatas'] else {}
            distance = results['distances'][0][i] if results['distances'] else 0

            docs.append({
                'id': metadata.get('id', f'doc_{i}'),
                'title': metadata.get('title', 'Unknown'),
                'content': doc,
                'distance': distance
            })

    return docs


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a single text (for testing/debugging)"""
    ef = get_embedding_function()
    result = ef([text])
    # Convert numpy floats to Python floats for type consistency
    return [float(x) for x in result[0]] if result else []
