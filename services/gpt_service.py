from dotenv import load_dotenv
load_dotenv()
from groq import Groq
import os, json, re, base64

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL        = "llama-3.3-70b-versatile"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

def extract_json(text):
    if not text or not text.strip():
        raise ValueError("Response kosong dari AI")
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"{[\s\S]*}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    raise ValueError("Gagal parse JSON: " + text[:200])

def parse_perintah_catat(teks):
    sys_msg = (
        "Balas HANYA JSON. "
        "Format: {\"keterangan\": \"susu\", \"jumlah\": 50000, \"kategori\": \"Bahan Baku\"}. "
        "Kategori: Bahan Baku/Operasional/Peralatan/Lain-lain. Jumlah integer."
    )
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": sys_msg},
            {"role": "user",   "content": teks}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    return extract_json(r.choices[0].message.content)

def parse_perintah_invoice(teks):
    sys_msg = (
        "Balas HANYA JSON. "
        "Format: {\"pembeli\": \"nama\", \"items\": [{\"nama\": \"salad buah\", \"qty\": 2, \"harga\": 20000}], \"ongkir\": 18000}. "
        "Harga per satuan, semua integer."
    )
    r = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": sys_msg},
            {"role": "user",   "content": teks}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    return extract_json(r.choices[0].message.content)

def parse_struk_gambar(image_path):
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode("utf-8")
    r = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64," + img}
                },
                {
                    "type": "text",
                    "text": (
                        "Scan struk belanja ini. Balas HANYA JSON format berikut:\n"
                        "{\n"
                        "  \"toko\": \"nama toko\",\n"
                        "  \"items\": [\n"
                        "    {\n"
                        "      \"keterangan\": \"nama item\",\n"
                        "      \"jumlah\": 15000,\n"
                        "      \"kategori\": \"Bahan Baku\",\n"
                        "      \"qty\": 1,\n"
                        "      \"satuan\": \"pcs\",\n"
                        "      \"harga_satuan\": 15000\n"
                        "    }\n"
                        "  ],\n"
                        "  \"total\": 50000\n"
                        "}\n"
                        "Aturan:\n"
                        "- jumlah = qty x harga_satuan\n"
                        "- kategori selalu Bahan Baku untuk bahan makanan\n"
                        "- qty isi 1 jika tidak jelas\n"
                        "- satuan isi pcs jika tidak jelas\n"
                        "- Jangan tambahkan teks selain JSON"
                    )
                }
            ]
        }],
        temperature=0
    )
    return extract_json(r.choices[0].message.content)