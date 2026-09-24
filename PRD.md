# PRD: SecretNotes — Aplikasi Catatan Rahasia Berenkripsi AES

> Dokumen ini ditulis agar dapat dibaca oleh manusia dan AI agent. Setiap kebutuhan punya ID unik (F1, NF1, dst.) dan kriteria penerimaan (acceptance criteria) yang bisa diuji. Bagian "Keputusan Desain" berisi nilai default; ubah jika ada keputusan lain.

## 1. Ringkasan

SecretNotes adalah aplikasi web untuk menyimpan catatan pribadi yang dienkripsi dengan AES sebelum masuk database. Aplikasi ini juga berfungsi sebagai media belajar kriptografi: pengguna dapat melihat matriks hexadecimal blok pertama dan proses key expansion (round keys).

**Konteks:** proyek akademik (D3 Teknik Informatika). Kode harus sederhana, mudah dibaca, dan mudah dijelaskan.

## 2. Tujuan dan Non-Tujuan

**Tujuan**
- Catatan di database hanya berupa ciphertext.
- Menampilkan cara kerja AES secara visual.
- Kode sederhana dan berkomentar.

**Non-tujuan (v1)**
- Multi-user / berbagi catatan
- Lampiran file
- Sinkronisasi offline
- Aplikasi mobile

## 3. Tech Stack

| Lapisan | Teknologi |
|---|---|
| Frontend | Vue.js 3 (Composition API), Vite, Vue Router, Pinia |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Database | Supabase (PostgreSQL) |
| Kripto | Implementasi AES manual (`aes.py`), PBKDF2 (`hashlib`), pembanding uji: `pycryptodome` |
| Pengujian | pytest (backend), Vitest (frontend, opsional) |

## 4. Keputusan Desain (Default)

| # | Keputusan | Default | Alternatif |
|---|---|---|---|
| D1 | Lokasi enkripsi | Backend Python | Sisi klien (lebih privat, AES manual di JS) |
| D2 | Ukuran kunci | AES-128 (10 ronde, 11 round key) | AES-256 |
| D3 | Mode operasi | CBC + IV acak per catatan | GCM (dengan autentikasi) |
| D4 | Judul catatan | Dienkripsi (agar daftar tetap rahasia) | Plaintext |
| D5 | Jumlah pengguna | Satu pengguna, satu PIN | Multi-akun via Supabase Auth |
| D6 | Timeout auto-lock | 3 menit | Dapat diatur pengguna |

## 5. Kebutuhan Fungsional

### F1 — Akses dengan PIN/Password
- Saat pertama kali dibuka, pengguna membuat PIN (minimal 6 karakter).
- PIN disimpan sebagai hash (bcrypt/argon2), bukan plaintext.
- Aplikasi tidak bisa diakses tanpa PIN benar.
- **Acceptance:** PIN salah menampilkan error; 5 kali salah beruntun mengunci login selama 60 detik.

### F2 — Membuat Catatan
- Input: judul dan isi.
- Isi (dan judul, sesuai D4) dienkripsi lalu disimpan bersama IV.
- **Acceptance:** baris baru di tabel `notes` hanya berisi ciphertext dan IV; teks asli tidak ditemukan di database.

### F3 — Daftar Catatan
- Menampilkan daftar catatan dengan judul (didekripsi saat sesi terbuka) dan tanggal ubah.
- Isi catatan tidak ditampilkan di daftar.
- **Acceptance:** daftar diurutkan dari yang terbaru.

### F4 — Membuka Catatan (Dekripsi)
- Ciphertext diambil, didekripsi dengan kunci sesi, lalu ditampilkan.
- **Acceptance:** isi yang tampil sama persis dengan yang disimpan; jika sesi terkunci, permintaan ditolak (401).

### F5 — Mengedit Catatan
- Isi baru dienkripsi ulang dengan **IV baru**.
- **Acceptance:** `updated_at` berubah; IV berbeda dari sebelumnya.

### F6 — Menghapus Catatan
- Dengan dialog konfirmasi.
- **Acceptance:** baris terhapus dari database dan hilang dari daftar.

### F7 — Log Matriks Hexadecimal (Blok Pertama)
- Menampilkan 16 byte pertama plaintext sebagai matriks 4×4 hex (urutan column-major sesuai standar AES).
- Menampilkan state setelah tiap tahap per ronde: AddRoundKey awal, lalu SubBytes, ShiftRows, MixColumns, AddRoundKey untuk ronde 1–9, dan ronde 10 tanpa MixColumns.
- **Acceptance:** output ronde akhir sama dengan 16 byte pertama ciphertext (ECB untuk satu blok) dari `pycryptodome` untuk kunci dan plaintext yang sama.

### F8 — Visualisasi Round Keys (Key Expansion)
- Menampilkan 11 round key (masing-masing matriks 4×4 hex) hasil key expansion.
- Menandai word yang melewati `RotWord`, `SubWord`, dan `Rcon`.
- **Acceptance:** untuk kunci uji FIPS-197 `2b7e151628aed2a6abf7158809cf4f3c`, round key 1 adalah `a0fafe1788542cb123a339392a6c7605`.

### F9 — Auto-Lock
- Timer idle di frontend (reset pada mouse, keyboard, touch, scroll).
- Saat habis: panggil `/auth/lock`, hapus state catatan dari memori frontend, kembali ke layar PIN.
- Menampilkan indikator sisa waktu (opsional).
- **Acceptance:** setelah 3 menit tanpa aktivitas, halaman terkunci dan token sesi tidak valid lagi.

## 6. Kebutuhan Non-Fungsional

| ID | Kebutuhan |
|---|---|
| NF1 | Semua komunikasi lewat HTTPS. |
| NF2 | Kunci AES tidak pernah ditulis ke database, log, atau disk. |
| NF3 | Row Level Security aktif di Supabase; backend memakai service key yang disimpan di `.env`, tidak di frontend. |
| NF4 | Buka/simpan catatan ≤ 10 KB selesai < 1 detik. |
| NF5 | UI responsif (desktop dan mobile browser). |
| NF6 | Kode modular, diberi komentar, tanpa abstraksi berlebihan. |

## 7. Rancangan Kriptografi

- **Turunan kunci:** `PBKDF2-HMAC-SHA256(PIN, kdf_salt, iterasi ≥ 100000, panjang 16 byte)` → kunci AES-128.
- **Verifikasi PIN:** hash terpisah (bcrypt/argon2), berbeda dari kunci turunan.
- **Enkripsi:** AES-128 CBC, IV acak 16 byte per catatan, padding PKCS#7.
- **Penyimpanan:** ciphertext dan IV dalam base64.
- **Sesi:** setelah unlock, kunci turunan disimpan di memori server terikat token sesi berumur pendek, dihapus saat lock/expired.
- **Modul AES manual** harus mengekspos fungsi:
  - `key_expansion(key) -> list[round_key]`
  - `encrypt_block(block, round_keys, trace=False) -> ciphertext, trace`
  - `decrypt_block(block, round_keys) -> plaintext`
  - `sub_bytes`, `shift_rows`, `mix_columns`, `add_round_key`, beserta kebalikannya
- Pengujian silang dengan `pycryptodome` dan test vector FIPS-197 wajib lulus.

## 8. Arsitektur

```
Vue.js (UI, idle timer)  <->  FastAPI (REST)  <->  Supabase (PostgreSQL)
                                 |
                                 +-- aes.py, kdf.py, session store
```

### Struktur Folder

```
secretnotes/
├── backend/
│   ├── app/
│   │   ├── main.py            # inisialisasi FastAPI, CORS
│   │   ├── config.py          # baca .env
│   │   ├── db.py              # klien Supabase
│   │   ├── crypto/
│   │   │   ├── aes.py         # implementasi AES manual + trace
│   │   │   ├── kdf.py         # PBKDF2, hash PIN
│   │   │   └── modes.py       # CBC + padding PKCS#7
│   │   ├── session.py         # penyimpanan kunci sesi + expiry
│   │   ├── schemas.py         # model Pydantic
│   │   └── routes/
│   │       ├── auth.py
│   │       └── notes.py
│   ├── tests/
│   │   ├── test_aes.py        # test vector FIPS-197 + banding pycryptodome
│   │   └── test_notes.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── main.js
    │   ├── router/index.js
    │   ├── stores/            # auth.js, notes.js (Pinia)
    │   ├── api/client.js      # wrapper fetch + token
    │   ├── composables/useIdleLock.js
    │   ├── views/             # LockView, NotesView, NoteEditorView, AesLabView
    │   └── components/        # HexMatrix.vue, RoundKeys.vue, NoteList.vue
    └── package.json
```

## 9. Skema Database (Supabase / PostgreSQL)

```sql
create table app_settings (
  id uuid primary key default gen_random_uuid(),
  pin_hash text not null,
  kdf_salt text not null,            -- base64
  idle_timeout_sec int not null default 180,
  created_at timestamptz default now()
);

create table notes (
  id uuid primary key default gen_random_uuid(),
  title_ciphertext text not null,    -- base64
  title_iv text not null,            -- base64
  body_ciphertext text not null,     -- base64
  body_iv text not null,             -- base64
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table app_settings enable row level security;
alter table notes enable row level security;
-- Akses hanya lewat service key di backend; tanpa policy publik.
```

## 10. Spesifikasi API

Semua endpoint selain `/auth/setup` dan `/auth/unlock` membutuhkan header `Authorization: Bearer <session_token>`.

| Method | Endpoint | Body | Respons |
|---|---|---|---|
| POST | `/auth/setup` | `{pin}` | 201; hanya bisa dipanggil jika belum ada `app_settings` |
| POST | `/auth/unlock` | `{pin}` | `{token, expires_in}`; 401 jika salah; 429 jika terkena lockout |
| POST | `/auth/lock` | - | 204; sesi dan kunci dihapus |
| GET | `/notes` | - | `[{id, title, updated_at}]` (judul didekripsi) |
| POST | `/notes` | `{title, body}` | `{id}` |
| GET | `/notes/{id}` | - | `{id, title, body, created_at, updated_at}` |
| PUT | `/notes/{id}` | `{title, body}` | 200 |
| DELETE | `/notes/{id}` | - | 204 |
| GET | `/notes/{id}/aes-log` | - | matriks input blok pertama + trace per ronde (hex) |
| GET | `/notes/{id}/round-keys` | - | `{round_keys: [11 x matriks 4x4 hex]}` + info RotWord/SubWord/Rcon |

Format error seragam: `{"detail": "pesan"}` dengan kode HTTP yang sesuai.

## 11. Layar Antarmuka

1. **LockView** — input PIN, tombol buka, pesan error/lockout. Mode setup PIN jika belum ada PIN.
2. **NotesView** — daftar catatan, tombol "Catatan Baru", indikator sisa waktu auto-lock.
3. **NoteEditorView** — input judul dan isi, tombol simpan/hapus.
4. **AesLabView** — tab "Blok Pertama" (matriks hex per ronde) dan tab "Round Keys" (11 matriks).

## 12. Milestone dan Urutan Pengerjaan

| Tahap | Isi | Selesai bila |
|---|---|---|
| 1 | Modul AES manual + key expansion + trace | `test_aes.py` lulus (FIPS-197 + banding pycryptodome) |
| 2 | KDF, hash PIN, mode CBC + padding | Enkripsi-dekripsi bolak-balik benar |
| 3 | Backend: auth, sesi, CRUD, Supabase | Semua endpoint F1–F6 berfungsi |
| 4 | Endpoint `aes-log` dan `round-keys` | F7 dan F8 acceptance terpenuhi |
| 5 | Frontend: LockView, daftar, editor, auto-lock | F1–F6 dan F9 berjalan end-to-end |
| 6 | Frontend: AesLabView | Visualisasi sesuai backend |
| 7 | Pengujian akhir dan dokumentasi | Semua acceptance criteria lulus |

## 13. Kriteria Keberhasilan Keseluruhan

- [ ] Isi database tidak bisa dibaca tanpa PIN.
- [ ] Hasil AES manual identik dengan `pycryptodome` dan test vector FIPS-197.
- [ ] Matriks hex dan 11 round key tampil benar.
- [ ] Auto-lock bekerja dan token sesi tidak valid setelah lock.
- [ ] Tidak ada kunci, PIN, atau plaintext catatan di database maupun log.

## 14. Risiko dan Catatan

| Risiko | Mitigasi |
|---|---|
| PIN pendek mudah ditebak (brute force pada hash) | Minimal 6 karakter, KDF dengan iterasi tinggi, lockout login |
| AES manual rentan salah implementasi dan side-channel | Cukup untuk tujuan edukasi; uji silang dengan pustaka standar; jelaskan bahwa produksi sebaiknya memakai pustaka teruji |
| Kunci di memori server | Dihapus saat lock/expired; token berumur pendek |
| CBC tanpa autentikasi | Catat sebagai batasan; GCM sebagai pengembangan lanjutan |

## 15. Instruksi untuk AI Agent

- Kerjakan berurutan sesuai bagian 12; jangan lompat tahap.
- Utamakan kode sederhana dan mudah dibaca, dengan komentar singkat pada langkah-langkah AES.
- Jangan menambah fitur di luar bagian 5.
- Jika ada keputusan di bagian 4 yang diubah, sesuaikan bagian 7–10 dan konfirmasi ke pengguna sebelum melanjutkan.
- Jangan menyimpan PIN, kunci AES, atau plaintext di database atau log.
