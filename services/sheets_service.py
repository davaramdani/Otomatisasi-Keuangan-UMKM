import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(os.getenv("SPREADSHEET_ID"))
    return spreadsheet

def catat_pengeluaran(keterangan, jumlah, kategori="Bahan Baku"):
    spreadsheet = get_sheet()
    ws = spreadsheet.worksheet("Pengeluaran")
    tanggal = datetime.now().strftime("%d/%m/%Y %H:%M")
    ws.append_row([tanggal, keterangan, jumlah, kategori, "Manual"])
    return True

def catat_penjualan(invoice_no, pembeli, total):
    spreadsheet = get_sheet()
    ws = spreadsheet.worksheet("Penjualan")
    tanggal = datetime.now().strftime("%d/%m/%Y %H:%M")
    ws.append_row([tanggal, invoice_no, pembeli, total, "Lunas"])
    return True

def catat_detail_penjualan(invoice_no, items):
    # items = list of dict: {"nama": ..., "qty": ..., "harga": ...}
    spreadsheet = get_sheet()
    ws = spreadsheet.worksheet("Detail Penjualan")
    for item in items:
        subtotal = item["qty"] * item["harga"]
        ws.append_row([invoice_no, item["nama"], item["qty"], item["harga"], subtotal])

def get_rekap(periode="bulan"):
    from datetime import datetime
    spreadsheet = get_sheet()
    ws_keluar = spreadsheet.worksheet("Pengeluaran")
    ws_jual   = spreadsheet.worksheet("Penjualan")

    now = datetime.now()
    records_keluar = ws_keluar.get_all_records()
    records_jual   = ws_jual.get_all_records()

    def filter_periode(records, key_tanggal):
        hasil = []
        for r in records:
            try:
                tgl = datetime.strptime(r[key_tanggal], "%d/%m/%Y %H:%M")
                if periode == "bulan" and tgl.month == now.month and tgl.year == now.year:
                    hasil.append(r)
                elif periode == "minggu":
                    selisih = (now - tgl).days
                    if selisih <= 7:
                        hasil.append(r)
            except:
                pass
        return hasil

    pengeluaran = filter_periode(records_keluar, "Tanggal")
    penjualan   = filter_periode(records_jual, "Tanggal")

    total_keluar = sum(int(str(r["Jumlah"]).replace(".","").replace(",","")) for r in pengeluaran)
    total_masuk  = sum(int(str(r["Total"]).replace(".","").replace(",","")) for r in penjualan)

    return {
        "periode": periode,
        "total_pengeluaran": total_keluar,
        "total_penjualan": total_masuk,
        "jumlah_transaksi_keluar": len(pengeluaran),
        "jumlah_transaksi_masuk": len(penjualan),
        "laba_kotor": total_masuk - total_keluar
    }
