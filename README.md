# The Papuan Thought Project

> An open-source platform for essays, reflections, and community writing from Papuans.

Diinisiasi oleh **Papua Open Source** — komunitas teknologi yang berkontribusi bagi Tanah Papua melalui perangkat lunak terbuka.

## Tentang Proyek

Platform ini dibuat sebagai ruang terbuka bagi masyarakat Papua untuk menulis dan membagikan perspektif, pengalaman, serta pemikiran mereka tentang Papua dalam bentuk esai, refleksi, cerita, dan gagasan tentang budaya, masyarakat, politik, teknologi, identitas, dan kehidupan sehari-hari.

## Fitur

- Tulis dan terbitkan esai dengan dukungan Markdown
- Tag yang dibuat langsung oleh penulis
- Profil penulis dengan riwayat esai dan koleksi simpan
- Reaksi (love) dan simpan (bookmark) per esai
- Komentar dan diskusi
- Sistem ikuti penulis
- Notifikasi: esai baru dari penulis yang diikuti dan rekomendasi sistem
- Panel admin menggunakan django-unfold

## Stack

- Python 3.13 + Django 6.x
- TailwindCSS v4 via django-tailwind
- Alpine.js untuk interaktivitas frontend
- django-unfold untuk panel admin
- SQLite (pengembangan) / PostgreSQL (produksi)
- uv sebagai package manager

## Memulai

Lihat [DEVELOPMENT.md](DEVELOPMENT.md) untuk panduan menjalankan proyek secara lokal.

## Kontribusi

Lihat [CONTRIBUTING.md](CONTRIBUTING.md) untuk panduan berkontribusi.

## Lisensi

AGPL-3.0 License. Lihat file [LICENSE](LICENSE) untuk detail lengkapnya.
