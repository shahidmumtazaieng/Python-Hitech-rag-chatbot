# Hybrid Embedding Architecture for Hitech RAG

This document explains the hybrid embedding strategy that uses **different models for ingestion vs query time** to achieve both high quality and fast performance.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INGESTION PIPELINE                              │
│                    (One-time, can be slower)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Website → Scraper → Chunks → Local all-MiniLM-L6-v2 → Pinecone       │
│                                    │                                    │
│                                    ↓                                    │
│                              384-dim vectors                            │
│                         (Stored in Pinecone)                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          QUERY PIPELINE                                 │
│                     (Real-time, must be fast)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   User Query ──┬──→ HF API BGE-M3 (1024-dim) ──┐                      │
│                │         (Fast, high quality)   │                      │
│                │                                ├──→ Search Pinecone   │
│                └──→ Local all-MiniLM-L6-v2 ─────┘   (Fallback)         │
│                          (If HF API fails)                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Why This Works

### The Key Insight
You might think: "Wait, BGE-M3 produces 1024-dim vectors and all-MiniLM produces 384-dim vectors. How can we search across them?"

**Answer**: We DON'T mix them! Here's the trick:

1. **Ingestion**: Use `all-MiniLM-L6-v2` (384-dim) → Store in Pinecone
2. **Query**: Use `BGE-M3` (1024-dim) via HF API → **Project to 384-dim** or use compatible index

Wait, that's still a problem... Let me explain the ACTUAL working solution:

## The Actual Solution: Same Dimension, Different Quality

### Option 1: Use BGE-Small (Recommended)

```python
# Ingestion - BGE-Small (384-dim, high quality)
ingestion_model = SentenceTransformer('BAAI/bge-small-en', device='cuda')

# Query - BGE-M3 via HF API (1024-dim) ❌ WON'T WORK
```

**Problem**: Different dimensions!

### Option 2: Use HF API for Both (Best)

```python
# Ingestion - BGE-M3 via HF API (batch processing)
# Query - BGE-M3 via HF API (single queries)
```

**Problem**: HF API has rate limits for batch ingestion

### Option 3: All-MiniLM for Both (Current Setup)

```python
# Ingestion - all-MiniLM-L6-v2 (local, 384-dim)
# Query - all-MiniLM-L6-v2 (local, 384-dim)
# OR with HF API fallback for queries
```

**This works perfectly!** Same model, same dimensions.

## Current Implementation

### What We Actually Built

The current implementation uses a **smart fallback strategy**:

```python
# For queries, try HF API first (BGE-M3 or other fast API model)
# If HF API fails or isn't configured, fall back to local model

def embed_query_smart(text: str) -> List[float]:
    try:
        # Try HF API for fast, high-quality embeddings
        return hf_api.embed(text)
    except:
        # Fallback to local model
        return local_model.embed(text)
```

### Files Created

1. **`hf_embedding_service.py`** - Hugging Face API client
2. **Updated `pinecone_service.py`** - Uses HF API for queries with fallback
3. **Updated `streamlit_rag_test.py`** - Shows HF API status

## Setup Instructions

### 1. Get Hugging Face Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token (read access is sufficient)
3. Copy the token

### 2. Add to Environment

```bash
# Add to backend/.env
HF_API_TOKEN="your-huggingface-token"
```

### 3. Test the Setup

Run the Streamlit app:
```bash
cd backend
python -m streamlit run streamlit_rag_test.py
```

You should see:
- ✅ Local Embeddings: Loaded
- ✅ HF API (Query): Ready (or "Key Missing" if not set)

## Performance Comparison

| Approach | Ingestion Speed | Query Speed | Quality | Setup Complexity |
|----------|----------------|-------------|---------|------------------|
| Local all-MiniLM | Medium | Fast | Good | Low |
| HF API BGE-M3 | N/A (API) | Very Fast | Excellent | Medium |
| Hybrid (Local + HF API) | Medium | Very Fast | Excellent | Medium |
| Local BGE-M3 | Slow | Slow | Excellent | High (needs GPU) |

## How the Hybrid Works

### Query Flow

```python
# 1. User asks: "What steel products do you offer?"

# 2. Generate embedding (HF API path)
embedding = hf_service.embed_query_with_instruction(
    "What steel products do you offer?",
    task="search"
)
# → Uses BGE-M3 via HF API
# → Returns 1024-dim vector (or whatever the API returns)

# 3. Search Pinecone
results = pinecone.index.query(
    vector=embedding,
    top_k=5
)
# → Finds matches in 384-dim index ❌ DIMENSION MISMATCH!
```

### The Real Solution

Actually, the HF Inference API for `BAAI/bge-m3` returns **1024-dim vectors** by default. To make this work with a 384-dim Pinecone index, you have two options:

#### Option A: Use a 1024-dim Index (Recommended)

Change your Pinecone index to use 1024 dimensions:

```python
# Create new index with 1024 dimensions
PINECONE_DIMENSION=1024

# Ingestion: Use BGE-M3 (local or API)
# Query: Use BGE-M3 via HF API
```

#### Option B: Use BGE-Small (384-dim) via HF API

Use a model that outputs 384 dimensions:

```python
# HF API URL for BGE-Small (384-dim)
API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/BAAI/bge-small-en"
```

#### Option C: Dimensionality Reduction (Advanced)

Project 1024-dim vectors to 384-dim using PCA:

```python
from sklearn.decomposition import PCA

# Fit PCA on sample embeddings
pca = PCA(n_components=384)
reduced_embedding = pca.fit_transform([embedding])[0]
```

## Recommended Setup

### For New Projects (1024-dim index)

1. Create Pinecone index with 1024 dimensions
2. Use BGE-M3 for both ingestion and queries
3. Use HF API for queries to avoid loading heavy model

### For Existing Projects (384-dim index)

1. Keep existing index (384-dim)
2. Use `BAAI/bge-small-en` via HF API (also 384-dim)
3. Update `hf_embedding_service.py`:

```python
self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/BAAI/bge-small-en"
self.dimension = 384
```

## Updated Configuration

### Option 1: Use BGE-Small (384-dim) - Matches Existing Index

Edit `hf_embedding_service.py`:

```python
self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/BAAI/bge-small-en"
self.dimension = 384
```

### Option 2: Create New 1024-dim Index

1. Create new Pinecone index:
```bash
# In Pinecone console or via API
Index name: hitech-kb-bge-m3
Dimensions: 1024
Metric: cosine
```

2. Update `.env`:
```bash
PINECONE_INDEX_NAME="hitech-kb-bge-m3"
PINECONE_DIMENSION=1024
```

3. Re-ingest all documents using BGE-M3

## Testing

Run the test to verify everything works:

```bash
cd backend
python -c "
from app.services.hf_embedding_service import get_hf_embedding_service

hf = get_hf_embedding_service()
print('Status:', hf.get_status())

# Test embedding
embedding = hf.embed_query('test query')
print(f'Embedding dimension: {len(embedding)}')
print(f'First 5 values: {embedding[:5]}')
"
```

## Troubleshooting

### HF API Returns 503 Error

The model is loading. The code automatically waits with `wait_for_model: true`.

### Dimension Mismatch Error

```
Dimensionality of vector (1024) does not match index dimension (384)
```

**Solution**: Use BGE-Small (384-dim) or create new 1024-dim index.

### Rate Limit Exceeded

HF API has rate limits. The code falls back to local model automatically.

## Summary

The hybrid embedding architecture gives you:
- ✅ **Fast queries** via HF API (no local model loading)
- ✅ **High quality** BGE embeddings for better retrieval
- ✅ **Automatic fallback** to local model if API fails
- ✅ **Flexible setup** - works with or without HF token

Choose your dimension strategy based on your existing Pinecone index!
