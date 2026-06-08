
# MemoryRAG

### Built MemoryRAG, a full-stack long-term memory RAG system using FastAPI, React, FAISS, and BGE-M3, supporting conversational memory updates, memory decay scoring, hybrid retrieval, and retrieval evaluation.
```
MemoryRAG/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   └── memory.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── llm.py
│   │   ├── rag/
│   │   │   ├── chunker.py
│   │   │   ├── embedder.py
│   │   │   ├── vector_store.py
│   │   │   ├── retriever.py
│   │   │   └── reranker.py
│   │   ├── memory/
│   │   │   ├── memory_manager.py
│   │   │   ├── memory_decay.py
│   │   │   └── memory_schema.py
│   │   └── eval/
│   │       ├── metrics.py
│   │       └── benchmark.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   └── App.jsx
│   └── package.json
│
├── experiments/
│   ├── memory_decay_demo.ipynb
│   └── retrieval_eval.ipynb
│
├── data/
├── docs/
├── docker-compose.yml
└── README.md
```
