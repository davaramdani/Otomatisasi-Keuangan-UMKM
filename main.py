import os
from dotenv import load_dotenv
load_dotenv()
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers.catat_handler   import handle_catat
from handlers.struk_handler   import handle_struk
from handlers.rekap_handler   import handle_rekap
from handlers.invoice_handler import handle_invoice
from handlers.stok_handler    import handle_stok
from handlers.chat_handler    import handle_chat

async def start(update: Update, context):
    await update.message.reply_text(
        "🍓 *Bot Zee Zee Dessert*\n\n"
        "/catat — Catat pengeluaran\n"
        "/stok — Kelola stok barang\n"
        "/invoice — Buat invoice PDF\n"
        "/rekap — Rekap pengeluaran",
        parse_mode="Markdown"
    )

def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("catat",   handle_catat))
    app.add_handler(CommandHandler("rekap",   handle_rekap))
    app.add_handler(CommandHandler("invoice", handle_invoice))
    app.add_handler(CommandHandler("stok",    handle_stok))
    app.add_handler(MessageHandler(filters.PHOTO, handle_struk))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chat))

    print("🤖 Bot Zee Zee Dessert berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()