from telegram import Update
from telegram.ext import ContextTypes
from services.stok_service import update_stok, kurang_stok

async def handle_stok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks = update.message.text.replace('/stok','').strip()
    if not teks:
        await update.message.reply_text(
            '📦 *Perintah Stok:*\n\n'
            'Tambah: `/stok tambah susu 10 liter 15000`\n'
            'Kurang: `/stok kurang susu 2`',
            parse_mode='Markdown'
        )
        return
    await update.message.reply_text('⏳ Memproses stok...')
    try:
        parts = teks.split()
        aksi = parts[0].lower()
        if aksi == 'tambah' and len(parts) >= 3:
            nama = parts[1]; jumlah = int(parts[2])
            satuan = parts[3] if len(parts)>3 else 'pcs'
            harga = int(parts[4]) if len(parts)>4 else 0
            status, nilai = update_stok(nama, jumlah, satuan, harga)
            pesan = ('✅ Stok *'+nama+'* diperbarui! Sekarang: *'+str(nilai)+' '+satuan+'*') if status=='update' else ('✅ *'+nama+'* ditambahkan! Jumlah: *'+str(nilai)+' '+satuan+'*')
            await update.message.reply_text(pesan, parse_mode='Markdown')
        elif aksi == 'kurang' and len(parts) >= 3:
            nama = parts[1]; jumlah = int(parts[2])
            status, nilai = kurang_stok(nama, jumlah)
            if status=='ok': await update.message.reply_text('✅ Sisa stok *'+nama+'*: *'+str(nilai)+'*', parse_mode='Markdown')
            elif status=='kurang': await update.message.reply_text('⚠️ Stok *'+nama+'* tidak cukup! Tersedia: *'+str(nilai)+'*', parse_mode='Markdown')
            else: await update.message.reply_text('❌ Barang *'+nama+'* tidak ditemukan.', parse_mode='Markdown')
        else:
            await update.message.reply_text('❌ Format salah. Contoh: `/stok tambah susu 10 liter 15000`', parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text('❌ Gagal: '+str(e))
