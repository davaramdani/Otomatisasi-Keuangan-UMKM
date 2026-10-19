# Otomatisasi Keuangan UMKM

Bot Telegram untuk membantu pencatatan keuangan dan pengelolaan stok UMKM, dengan Google Sheets sebagai penyimpanan data dan Groq untuk membaca perintah serta struk belanja.

## Fitur

- Mencatat pengeluaran melalui `/catat`.
- Membaca foto struk dan mencatat belanja.
- Mengelola stok melalui `/stok`.
- Membuat invoice PDF melalui `/invoice`.
- Menampilkan rekap pengeluaran dan penjualan melalui `/rekap`.
- Melayani perintah dalam percakapan teks.

## Menjalankan secara lokal

Gunakan Python 3.10 atau lebih baru. Jalankan perintah berikut di PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Isi `.env` dengan token bot Telegram, API key Groq, dan ID Google Spreadsheet. Simpan kunci service account Google sebagai `credentials.json` di folder utama proyek, lalu bagikan spreadsheet kepada alamat email service account tersebut dengan akses editor. Aktifkan Google Sheets API dan Google Drive API untuk proyek Google Cloud yang digunakan.

Siapkan worksheet berikut beserta header-nya:

| Worksheet | Header kolom berurutan |
| --- | --- |
| Pengeluaran | Tanggal, Keterangan, Jumlah, Kategori, Sumber |
| Penjualan | Tanggal, Invoice No, Pembeli, Total, Status |
| Detail Penjualan | Invoice No, Item, Qty, Harga Satuan, Subtotal |
| Stok | Nama Barang, Satuan, Stok, Harga Satuan, Tanggal, Keterangan |

Jalankan bot dari folder utama proyek:

```powershell
python main.py
```

Invoice akan disimpan di `output/invoices/`. Nama usaha dan informasi kontak pada invoice dapat disesuaikan di `services/pdf_service.py`.

## Konfigurasi pribadi

File `.env`, kunci service account, virtual environment, cache Python, dan invoice hasil pemrosesan dikecualikan dari Git melalui `.gitignore`. Setiap instalasi memerlukan konfigurasi dan kredensialnya sendiri.
