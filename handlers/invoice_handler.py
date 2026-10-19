from telegram import Update
from telegram.ext import ContextTypes
from services.pdf_service  import generate_invoice   # ← nama fungsi yang benar
from services.stok_service import get_sheet
from datetime import datetime


async def buat_invoice_data(update: Update, context: ContextTypes.DEFAULT_TYPE, data: dict):
    pembeli = data.get("pembeli", "Customer")
    items   = data.get("items", [])
    ongkir  = int(data.get("ongkir", 0))

    if not items:
        await update.message.reply_text("⚠️ Tidak ada item yang disebutkan.")
        return

    subtotal = sum(int(i.get("qty", 1)) * int(i.get("harga", 0)) for i in items)
    total    = subtotal + ongkir
    tgl      = datetime.now().strftime("%d/%m/%Y %H:%M")
    inv_no   = "INV-" + datetime.now().strftime("%Y%m-%d%H%M")

    # ✅ Sesuaikan format dict dengan yang diminta generate_invoice
    pdf_data = {
        "invoice_no": inv_no,
        "pembeli": pembeli,
        "items": [
            {
                "nama":  i.get("nama", ""),
                "qty":   int(i.get("qty", 1)),
                "harga": int(i.get("harga", 0))
            }
            for i in items
        ],
        "ongkir": ongkir
    }

    # Generate PDF
    pdf_path = generate_invoice(pdf_data)

    # Catat ke sheet
    try:
        ws_jual = get_sheet().worksheet("Penjualan")
        ws_jual.append_row([tgl, inv_no, pembeli, total, "Lunas"])

        ws_detail = get_sheet().worksheet("Detail Penjualan")
        for item in items:
            nama  = item.get("nama", "")
            qty   = int(item.get("qty", 1))
            harga = int(item.get("harga", 0))
            ws_detail.append_row([inv_no, nama, qty, harga, qty * harga])
    except Exception as e:
        await update.message.reply_text(f"⚠️ Invoice dibuat tapi gagal catat sheet: {e}")

    # Kirim PDF
    with open(pdf_path, "rb") as f:
        await update.message.reply_document(
            document=f,
            filename=f"Invoice_{pembeli}_{inv_no}.pdf",
            caption=(
                f"✅ *Invoice berhasil dibuat!*\n\n"
                f"📋 No     : {inv_no}\n"
                f"👤 Pembeli: {pembeli}\n"
                f"💰 Total  : Rp {total:,}".replace(",",".")
            ),
            parse_mode="Markdown"
        )


async def handle_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from services.gpt_service import parse_perintah_invoice
    args = " ".join(context.args) if context.args else ""
    if not args:
        await update.message.reply_text(
            "📋 Contoh perintah:\n"
            "/invoice atas nama Dava, 2 salad buah 40rb, ongkir 18rb"
        )
        return
    try:
        data = parse_perintah_invoice(args)
        await buat_invoice_data(update, context, data)
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal buat invoice: {e}")