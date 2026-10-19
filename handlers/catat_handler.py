from telegram import Update
from telegram.ext import ContextTypes
from services.gpt_service import parse_perintah_catat
from services.sheets_service import catat_pengeluaran

async def handle_catat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = update.message.text.replace("/catat", "").strip()
    if not teks:
        await update.message.reply_text("Contoh: /catat belanja susu 50 ribu")
        return
    await update.message.reply_text("Sedang memproses...")
    try:
        data = parse_perintah_catat(teks)
        catat_pengeluaran(data["keterangan"], data["jumlah"], data.get("kategori", "Bahan Baku"))
        jumlah = int(data["jumlah"])
        await update.message.reply_text(
            "Berhasil dicatat!\n\n"
            + "Keterangan: " + str(data["keterangan"]) + "\n"
            + "Jumlah    : Rp " + f"{jumlah:,}".replace(",",".") + "\n"
            + "Kategori  : " + str(data.get("kategori","Bahan Baku")) + "\n\n"
            + "Sudah masuk ke Google Sheets!"
        )
    except Exception as e:
        await update.message.reply_text("Gagal: " + str(e))