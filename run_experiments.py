"""Menjalankan Experiment 1-3 ke aplikasi yang SEDANG BERJALAN dan menyimpan hasil aktualnya.

Langkah:
  1. Terminal 1:  fastapi dev main.py
  2. Terminal 2:  python run_experiments.py
  3. Buka experiment_results.md, salin hasilnya ke README, lalu tulis pendapatmu sendiri.

Query di bawah boleh (dan sebaiknya) kamu ganti dengan query buatanmu sendiri.
"""
import json

import httpx

BASE_URL = "http://127.0.0.1:8000"

# Experiment 1: 5 query natural, tidak menyalin kalimat dataset
EXP1_QUERIES = [
    "cara mencari luas daerah yang dibatasi grafik",
    "menghitung panjang sisi terpanjang segitiga yang punya sudut 90 derajat",
    "berapa banyak cara memilih pengurus kelas kalau urutannya tidak penting",
    "mencari ukuran wadah supaya isinya paling banyak",
    "seberapa tersebar nilai ujian satu kelas",
]

# Experiment 2: satu query yang sama untuk top_k 1, 3, 5
EXP2_QUERY = "rumus yang berhubungan dengan segitiga"

# Experiment 3: kandidat bad retrieval (pilih yang hasilnya benar-benar aneh)
EXP3_CANDIDATES = [
    "materi yang tidak ada hubungannya dengan segitiga",   # negasi
    "resep membuat kue bolu",                               # di luar topik dataset
    "dua pi",                                               # query sangat pendek & ambigu
    "pangkat",                                              # satu kata, beberapa materi memakai kata ini
]


def search(client: httpx.Client, query: str, top_k: int) -> dict:
    r = client.post(f"{BASE_URL}/search", json={"query": query, "top_k": top_k})
    r.raise_for_status()
    return r.json()


def fmt(results: list[dict]) -> str:
    return "\n".join(f"{i}. [{x['category']}] {x['text']} — score **{x['score']:.4f}**"
                     for i, x in enumerate(results, 1))


def main():
    out = []
    with httpx.Client(timeout=60) as client:
        health = client.get(f"{BASE_URL}/health").json()
        if not health.get("indexed"):
            print("Collection belum di-index, menjalankan POST /index ...")
            print(client.post(f"{BASE_URL}/index").json())

        example_req = {"query": EXP1_QUERIES[0], "top_k": 3}
        out.append("## Example Request / Response (actual)\n")
        out.append("```json\n" + json.dumps(example_req, ensure_ascii=False, indent=2) + "\n```\n")
        out.append("```json\n" + json.dumps(search(client, **example_req), ensure_ascii=False, indent=2) + "\n```\n")

        out.append("## Experiment 1 - Semantic Search\n")
        for i, q in enumerate(EXP1_QUERIES, 1):
            res = search(client, q, 3)["results"]
            top = res[0]
            out.append(f"### Query {i}\n\nQuery: `{q}`\n\nTop Result: [{top['category']}] {top['text']}\n\n"
                       f"Similarity Score: {top['score']:.4f}\n\nTop-3 lengkap:\n\n{fmt(res)}\n")

        out.append("## Experiment 2 - Top-K\n")
        out.append(f"Query: `{EXP2_QUERY}`\n")
        for k in (1, 3, 5):
            out.append(f"### Top-K = {k}\n\n{fmt(search(client, EXP2_QUERY, k)['results'])}\n")

        out.append("## Experiment 3 - Kandidat Bad Retrieval (pilih minimal 1)\n")
        for q in EXP3_CANDIDATES:
            out.append(f"### `{q}`\n\n{fmt(search(client, q, 3)['results'])}\n")

    text = "\n".join(out)
    with open("experiment_results.md", "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print("\nTersimpan di experiment_results.md")


if __name__ == "__main__":
    main()
