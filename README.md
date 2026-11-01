# Semantic Search & Vector Database

> Petunjuk (hapus sebelum dikumpulkan): bagian **[ISI SENDIRI]** wajib diisi dengan hasil aplikasi yang kamu jalankan
> sendiri dan pendapatmu sendiri. Similarity score harus berasal dari aplikasi, jangan ditebak.
> Cara menjalankan dan cara mengambil hasil eksperimen ada di bagian paling bawah.

## Project Information

**Nama Project:**
Semantic Search Materi Matematika SMA

**Tema Dataset:**
Materi Matematika SMA

**Deskripsi Singkat:**
Aplikasi untuk mencari penjelasan materi matematika SMA berdasarkan makna pertanyaan, bukan kecocokan kata. Siswa bisa
mengetik pertanyaan dengan bahasanya sendiri (misalnya "cara mencari luas daerah di bawah grafik") dan aplikasi
menemukan materi yang relevan (integral tentu) beserta similarity score-nya.

## Dataset

### Jumlah Data

30 data (`data.json`), masing-masing memiliki `id`, `title`, `text`, dan `category`.

### Kategori yang Digunakan

| Kategori | Jumlah data |
|---|---|
| `aljabar` | 6 |
| `trigonometri` | 6 |
| `kalkulus` | 6 |
| `statistika_peluang` | 6 |
| `geometri` | 6 |

### Kenapa kalian memilih dataset tersebut?

[ISI SENDIRI]

## Tech Stack

- Python 3.10+
- FastAPI (REST API, dokumentasi otomatis di `/docs`)
- Pydantic (validasi request body)
- SentenceTransformers dengan model `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (vector 384 dimensi)
- Qdrant (`qdrant-client`, local persistent mode di folder `qdrant_data/`, distance COSINE)
- pytest (test alur index dan search memakai encoder palsu + Qdrant in-memory)

## Application Flow

```
Indexing (POST /index):
Dataset (data.json)
↓
Embedding Model (SentenceTransformer, normalize_embeddings=True)
↓
Vector (384 dimensi per data)
↓
Qdrant (PointStruct: id + vector + payload {text, category, title})

Searching (POST /search):
User Query
↓
Embedding Model (model yang sama)
↓
Query Vector
↓
Qdrant Search (query_points, cosine similarity, limit = top_k)
↓
Top-K Results (text, category, score)
```

**Penjelasan kalian:**

[ISI SENDIRI]

## Embedding Model

Model yang digunakan:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

**Menurut kalian, apa fungsi embedding model pada project ini?**

[ISI SENDIRI]

## Vector Database

**Apa fungsi Qdrant pada aplikasi kalian?**

[ISI SENDIRI]

**Apa saja data yang kalian simpan di payload?**

Setiap point menyimpan payload:

```json
{"text": "isi materi", "category": "kategori materi", "title": "judul materi"}
```

`text` dan `category` ditampilkan di hasil pencarian; `category` juga dipakai untuk filter opsional pada `/search`;
`title` membantu membaca hasil dengan cepat. ID point sama dengan `id` di `data.json`.

## API Endpoint

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/health` | Status aplikasi, model, ukuran vector, dan jumlah point di Qdrant |
| POST | `/index` | Membaca `data.json`, membuat embedding, dan menyimpan ke Qdrant (collection dibuat ulang agar tidak duplikat) |
| POST | `/search` | Semantic search. Body: `query` (wajib), `top_k` (1–30, default 3), `category` (opsional) |
| GET | `/documents` | Menampilkan isi dataset |

## Example Request

[ISI SENDIRI — salin dari `experiment_results.md` bagian Example Request]

## Example Response

[ISI SENDIRI — salin dari `experiment_results.md` bagian Example Response]

## Experiment 1 - Semantic Search

### Query 1

**Query:**

[ISI SENDIRI]

**Top Result:**

[ISI SENDIRI]

**Similarity Score:**

[ISI SENDIRI]

**Menurut kalian apakah hasilnya relevan? Kenapa?**

[ISI SENDIRI]

### Query 2

**Query:**

[ISI SENDIRI]

**Top Result:**

[ISI SENDIRI]

**Similarity Score:**

[ISI SENDIRI]

**Menurut kalian apakah hasilnya relevan? Kenapa?**

[ISI SENDIRI]

### Query 3

**Query:**

[ISI SENDIRI]

**Top Result:**

[ISI SENDIRI]

**Similarity Score:**

[ISI SENDIRI]

**Menurut kalian apakah hasilnya relevan? Kenapa?**

[ISI SENDIRI]

### Query 4

**Query:**

[ISI SENDIRI]

**Top Result:**

[ISI SENDIRI]

**Similarity Score:**

[ISI SENDIRI]

**Menurut kalian apakah hasilnya relevan? Kenapa?**

[ISI SENDIRI]

### Query 5

**Query:**

[ISI SENDIRI]

**Top Result:**

[ISI SENDIRI]

**Similarity Score:**

[ISI SENDIRI]

**Menurut kalian apakah hasilnya relevan? Kenapa?**

[ISI SENDIRI]

## Experiment 2 - Top-K

Gunakan query yang sama.

**Query**

[ISI SENDIRI]

### Top-K = 1

**Actual Result:**

[ISI SENDIRI]

### Top-K = 3

**Actual Result:**

[ISI SENDIRI]

### Top-K = 5

**Actual Result:**

[ISI SENDIRI]

**Apa perubahan yang kalian lihat ketika nilai Top-K diperbesar?**

[ISI SENDIRI]

**Apakah menambah Top-K selalu membuat hasil pencarian menjadi lebih baik?**

[ISI SENDIRI — perhatikan skor hasil ke-4 dan ke-5: apakah masih relevan?]

## Experiment 3 - Bad Retrieval

**Query**

[ISI SENDIRI — pilih dari kandidat di `experiment_results.md` yang hasilnya benar-benar aneh, atau buat query sendiri]

**Actual Results**

[ISI SENDIRI]

**Similarity Score**

[ISI SENDIRI]

**Kenapa menurut kalian hasil tersebut kurang relevan?**

[ISI SENDIRI]

**Menurut kalian apa yang mungkin menyebabkan hasil tersebut?**

[ISI SENDIRI]

## Personal Reflection

**1. Sebelum mengerjakan tugas ini, bagaimana kalian membayangkan sebuah search engine bekerja? Apakah ada perbedaan setelah mempelajari semantic search?**

[ISI SENDIRI]

**2. Menurut kalian apa perbedaan terbesar antara keyword search dan semantic search?**

[ISI SENDIRI]

**3. Menurut kalian apa fungsi embedding di dalam semantic search?**

[ISI SENDIRI]

**4. Kenapa embedding tidak cukup hanya disimpan di list Python jika jumlah data menjadi sangat banyak?**

[ISI SENDIRI]

**5. Bagian project mana yang paling sulit kalian pahami?**

[ISI SENDIRI]

**6. Bagian kode mana yang paling banyak dibantu oleh AI?**

[ISI SENDIRI]

**7. Jelaskan dengan bahasa kalian sendiri bagaimana bagian kode tersebut bekerja.**

[ISI SENDIRI]

**8. Menurut kalian, aplikasi semantic search yang kalian buat bisa dikembangkan menjadi aplikasi apa jika project ini dilanjutkan?**

[ISI SENDIRI]

## AI Usage

**AI tools yang digunakan**

[ISI SENDIRI]

**AI digunakan untuk membantu bagian apa?**

[ISI SENDIRI]

**Bagian apa yang kalian ubah atau tentukan sendiri setelah mendapatkan hasil dari AI?**

[ISI SENDIRI]

---

## Cara Menjalankan

```bash
python -m venv venv
# Windows: venv\Scripts\activate     macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
fastapi dev main.py          # run pertama mengunduh model (±470 MB), butuh internet
```

Buka http://127.0.0.1:8000/docs, jalankan `POST /index` sekali, lalu coba `POST /search`:

```json
{"query": "cara mencari luas daerah yang dibatasi grafik", "top_k": 3}
```

Test (tidak mengunduh model): `pytest -q`

## Cara Mengambil Hasil Eksperimen

Dengan server tetap berjalan, buka terminal kedua:

```bash
python run_experiments.py
```

Script memanggil `/search` di aplikasi yang sedang berjalan dan menyimpan hasil aktual Experiment 1–3 ke
`experiment_results.md`. Salin angka dan hasilnya ke README, lalu tulis pendapatmu sendiri. Query di dalam script
boleh diganti dengan query buatanmu.

## Struktur Project

```
tugas-semantic-search/
├── main.py              # FastAPI: /health, /index, /search, /documents
├── search_engine.py     # embedding, indexing ke Qdrant, query Top-K
├── data.json            # 30 materi matematika SMA, 5 kategori
├── run_experiments.py   # mengambil hasil aktual eksperimen dari API
├── tests/test_api.py    # pytest (encoder palsu + Qdrant in-memory)
├── requirements.txt
└── .gitignore           # venv/, __pycache__/, qdrant_data/
```
