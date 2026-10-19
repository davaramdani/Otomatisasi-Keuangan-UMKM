from telegram import Update
from telegram.ext import ContextTypes
from services.sheets_service import get_rekap

async def handle_rekap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    periode = "bulan"
    if args and args[0].lower() == "minggu":
        periode = "minggu"

    await update.message.reply_text("📊 Sedang menghitung rekap...")
    try:
        data = get_rekap(periode)
        label = "Bulan Ini" if periode == "bulan" else "7 Hari Terakhir"
        laba = data["laba_kotor"]
        laba_str = f"Rp {laba:,}" if laba >= 0 else f"-Rp {abs(laba):,}"

        await update.message.reply_text(
            f"📊 *Rekap {label}*\n\n"
            f"🛒 Pengeluaran Modal  : Rp {data['total_pengeluaran']:,}\n"
            f"   ({data['jumlah_transaksi_keluar']} transaksi)\n\n"
            f"💵 Total Penjualan   : Rp {data['total_penjualan']:,}\n"
            f"   ({data['jumlah_transaksi_masuk']} transaksi)\n\n"
            f"📈 Laba Kotor        : {laba_str}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal ambil rekap: {str(e)}")
