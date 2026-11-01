"""Logika semantic search: embedding dataset, simpan ke Qdrant, cari Top-K.

Encoder dan QdrantClient diberikan dari luar (dependency injection) supaya bisa
dites tanpa mengunduh model.
"""
from qdrant_client import QdrantClient
from qdrant_client.models import (Distance, FieldCondition, Filter, MatchValue, PointStruct,
                                  VectorParams)

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION_NAME = "materi_matematika"


class SemanticSearchEngine:
    def __init__(self, encoder, client: QdrantClient, collection_name: str = COLLECTION_NAME):
        self.encoder = encoder
        self.client = client
        self.collection_name = collection_name
        # ukuran vector diambil dari model, tidak di-hardcode (MiniLM-L12-v2 = 384)
        self.vector_size = encoder.get_sentence_embedding_dimension()

    # ------------------------------------------------------------------ embedding
    def embed(self, texts: list[str]):
        # normalize_embeddings=True: panjang vector = 1, sehingga cosine similarity = dot product
        return self.encoder.encode(texts, normalize_embeddings=True)

    # ------------------------------------------------------------------ indexing
    def index(self, documents: list[dict]) -> int:
        """Dataset -> embedding -> PointStruct (id, vector, payload) -> collection Qdrant.

        Collection dibuat ulang setiap kali index dipanggil agar tidak ada data ganda.
        """
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
        )

        vectors = self.embed([doc["text"] for doc in documents])
        points = [
            PointStruct(
                id=doc["id"],
                vector=vector.tolist(),
                payload={"text": doc["text"], "category": doc["category"], "title": doc.get("title", "")},
            )
            for doc, vector in zip(documents, vectors)
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)
        return len(points)

    # ------------------------------------------------------------------ status
    def is_indexed(self) -> bool:
        return self.client.collection_exists(self.collection_name)

    def count(self) -> int:
        if not self.is_indexed():
            return 0
        return self.client.count(collection_name=self.collection_name, exact=True).count

    # ------------------------------------------------------------------ search
    def search(self, query: str, top_k: int = 3, category: str | None = None) -> list[dict]:
        """Query -> embedding -> query vector -> Qdrant -> Top-K hasil paling mirip."""
        query_vector = self.embed([query])[0].tolist()
        query_filter = None
        if category:
            query_filter = Filter(must=[FieldCondition(key="category", match=MatchValue(value=category))])

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )
        return [
            {
                "id": point.id,
                "title": point.payload.get("title", ""),
                "text": point.payload["text"],
                "category": point.payload["category"],
                "score": round(point.score, 4),
            }
            for point in response.points
        ]
