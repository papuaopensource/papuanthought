# Panduan Pengembangan

## Prasyarat

- Python 3.13
- [uv](https://docs.astral.sh/uv/) sebagai package manager
- Node.js (dibutuhkan oleh django-tailwind untuk kompilasi CSS)

## Setup Lokal

Clone repositori dan masuk ke direktori proyek.

```bash
git clone <url-repositori>
cd papuan-thought-project
```

Install dependensi Python menggunakan uv.

```bash
uv sync
```

Salin file konfigurasi environment.

```bash
cp .env.example .env
```

Sesuaikan isi `.env` jika diperlukan. Untuk pengembangan lokal, nilai default sudah cukup.

Pastikan variabel berikut ada di `.env`:

```
DJANGO_SETTINGS_MODULE=django_project.settings.development
SECRET_KEY=secret-key-lokal-anda
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Jalankan migrasi database.

```bash
uv run python manage.py migrate
```

Buat akun superuser untuk mengakses panel admin.

```bash
uv run python manage.py createsuperuser
```

Isi data contoh (opsional).

```bash
uv run python manage.py seed_data
```

Untuk mengulang dari awal, gunakan flag `--flush`.

```bash
uv run python manage.py seed_data --flush
```

## Menjalankan Server

Proyek membutuhkan dua proses yang berjalan bersamaan: server Django dan proses kompilasi TailwindCSS.

Terminal pertama — server Django:

```bash
uv run python manage.py runserver
```

Terminal kedua — Tailwind:

```bash
uv run python manage.py tailwind start
```

Aplikasi dapat diakses di `http://127.0.0.1:8000`.

Panel admin tersedia di `http://127.0.0.1:8000/site-manager/`.

## Struktur Proyek

```
accounts/        pengguna, profil, autentikasi
essays/          esai, tag, penerbitan
interactions/    komentar, reaksi, ikuti, simpan, notifikasi
commons/         halaman statis (tentang, panduan, privasi, dll)
templates/       layout utama dan partial (navbar, footer)
theme/           konfigurasi TailwindCSS
django_project/  settings, urls, wsgi
```

Setiap app memiliki `services.py` yang berisi logika bisnis. View hanya memanggil fungsi dari services, tidak mengandung logika langsung.

Semua view ditulis sebagai Class-Based View (CBV).

## Migrasi

Setelah mengubah model, buat dan terapkan migrasi.

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

## Pemeriksaan Sistem

```bash
uv run python manage.py check
```
