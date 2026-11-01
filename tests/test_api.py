"""Test tanpa mengunduh model: encoder palsu + Qdrant in-memory.

Encoder palsu hanya menghitung kata (bukan makna), jadi test ini menguji alur
index -> Qdrant -> search dan error handling, BUKAN kualitas semantic search.

Jalankan:  pytest -q
"""
import hashlib

import numpy as np
import pytest
from fastapi.testclient import TestClient
from qdrant_client import QdrantClient

import main
from search_engine import SemanticSearchEngine

DIM = 384


class FakeEncoder:
    def get_sentence_embedding_dimension(self):
        return DIM

    def encode(self, texts, normalize_embeddings=True):
        out = np.zeros((len(texts), DIM), dtype=np.float32)
        for i, t in enumerate(texts):
            for w in t.lower().split():
                out[i, int(hashlib.md5(w.encode()).hexdigest(), 16) % DIM] += 1
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        return out / np.where(norms == 0, 1, norms)


@pytest.fixture()
def client():
    main.engine = SemanticSearchEngine(FakeEncoder(), QdrantClient(":memory:"))
    yield TestClient(main.app)      # tanpa "with": lifespan (model asli) tidak dijalankan
    main.engine = None


def test_dataset_requirements():
    docs = main.load_documents()
    assert 20 <= len(docs) <= 50
    assert len({d["category"] for d in docs}) >= 3
    assert all(d["text"] and d["category"] for d in docs)
    assert len({d["id"] for d in docs}) == len(docs)


def test_search_before_index_returns_409(client):
    r = client.post("/search", json={"query": "turunan fungsi", "top_k": 3})
    assert r.status_code == 409


def test_index_then_health(client):
    r = client.post("/index")
    assert r.status_code == 200
    assert r.json()["indexed"] == len(main.load_documents())
    h = client.get("/health").json()
    assert h["indexed"] is True and h["points_in_collection"] == r.json()["indexed"]
    assert h["vector_size"] == DIM


def test_index_twice_no_duplicates(client):
    client.post("/index")
    client.post("/index")
    assert client.get("/health").json()["points_in_collection"] == len(main.load_documents())


@pytest.mark.parametrize("k", [1, 3, 5])
def test_top_k(client, k):
    client.post("/index")
    body = client.post("/search", json={"query": "luas lingkaran jari-jari", "top_k": k}).json()
    assert len(body["results"]) == k
    first = body["results"][0]
    assert {"text", "category", "score"} <= first.keys()
    scores = [x["score"] for x in body["results"]]
    assert scores == sorted(scores, reverse=True)


def test_category_filter(client):
    client.post("/index")
    body = client.post("/search", json={"query": "sudut", "top_k": 5, "category": "trigonometri"}).json()
    assert body["results"] and all(x["category"] == "trigonometri" for x in body["results"])


@pytest.mark.parametrize("payload", [{"query": "", "top_k": 3}, {"query": "limit", "top_k": 0},
                                     {"query": "limit", "top_k": 100}, {"top_k": 3}])
def test_invalid_request_returns_422(client, payload):
    client.post("/index")
    assert client.post("/search", json=payload).status_code == 422
