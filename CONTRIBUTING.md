# Panduan Kontribusi

Terima kasih sudah meluangkan waktu untuk berkontribusi. Proyek ini terbuka untuk siapa saja yang ingin membantu membangun ruang digital untuk suara-suara Papua.

## Cara Melaporkan Masalah

Gunakan fitur Issues di repositori GitHub untuk melaporkan bug atau mengusulkan fitur baru. Sertakan langkah-langkah untuk mereproduksi masalah jika memungkinkan.

## Alur Kontribusi

Fork repositori, lalu buat branch baru dari `main`.

Penamaan branch:

- `feat/nama-fitur` untuk fitur baru
- `fix/nama-perbaikan` untuk perbaikan bug
- `docs/nama-perubahan` untuk perubahan dokumentasi

Buat perubahan, pastikan proyek tetap berjalan dengan benar, lalu kirim pull request ke branch `main`.

## Standar Kode

**Views** — Semua view ditulis sebagai Class-Based View (CBV). Function-based view tidak digunakan.

**Logika bisnis** — Taruh di `services.py` masing-masing app. View hanya memanggil fungsi dari services.

**Migrasi** — Selalu sertakan file migrasi jika ada perubahan model.

**Komentar** — Tulis hanya jika ada sesuatu yang tidak jelas dari kode itu sendiri.

## Pesan Commit

Proyek ini mengikuti konvensi [Conventional Commits](https://www.conventionalcommits.org).

Format:

```
<type>(<scope>): <deskripsi singkat>
```

Type yang umum digunakan:

- `feat` — fitur baru
- `fix` — perbaikan bug
- `docs` — perubahan dokumentasi
- `refactor` — perubahan kode tanpa menambah fitur atau memperbaiki bug
- `style` — perubahan tampilan atau format
- `chore` — pemeliharaan, konfigurasi, dependensi

Contoh:

```
feat(essays): add essay edit functionality
fix(notifications): correct unread badge count on reload
docs(readme): update local setup instructions
refactor(interactions): extract tag helper into shared function
```

## Pertanyaan

Hubungi tim Papua Open Source melalui halaman kontak di platform atau buka diskusi di repositori GitHub.
