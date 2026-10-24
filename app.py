import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Data Science & Process AI Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Data Science & Process AI Assistant")
st.caption("Chatbot interaktif berbasis Gemini API untuk analisis data, query SQL, dan optimasi proses bisnis.")

# ==========================================
# 2. SIDEBAR: PARAMETER KREATIF & API KEY
# ==========================================
st.sidebar.header("⚙️ Konfigurasi Chatbot")

# Input API Key secara dinamis
api_key = st.sidebar.text_input(
    "Gemini API Key:",
    type="password",
    help="Dapatkan API key gratis di Google AI Studio (aistudio.google.com)"
)

# Parameter Kreatif 1: Dynamic Persona (Gaya Bahasa)
gaya_bahasa = st.sidebar.selectbox(
    "Gaya Bahasa Respon:",
    ["Formal & Analitis", "Santai & Edukatif", "Ringkas & Direct (Point-to-Point)"]
)

# Parameter Kreatif 2: Temperature Slider
temperature = st.sidebar.slider(
    "Temperature (Kreativitas):",
    min_value=0.0,
    max_value=2.0,
    value=0.5,
    step=0.1,
    help="Skor rendah (0.0) untuk jawaban deterministik/pasti; Skor tinggi (>1.0) untuk jawaban lebih kreatif."
)

# Parameter Kreatif 3: Max Output Tokens
max_tokens = st.sidebar.slider(
    "Max Tokens:",
    min_value=100,
    max_value=2048,
    value=800,
    step=100,
    help="Membatasi panjang kata/token dalam satu respon."
)

# Fitur Tambahan: Tombol Reset Percakapan
if st.sidebar.button("🧹 Hapus Riwayat Chat"):
    st.session_state.messages = []
    st.rerun()

# ==========================================
# 3. MEMORI PERCAKAPAN (SESSION STATE)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan seluruh riwayat percakapan yang tersimpan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# System Instruction berdasarkan pilihan gaya bahasa
system_instruction = f"""
Anda adalah AI Assistant profesional spesialis Data Science, Business Process Improvement, dan SQL.
Instruksi gaya komunikasi:
- Adopsi gaya bahasa: {gaya_bahasa}.
- Berikan struktur jawaban yang rapi menggunakan poin-poin atau blok kode Python/SQL jika relevan.
- Bantu jawab pertanyaan pengguna secara rinci dan terstruktur.
"""

# ==========================================
# 4. PEMROSESAN CHAT & GEMINI API INTEGRATION
# ==========================================
if prompt := st.chat_input("Tanyakan sesuatu (misal: 'Buatkan query SQL window function' atau 'Apa itu VSM?')..."):
    
    if not api_key:
        st.error("⚠️ Masukkan Gemini API Key terlebih dahulu pada panel Sidebar di sebelah kiri!")
    else:
        # Simpan dan tampilkan input pengguna
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Konfigurasi Gemini API
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel(
                model_name="gemini-3.6-flash",
                system_instruction=system_instruction,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )

            # Format histori percakapan sesuai struktur Gemini API
            formatted_history = []
            for msg in st.session_state.messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                formatted_history.append({"role": role, "parts": [msg["content"]]})

            chat = model.start_chat(history=formatted_history)

            # Kirim pesan dan tampilkan respon bot
            with st.chat_message("assistant"):
                with st.spinner("Sedang memproses..."):
                    response = chat.send_message(prompt)
                    st.markdown(response.text)

            # Simpan respon bot ke session state
            st.session_state.messages.append({"role": "assistant", "content": response.text})

        except Exception as e:
            st.error(f"Gagal memproses respon API: {str(e)}")