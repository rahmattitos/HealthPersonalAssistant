%%writefile app.py
import os
import streamlit as st
from google import genai
from google.genai import types

# 1. Konfigurasi Sistem (System Instruction / Parameter Kreatif)
SYSTEM_INSTRUCTION = """
Kamu adalah HealthBuddy, seorang Personal Assistant di bidang kesehatan dan gaya hidup sehat.

Aturan Utama:
1. Domain: Hanya fokus memberikan saran gaya hidup sehat, nutrisi, hidrasi, olahraga ringan, manajemen stres, dan pola tidur.
2. Gaya Bahasa: Gunakan bahasa Indonesia yang santai, ramah, akrab, dan mudah dipahami (seperti mengobrol dengan teman). Gunakan kata sapaan seperti 'kamu', 'yuk', 'nih', dan 'sip'.
3. Edukatif & Aman: Berikan saran praktis dan terukur. Selalu sertakan catatan ramah bahwa kamu adalah asisten AI dan bukan pengganti konsultasi medis dokter spesialis jika pengguna menanyakan penyakit berat.
"""

# 2. Setup Halaman Streamlit
st.set_page_config(
    page_title="HealthBuddy AI - Asisten Kesehatan",
    page_icon="🩺",
    layout="centered"
)

st.title("🩺 HealthBuddy AI")
st.caption("Asisten pribadi gaya hidup sehat dengan penyampaian santai dan informatif.")

# 3. Setup API Key di Sidebar
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Masukkan Gemini API Key:", type="password")

if not api_key:
    st.warning("Silakan masukkan Gemini API Key di sidebar sebelah kiri untuk memulai.", icon="🔑")
    st.stop()

# Inisialisasi Client Gemini
client = genai.Client(api_key=api_key)

# 4. Menyimpan Riwayat Chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "model",
            "content": "Halo! Aku HealthBuddy 🩺. Mau diskusi soal pola makan, tips olahraga ringan, atau manajemen tidur hari ini?"
        }
    ]

# 5. Menampilkan Riwayat Chat Sebelumnya
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "model" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 6. Input Pesan Pengguna & Logika Gemini
if user_input := st.chat_input("Tanyakan sesuatu seputar kesehatan..."):
    # Tampilkan pesan user ke layar & simpan ke riwayat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Siapkan format pesan untuk API Gemini
    contents = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=m["content"])]
        )
    )

    # Proses balasan dari Gemini
    with st.chat_message("model", avatar="🤖"):
        with st.spinner("Mikirin saran terbaik buat kamu..."):
            try:
                # Menggunakan model gemini-3.5-flash-lite sesuai permintaan
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7
                    )
                )
                
                # Tampilkan dan simpan balasan
                st.markdown(response.text)
                st.session_state.messages.append({"role": "model", "content": response.text})
                
            except Exception as e:
                st.error(f"Terjadi kendala koneksi: {e}")
