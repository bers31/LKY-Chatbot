# Data sources

Dokumen sumber untuk chatbot ini disimpan di dua tempat:

- `data/sources.json` — metadata (judul, tanggal, tipe dokumen, topik, URL sumber).
  File ini di-commit ke repo publik.
- `data/raw/` — file PDF/teks asli, hanya di komputer lokal. **Tidak di-commit**
  (lihat `.gitignore`), karena sebagian besar sumber berasal dari National
  Archives of Singapore yang Terms of Use-nya melarang redistribusi ulang
  tanpa izin tertulis — lihat https://corporate.nas.gov.sg/terms-of-use/.
  Hanya diunduh untuk penggunaan riset personal, sesuai izin yang diberikan
  di Terms of Use tersebut.

Untuk mereproduksi dataset ini, evaluator dapat mengunjungi `source_url` di
`sources.json` dan mengunduh sendiri salinan untuk keperluan riset personal.