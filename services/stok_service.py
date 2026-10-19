from dotenv import load_dotenv
load_dotenv()
import gspread, os, time
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

def get_sheet():
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(os.getenv('SPREADSHEET_ID'))

def catat_pengeluaran_otomatis(nama, jumlah, harga, tgl):
    """Kolom sheet: Tanggal | Keterangan | Jumlah | Kategori | Sumber"""
    try:
        total = int(jumlah) * int(harga)
        if total <= 0: return
        ws = get_sheet().worksheet('Pengeluaran')
        ws.append_row([tgl, f'Beli {nama} {jumlah}x @{harga}', total, 'Bahan Baku', 'Bot'])
    except Exception as e:
        print(f'[WARN] Gagal catat pengeluaran otomatis: {e}')

def get_semua_stok():
    return get_sheet().worksheet('Stok').get_all_records()

def update_stok(nama, jumlah, satuan, harga, ket='', auto_catat=True):
    """
    auto_catat=True  → otomatis catat ke Pengeluaran (default, untuk chat/manual)
    auto_catat=False → TIDAK catat ke Pengeluaran (untuk struk, sudah dicatat sendiri)
    """
    ws      = get_sheet().worksheet('Stok')
    records = ws.get_all_records()
    tgl     = datetime.now().strftime('%d/%m/%Y %H:%M')
    for i, r in enumerate(records):
        if r['Nama Barang'].lower() == nama.lower():
            stok_baru = int(r['Stok']) + int(jumlah)
            ws.update_cell(i+2, 3, stok_baru)
            if int(harga) > 0:
                ws.update_cell(i+2, 4, harga)   # ← harga tetap tersimpan
            ws.update_cell(i+2, 5, tgl)
            if int(harga) > 0 and auto_catat:    # ← hanya catat jika auto_catat=True
                catat_pengeluaran_otomatis(nama, jumlah, harga, tgl)
            time.sleep(0.5)
            return 'update', stok_baru
    ws.append_row([nama, satuan, jumlah, harga, tgl, ket])
    if int(harga) > 0 and auto_catat:             # ← hanya catat jika auto_catat=True
        catat_pengeluaran_otomatis(nama, jumlah, harga, tgl)
    time.sleep(0.5)
    return 'tambah', int(jumlah)

def kurang_stok(nama, jumlah):
    ws      = get_sheet().worksheet('Stok')
    records = ws.get_all_records()
    for i, r in enumerate(records):
        if r['Nama Barang'].lower() == nama.lower():
            stok = int(r['Stok'])
            if stok < int(jumlah): return 'kurang', stok
            stok_baru = stok - int(jumlah)
            ws.update_cell(i+2, 3, stok_baru)
            return 'ok', stok_baru
    return 'tidak_ada', 0