# 🍜 Warung Digital API

REST API untuk sistem menu & pemesanan warung/UMKM lokal - dibangun dengan **FastAPI + SQLite + JWT Auth**.

## Fitur

- **Auth** - Register & Login dengan JWT token
- **Role-based access** - `owner` (kelola menu) & `cashier` (buat pesanan)
- **Menu CRUD** - Tambah, ubah, hapus, dan lihat menu
- **Order Management** - Buat pesanan, update status, lihat detail
- **Auto Docs** - Swagger UI tersedia di `/docs`

## Cara Menjalankan

### Lokal
```bash
# Clone repo
git clone https://github.com/Alice699/warung-digital.git
cd warung-digital

# Install dependencies
pip install -r requirements.txt

# Jalankan server
uvicorn main:app --reload
```

Buka **http://localhost:8000/docs** untuk Swagger UI.

### Dengan Docker
```bash
docker build -t warung-digital .
docker run -p 8000:8000 warung-digital
```

## Endpoint

### Auth
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/auth/register` | Daftarkan user baru |
| POST | `/auth/login` | Login, dapatkan JWT token |

### Menu
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/menu/` | Lihat semua menu |
| GET | `/menu/{id}` | Detail menu |
| POST | `/menu/` | Tambah menu (owner) |
| PUT | `/menu/{id}` | Update menu (owner) |
| DELETE | `/menu/{id}` | Hapus menu (owner) |

### Orders
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/orders/` | Buat pesanan baru |
| GET | `/orders/` | Lihat semua pesanan |
| GET | `/orders/{id}` | Detail pesanan |
| PATCH | `/orders/{id}/status` | Update status pesanan |

## Status Pesanan

`pending` → `preparing` → `ready` → `done` (atau `cancelled`)

## 🛠️ Tech Stack

- **Python 3.11**
- **FastAPI** — Web framework
- **SQLite** — Database
- **JWT (python-jose)** — Authentication
- **Passlib (bcrypt)** — Password hashing
- **Docker** — Containerization

## Author

**Robbian Saputra Gumay** - [@Alice699](https://github.com/Alice699)

---
> Dibuat dengan ❤️ dari Palembang, South Sumatera 🇮🇩
