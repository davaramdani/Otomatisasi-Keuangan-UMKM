from dotenv import load_dotenv
load_dotenv()
from services.stok_service import get_sheet
from datetime import datetime, timedelta


def parse_tanggal(tgl_str):
    for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(tgl_str).strip(), fmt)
        except:
            continue
    return None


def get_pengeluaran_periode(periode="hari"):
    ws      = get_sheet().worksheet("Pengeluaran")
    records = ws.get_all_records()
    now     = datetime.now()

    if periode == "hari":
        batas = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periode == "minggu":
        batas = now - timedelta(days=now.weekday())
        batas = batas.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periode == "bulan":
        batas = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        batas = now.replace(hour=0, minute=0, second=0, microsecond=0)

    hasil = []
    total = 0
    for r in records:
        tgl = parse_tanggal(r.get("Tanggal", ""))
        if tgl and tgl >= batas:
            hasil.append(r)
            try:
                total += int(str(r.get("Jumlah", 0)).replace(".", "").replace(",", ""))
            except:
                pass
    return hasil, total


def get_penjualan_periode(periode="bulan"):
    try:
        ws      = get_sheet().worksheet("Penjualan")
        records = ws.get_all_records()
        now     = datetime.now()

        if periode == "hari":
            batas = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periode == "minggu":
            batas = now - timedelta(days=now.weekday())
            batas = batas.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periode == "bulan":
            batas = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            batas = now.replace(hour=0, minute=0, second=0, microsecond=0)

        hasil = []
        total = 0
        for r in records:
            tgl = parse_tanggal(r.get("Tanggal", ""))
            if tgl and tgl >= batas:
                hasil.append(r)
                try:
                    total += int(str(r.get("Total", 0)).replace(".", "").replace(",", ""))
                except:
                    pass
        return hasil, total
    except:
        return [], 0


def get_stok_menipis(batas=5):
    try:
        ws      = get_sheet().worksheet("Stok")
        records = ws.get_all_records()
        return [r for r in records if int(r.get("Stok", 0)) <= batas]
    except:
        return []


def get_data_penjualan_lengkap():
    """Kolom: Tanggal | Invoice No | Pembeli | Total | Status"""
    try:
        return get_sheet().worksheet("Penjualan").get_all_records()
    except:
        return []


def get_data_detail_penjualan():
    """Kolom: Invoice No | Item | Qty | Harga Satuan | Subtotal"""
    try:
        return get_sheet().worksheet("Detail Penjualan").get_all_records()
    except:
        return []


# ← Sekarang di luar, tidak di dalam fungsi lain
def get_semua_pengeluaran():
    """Ambil SEMUA data pengeluaran tanpa filter tanggal."""
    try:
        return get_sheet().worksheet("Pengeluaran").get_all_records()
    except:
        return []


def get_pengeluaran_by_bulan(bulan, tahun):
    """Ambil pengeluaran berdasarkan bulan & tahun tertentu."""
    try:
        records = get_sheet().worksheet("Pengeluaran").get_all_records()
        hasil   = []
        total   = 0
        for r in records:
            tgl = parse_tanggal(r.get("Tanggal", ""))
            if tgl and tgl.month == bulan and tgl.year == tahun:
                hasil.append(r)
                try:
                    total += int(str(r.get("Jumlah", 0)).replace(".", "").replace(",", ""))
                except:
                    pass
        return hasil, total
    except:
        return [], 0


def get_pengeluaran_by_tanggal(tgl_str):
    """Ambil pengeluaran berdasarkan tanggal tertentu. tgl_str = '28/03/2026'"""
    try:
        records = get_sheet().worksheet("Pengeluaran").get_all_records()
        hasil   = []
        total   = 0
        for r in records:
            tgl_data = str(r.get("Tanggal", ""))
            if tgl_data.startswith(tgl_str):
                hasil.append(r)
                try:
                    total += int(str(r.get("Jumlah", 0)).replace(".", "").replace(",", ""))
                except:
                    pass
        return hasil, total
    except:
        return [], 0