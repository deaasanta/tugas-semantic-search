"""Semantic Search Materi Matematika SMA - FastAPI + SentenceTransformers + Qdrant.

Jalankan:  fastapi dev main.py   lalu buka http://127.0.0.1:8000/docs
Urutan pakai: POST /index (sekali) -> POST /search
"""
import json
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from search_engine import COLLECTION_NAME, MODEL_NAME, SemanticSearchEngine

DATA_PATH = Path(__file__).parent / "data.json"
QDRANT_PATH = Path(__file__).parent / "qdrant_data"

engine: SemanticSearchEngine | None = None


def load_documents() -> list[dict]:
    with open(DATA_PATH, encoding="utf-8") as f:
        docs = json.load(f)
    for d in docs:
        if not {"id", "text", "category"} <= d.keys():
            raise ValueError(f"Data tidak lengkap (wajib id, text, category): {d}")
    return docs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Model dan koneksi Qdrant dibuat SEKALI saat server start, bukan setiap request."""
    global engine
    if engine is None:
        from qdrant_client import QdrantClient
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(MODEL_NAME)
        client = QdrantClient(path=str(QDRANT_PATH))   # local persistent database
        engine = SemanticSearchEngine(model, client)
    yield
    engine.client.close()


app = FastAPI(
    title="Semantic Search Materi Matematika SMA",
    description="Mencari materi matematika berdasarkan makna (semantic similarity) dengan Qdrant.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------- schemas
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=300, examples=["cara mencari luas daerah di bawah grafik"])
    top_k: int = Field(3, ge=1, le=30, description="Jumlah hasil yang dikembalikan")
    category: str | None = Field(None, description="Opsional: batasi pencarian ke satu kategori",
                                 examples=[None])


class SearchResult(BaseModel):
    id: int
    title: str
    text: str
    category: str
    score: float


class SearchResponse(BaseModel):
    query: str
    top_k: int
    category_filter: str | None
    results: list[SearchResult]


# ---------------------------------------------------------------------------- endpoints
def get_engine() -> SemanticSearchEngine:
    if engine is None:
        raise HTTPException(status_code=503, detail="Model belum siap")
    return engine


@app.get("/health")
def health():
    eng = get_engine()
    return {
        "status": "OK",
        "model": MODEL_NAME,
        "vector_size": eng.vector_size,
        "collection": COLLECTION_NAME,
        "indexed": eng.is_indexed(),
        "points_in_collection": eng.count(),
    }


@app.post("/index")
def index_dataset():
    """Baca data.json, ubah setiap text menjadi embedding, simpan ke Qdrant beserta payload."""
    eng = get_engine()
    try:
        docs = load_documents()
    except (OSError, ValueError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=500, detail=f"Gagal membaca dataset: {e}")
    if not docs:
        raise HTTPException(status_code=400, detail="Dataset kosong")

    start = time.perf_counter()
    n = eng.index(docs)
    categories = sorted({d["category"] for d in docs})
    return {
        "message": "Dataset berhasil di-index ke Qdrant",
        "indexed": n,
        "categories": categories,
        "vector_size": eng.vector_size,
        "distance": "COSINE",
        "seconds": round(time.perf_counter() - start, 2),
    }


@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    eng = get_engine()
    if not eng.is_indexed() or eng.count() == 0:
        raise HTTPException(status_code=409, detail="Collection belum di-index. Jalankan POST /index terlebih dahulu.")
    query = request.query.strip()
    if len(query) < 2:
        raise HTTPException(status_code=422, detail="Query terlalu pendek")
    results = eng.search(query, request.top_k, request.category)
    return SearchResponse(query=query, top_k=request.top_k, category_filter=request.category, results=results)


@app.get("/documents")
def list_documents():
    """Melihat isi dataset (membantu memastikan query tidak menyalin kalimat dataset)."""
    return load_documents()
