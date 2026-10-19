from telegram import Update
from telegram.ext import ContextTypes
from services.stok_service import get_semua_stok, update_stok, kurang_stok, get_sheet
from services.analitik_service import (
    get_pengeluaran_periode, get_penjualan_periode,
    get_stok_menipis, get_data_penjualan_lengkap,
    get_data_detail_penjualan, get_semua_pengeluaran
)
from handlers.invoice_handler import buat_invoice_data
from dotenv import load_dotenv
load_dotenv()
import os, json
from groq import Groq
from datetime import datetime

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"

def fmt(n):
    try: return "Rp {:,}".format(int(n)).replace(",",".")
    except: return "Rp 0"

def build_context():
    ctx = ""
    now = datetime.now()

    # === STOK ===
    try:
        stok = get_semua_stok()
        if stok:
            ctx += "DATA STOK SAAT INI:\n"
            for s in stok:
                ctx += f"- {s.get('Nama Barang')}: stok={s.get('Stok')} {s.get('Satuan')}, harga=Rp {s.get('Harga Satuan',0)}\n"
    except:
        ctx += "DATA STOK: tidak tersedia\n"

    # === RINGKASAN PENGELUARAN PERIODE ===
    try:
        rh, th = get_pengeluaran_periode("hari")
        rw, tw = get_pengeluaran_periode("minggu")
        rb, tb = get_pengeluaran_periode("bulan")
        ctx += f"\nRINGKASAN PENGELUARAN:\n"
        ctx += f"- Hari ini ({now.strftime('%d/%m/%Y')})  : Rp {th:,} ({len(rh)} transaksi)\n"
        ctx += f"- Minggu ini : Rp {tw:,} ({len(rw)} transaksi)\n"
        ctx += f"- Bulan ini  : Rp {tb:,} ({len(rb)} transaksi)\n"
    except:
        ctx += "DATA PENGELUARAN PERIODE: tidak tersedia\n"

    # === SEMUA HISTORI PENGELUARAN ===
    try:
        semua = get_semua_pengeluaran()
        if semua:
            per_bulan = {}
            for r in semua:
                tgl_str = str(r.get("Tanggal", ""))
                try:
                    bagian = tgl_str.split(" ")[0]
                    parts  = bagian.split("/")
                    key    = f"{parts[1]}/{parts[2]}"
                except:
                    key = "Lainnya"
                if key not in per_bulan:
                    per_bulan[key] = []
                per_bulan[key].append(r)

            ctx += "\nSEMUA HISTORI PENGELUARAN (Tanggal | Keterangan | Jumlah | Kategori):\n"
            for bulan_key in sorted(per_bulan.keys()):
                total_bln = 0
                for r in per_bulan[bulan_key]:
                    try:
                        total_bln += int(str(r.get("Jumlah", 0)).replace(".", "").replace(",", ""))
                    except:
                        pass
                ctx += f"\n[Bulan {bulan_key}] Total: Rp {total_bln:,}\n".replace(",",".")
                for r in per_bulan[bulan_key]:
                    ctx += (
                        f"  - {r.get('Tanggal','-')} | "
                        f"{r.get('Keterangan','-')} | "
                        f"Rp {r.get('Jumlah',0)} | "
                        f"{r.get('Kategori','-')}\n"
                    )
    except:
        ctx += "HISTORI PENGELUARAN: tidak tersedia\n"

    # === PENJUALAN + CUSTOMER ===
    try:
        semua_jual = get_data_penjualan_lengkap()
        _, tm = get_penjualan_periode("bulan")
        ctx += f"\nPENJUALAN BULAN INI: Rp {tm:,} ({len(semua_jual)} transaksi total)\n"
        if semua_jual:
            ctx += "\nDATA CUSTOMER (Tanggal | Invoice | Pembeli | Total | Status):\n"
            for r in semua_jual:
                ctx += (
                    f"  - {r.get('Tanggal','-')} | "
                    f"{r.get('Invoice No','-')} | "
                    f"{r.get('Pembeli','-')} | "
                    f"Rp {r.get('Total',0)} | "
                    f"{r.get('Status','-')}\n"
                )
    except:
        ctx += "DATA PENJUALAN: tidak tersedia\n"

    # === DETAIL PRODUK + FREKUENSI ===
    try:
        detail_jual = get_data_detail_penjualan()
        if detail_jual:
            freq      = {}
            qty_total = {}
            for d in detail_jual:
                item            = d.get('Item', '-')
                qty             = int(d.get('Qty', 1))
                freq[item]      = freq.get(item, 0) + 1
                qty_total[item] = qty_total.get(item, 0) + qty
            sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
            ctx += "\nPRODUK PALING SERING DIBELI:\n"
            for item, count in sorted_freq:
                ctx += f"  - {item}: {count}x dipesan, total {qty_total[item]} pcs\n"
            ctx += "\nDETAIL TRANSAKSI PRODUK (Invoice | Item | Qty | Harga | Subtotal):\n"
            for d in detail_jual:
                ctx += (
                    f"  - {d.get('Invoice No','-')} | "
                    f"{d.get('Item','-')} | "
                    f"{d.get('Qty',0)}x | "
                    f"Rp {d.get('Harga Satuan',0)} | "
                    f"Rp {d.get('Subtotal',0)}\n"
                )
    except:
        pass

    # === STOK MENIPIS ===
    try:
        menipis = get_stok_menipis(5)
        if menipis:
            ctx += "\nSTOK HAMPIR HABIS: " + ", ".join([r.get("Nama Barang","?") for r in menipis]) + "\n"
    except:
        pass

    return ctx

def hitung_modal(pemakaian_list):
    try:
        stok      = get_semua_stok()
        stok_dict = {s["Nama Barang"].lower(): s for s in stok}
        total_modal = 0
        detail      = []
        for item in pemakaian_list:
            nama   = item["nama"].lower()
            jumlah = item["jumlah"]
            if nama in stok_dict:
                harga      = int(stok_dict[nama].get("Harga Satuan", 0))
                modal_item = harga * jumlah
                total_modal += modal_item
                detail.append({
                    "nama": stok_dict[nama]["Nama Barang"],
                    "jumlah": jumlah,
                    "harga_satuan": harga,
                    "modal": modal_item
                })
            else:
                detail.append({
                    "nama": item["nama"],
                    "jumlah": jumlah,
                    "harga_satuan": 0,
                    "modal": 0,
                    "note": "tidak ditemukan"
                })
        return total_modal, detail
    except:
        return 0, []

async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pesan = update.message.text.strip()
    if not pesan:
        return

    await update.message.reply_text("🤔 Sedang berpikir...")
    data_context = build_context()
    now          = datetime.now().strftime("%d %B %Y %H:%M")

    system_prompt = f"""Kamu adalah asisten bisnis pintar untuk toko dessert bernama Zee Zee Dessert.
Kamu punya akses ke data bisnis real-time berikut:

{data_context}

Tanggal & waktu sekarang: {now}

TUGAS KAMU:
1. Jawab pertanyaan tentang stok, pengeluaran, penjualan, customer, dan produk terlaris
2. Untuk pengeluaran tanggal/bulan tertentu: cari di SEMUA HISTORI PENGELUARAN

3. Jika user ingin CATAT atau TAMBAH STOK, kembalikan tag berikut PERSIS:
[STOKIN]
{{"nama": "susu", "jumlah": 3, "satuan": "liter", "harga": 15000}}
[/STOKIN]

4. Jika user sebut PEMAKAIAN bahan + pendapatan, kembalikan tag berikut PERSIS:
[LABA]
{{"pemakaian": [{{"nama": "susu", "jumlah": 3}}], "pendapatan": 1000000}}
[/LABA]

5. Jika user ingin CATAT PENGELUARAN (gas, listrik, dll), kembalikan tag berikut PERSIS:
[KELUAR]
{{"keterangan": "beli gas", "kategori": "Operasional", "jumlah": 25000}}
[/KELUAR]

6. Jika user ingin BUAT INVOICE atau NOTA atau TAGIHAN atau sebut kata "atas nama", kembalikan tag berikut PERSIS:
[INVOICE]
{{"pembeli": "nama customer", "items": [{{"nama": "salad buah", "qty": 2, "harga": 20000}}], "ongkir": 0}}
[/INVOICE]
Catatan: harga adalah harga per satuan item, ongkir=0 jika tidak disebutkan, qty dan harga wajib integer

7. Gunakan Bahasa Indonesia yang natural dan ramah
8. JANGAN gunakan format Markdown seperti *, _, dalam jawabanmu, tulis polos saja
9. PENTING: Tulis tag [STOKIN], [LABA], [KELUAR], [INVOICE] PERSIS seperti contoh, jangan diubah"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": pesan}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        jawaban = response.choices[0].message.content

        # ============================================================
        # CATAT STOK
        # ============================================================
        if "[STOKIN]" in jawaban and "[/STOKIN]" in jawaban:
            teks_bersih = jawaban.split("[STOKIN]")[0].strip()
            json_str    = jawaban.split("[STOKIN]")[1].split("[/STOKIN]")[0].strip()
            try:
                d      = json.loads(json_str)
                nama   = d.get("nama", "")
                jumlah = int(d.get("jumlah", 0))
                satuan = d.get("satuan", "pcs")
                harga  = int(d.get("harga", 0))
                status, nilai = update_stok(nama, jumlah, satuan, harga)
                aksi = "diperbarui, sekarang" if status == "update" else "ditambahkan! Total"
                if teks_bersih:
                    await update.message.reply_text(teks_bersih)
                bot_msg = f"✅ Stok {nama} berhasil {aksi}: {nilai} {satuan}"
                if harga > 0:
                    bot_msg += f"\n📋 Pengeluaran {fmt(jumlah * harga)} otomatis tercatat di sheet!"
                await update.message.reply_text(bot_msg)
            except Exception as e:
                if teks_bersih:
                    await update.message.reply_text(teks_bersih)
                await update.message.reply_text(f"⚠️ Gagal catat stok: {e}")
            return

        # ============================================================
        # HITUNG LABA + KURANGI STOK
        # ============================================================
        if "[LABA]" in jawaban and "[/LABA]" in jawaban:
            teks_bersih = jawaban.split("[LABA]")[0].strip()
            json_str    = jawaban.split("[LABA]")[1].split("[/LABA]")[0].strip()
            try:
                d          = json.loads(json_str)
                pemakaian  = d.get("pemakaian", [])
                pendapatan = int(d.get("pendapatan", 0))
                total_modal, detail = hitung_modal(pemakaian)
                laba   = pendapatan - total_modal
                margin = (laba / pendapatan * 100) if pendapatan > 0 else 0

                if teks_bersih:
                    await update.message.reply_text(teks_bersih)

                bot_msg = "📊 Rincian Kalkulasi:\n\nModal Bahan:\n"
                for dt in detail:
                    if dt.get("note"):
                        bot_msg += f"• {dt['nama']} x{dt['jumlah']} — harga tidak diketahui\n"
                    else:
                        bot_msg += f"• {dt['nama']} x{dt['jumlah']} @ {fmt(dt['harga_satuan'])} = {fmt(dt['modal'])}\n"
                bot_msg += f"\nPendapatan  : {fmt(pendapatan)}\n"
                bot_msg += f"Total Modal : {fmt(total_modal)}\n"
                bot_msg += f"Laba Kotor  : {fmt(laba)}\n"
                bot_msg += f"Margin      : {margin:.1f}%\n"
                if laba > 0:
                    bot_msg += "\n🎉 Hari yang menguntungkan!"
                elif laba == 0:
                    bot_msg += "\n⚠️ Hari ini impas."
                else:
                    bot_msg += "\n🚨 Hari ini merugi!"
                await update.message.reply_text(bot_msg)

                stok_update = []
                stok_gagal  = []
                for item in pemakaian:
                    nama   = item["nama"]
                    jumlah = item["jumlah"]
                    status, nilai = kurang_stok(nama, jumlah)
                    if status == "ok":
                        stok_update.append(f"• {nama} -{jumlah} (sisa: {nilai})")
                    elif status == "kurang":
                        stok_update.append(f"• {nama} stok tidak cukup (ada: {nilai})")
                    else:
                        stok_gagal.append(f"• {nama} tidak ditemukan")

                stok_msg = "📦 Update Stok Pemakaian:\n"
                if stok_update:
                    stok_msg += "\n".join(stok_update)
                if stok_gagal:
                    stok_msg += "\n\nTidak ditemukan:\n" + "\n".join(stok_gagal)
                await update.message.reply_text(stok_msg)

            except Exception as e:
                if teks_bersih:
                    await update.message.reply_text(teks_bersih)
                await update.message.reply_text(f"⚠️ Gagal hitung laba: {e}")
            return

        # ============================================================
        # CATAT PENGELUARAN MANUAL
        # ============================================================
        if "[KELUAR]" in jawaban and "[/KELUAR]" in jawaban:
            teks_bersih = jawaban.split("[KELUAR]")[0].strip()
            json_str    = jawaban.split("[KELUAR]")[1].split("[/KELUAR]")[0].strip()
            try:
                d   = json.loads(json_str)
                ket = d.get("keterangan", "")
                kat = d.get("kategori", "Lain-lain")
                jml = int(d.get("jumlah", 0))
                tgl = datetime.now().strftime("%d/%m/%Y %H:%M")
                get_sheet().worksheet("Pengeluaran").append_row([tgl, ket, jml, kat, "Bot"])
                if teks_bersih:
                    await update.message.reply_text(teks_bersih)
                await update.message.reply_text(
                    f"✅ Pengeluaran dicatat!\n📋 {ket}: {fmt(jml)} [{kat}]"
                )
            except Exception as e:
                if teks_bersih:
                    await update.message.reply_text(teks_bersih)
                await update.message.reply_text(f"⚠️ Gagal catat pengeluaran: {e}")
            return

        # ============================================================
        # BUAT INVOICE via NLP
        # ============================================================
        if "[INVOICE]" in jawaban and "[/INVOICE]" in jawaban:
            teks_bersih = jawaban.split("[INVOICE]")[0].strip()
            json_str    = jawaban.split("[INVOICE]")[1].split("[/INVOICE]")[0].strip()
            try:
                d = json.loads(json_str)
                if teks_bersih:
                    await update.message.reply_text(teks_bersih)
                await update.message.reply_text("📄 Membuat invoice...")
                await buat_invoice_data(update, context, d)
            except Exception as e:
                if teks_bersih:
                    await update.message.reply_text(teks_bersih)
                await update.message.reply_text(f"⚠️ Gagal buat invoice: {e}")
            return

        # ============================================================
        # FALLBACK — jawaban biasa
        # ============================================================
        await update.message.reply_text(jawaban)

    except Exception as e:
        await update.message.reply_text("❌ Gagal memproses: " + str(e))