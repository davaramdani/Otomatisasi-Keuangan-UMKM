import os
from telegram import Update
from telegram.ext import ContextTypes
from services.gpt_service import parse_struk_gambar
from services.sheets_service import catat_pengeluaran
from services.stok_service import update_stok

async def handle_struk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("📸 Kirim foto struk belanja kamu!")
        return

    await update.message.reply_text("🔍 Sedang menganalisis struk...")

    photo      = update.message.photo[-1]
    file       = await context.bot.get_file(photo.file_id)
    os.makedirs("temp", exist_ok=True)
    image_path = f"temp/struk_{update.message.message_id}.jpg"
    await file.download_to_drive(image_path)

    try:
        hasil = parse_struk_gambar(image_path)
        items = hasil.get("items", [])
        toko  = hasil.get("toko", "Tidak terdeteksi")
        total = hasil.get("total", 0)

        if not items:
            await update.message.reply_text("⚠️ Tidak ada item terdeteksi di struk.")
            return

        stok_berhasil = []
        stok_gagal    = []

        for item in items:
            # ✅ Catat ke Pengeluaran — dilakukan di sini
            catat_pengeluaran(
                item["keterangan"],
                item["jumlah"],
                item.get("kategori", "Bahan Baku")
            )

            # ✅ Update Stok dengan harga asli + auto_catat=False
            # supaya tidak double catat ke Pengeluaran
            try:
                qty          = int(item.get("qty", 1))
                satuan       = item.get("satuan", "pcs")
                harga_satuan = int(item.get("harga_satuan", 0))  # ← harga asli dari struk
                status, nilai = update_stok(
                    nama       = item["keterangan"],
                    jumlah     = qty,
                    satuan     = satuan,
                    harga      = harga_satuan,   # ← harga tersimpan di stok
                    ket        = f"Dari struk {toko}",
                    auto_catat = False           # ← tidak double catat pengeluaran
                )
                stok_berhasil.append(
                    f"• {item['keterangan']} +{qty} {satuan} "
                    f"@ Rp {harga_satuan:,} (stok: {nilai})".replace(",",".")
                )
            except Exception as se:
                stok_gagal.append(f"• {item['keterangan']} — {se}")

        # Ringkasan pengeluaran
        detail = "\n".join([
            f"  • {i['keterangan']}: Rp {int(i['jumlah']):,}".replace(",",".")
            for i in items
        ])
        await update.message.reply_text(
            f"✅ *Struk berhasil diproses!*\n\n"
            f"🏪 Toko  : {toko}\n"
            f"📋 Item  :\n{detail}\n"
            f"💰 Total : Rp {int(total):,}\n\n"
            f"Semua item sudah dicatat ke Sheets 📊".replace(",","."),
            parse_mode="Markdown"
        )

        # Ringkasan stok
        stok_msg = "📦 *Update Stok:*\n"
        if stok_berhasil:
            stok_msg += "\n".join(stok_berhasil)
        if stok_gagal:
            stok_msg += "\n\n⚠️ *Gagal:*\n" + "\n".join(stok_gagal)
        await update.message.reply_text(stok_msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Gagal proses struk: {str(e)}")
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)