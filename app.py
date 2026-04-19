import streamlit as st
import pandas as pd
from datetime import datetime

# PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

# ========================
# CONFIG
# ========================
st.set_page_config(page_title="Klasifikasi ABK", layout="wide")

# ========================
# STYLE
# ========================
st.markdown("""
<style>
.main-title {
    font-size: 32px;
    font-weight: bold;
    color: #1f4e79;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ========================
# STRATEGI AKADEMIK
# ========================
strategi = {
    "RENDAH": """
🔴 Strategi Akademik:
Memberikan pendampingan lebih intensif pada kelompok rendah, seperti perhatian lebih dan pendekatan personal dari guru.

📘 Strategi Berdasarkan Gaya Belajar:

🎨 Visual:
Gunakan gambar, video, warna, diagram, dan mind mapping agar materi lebih mudah dipahami.

🎧 Auditori:
Berikan penjelasan lisan yang sederhana dan berulang, diskusi ringan, serta tanya jawab.

🤸 Kinestetik:
Libatkan dalam aktivitas langsung seperti praktik sederhana, permainan edukatif, dan belajar sambil bergerak.
""",

    "SEDANG": """
🟡 Strategi Akademik:
Memberikan latihan bertahap pada kelompok sedang, dari materi yang mudah ke yang lebih kompleks.

📘 Strategi Berdasarkan Gaya Belajar:

🎨 Visual:
Gunakan infografis, diagram alur, dan catatan berwarna untuk membantu memahami konsep yang lebih kompleks.

🎧 Auditori:
Dorong diskusi kelompok, presentasi, dan penjelasan ulang materi dengan kata-kata sendiri.

🤸 Kinestetik:
Gunakan metode praktik, eksperimen, dan simulasi agar pemahaman semakin kuat.
""",

    "TINGGI": """
🟢 Strategi Akademik:
Memberikan pengayaan dan tantangan tambahan pada kelompok tinggi agar potensi berkembang maksimal.

📘 Strategi Berdasarkan Gaya Belajar:

🎨 Visual:
Berikan tugas proyek seperti membuat mind map kompleks, presentasi visual, atau desain konsep.

🎧 Auditori:
Dorong debat, presentasi, dan menjelaskan materi kepada teman lain (peer teaching).

🤸 Kinestetik:
Libatkan dalam proyek nyata, eksperimen lanjutan, atau kegiatan berbasis problem solving.
"""
}

# ========================
# SESSION DATA
# ========================
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Tanggal","Nama Guru","Lama Mengajar","Jenjang",
        "Kelas","Nama Anak","Usia","Ketunaan",
        "Total Skor","Hasil"
    ])

# ========================
# MENU
# ========================
menu = st.sidebar.radio("Menu", ["📋 Kuesioner", "📊 Dashboard Guru"])

# ========================
# HALAMAN KUESIONER
# ========================
if menu == "📋 Kuesioner":

    st.markdown('<p class="main-title">📊 Klasifikasi Akademik ABK Random Forest</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # DATA GURU
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("👨‍🏫 Data Guru")

        nama_guru = st.text_input("Nama Lengkap")
        lama_mengajar = st.number_input("Lama Mengajar (tahun)", 0, 50)
        jenjang = st.selectbox("Jenjang", ["Pilih", "SMPLB","SMALB"])

        st.markdown('</div>', unsafe_allow_html=True)

    # DATA ANAK
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("👦 Data Anak")

        kelas = st.text_input("Kelas")
        nama_anak = st.text_input("Nama Anak")
        usia = st.number_input("Usia", 5, 25)

        jenis_kebutuhan = st.selectbox(
            "Jenis Kebutuhan",
            ["Tunanetra","Tunarungu","Tunawicara","Tunagrahita Ringan","Tunagrahita Sedang", "Tunagrahita Berat", "Down Syndrome","Tunalaras", "CIBI", "Tunadaksa", "Tunaganda", "Autisme", "Hiperaktif", "Lainnya"]
        )

        if jenis_kebutuhan == "Lainnya":
            jenis_kebutuhan = st.text_input("Isi Jenis Lainnya")

        st.markdown('</div>', unsafe_allow_html=True)

    # ========================
    # KUESIONER
    # ========================
    st.subheader("📝 Kuesioner")

    skala = {"Pilih":0, "RENDAH":1, "SEDANG":2, "TINGGI":3}

    pertanyaan = [
        "Kemampuan memahami pelajaran melalui visual (gambar, tulisan atau video)",
        "Kemampuan memahami pelajaran melalui penjelasan lisan atau suara sesuai kondisi anak",
        "Kemampuan memahami pelajaran melalui kegiatan praktik langsung atau aktivitas fisik sesuai kondisi anak",
        "Kemampuan memahami informasi melalui media komunikasi sesuai kondisi anak (menulis tangan, braille, mengetik)",
        "Kemampuan menulis sesuai kondisi anak (menulis tangan, braille, mengetik)",
        "Kemampuan melakukan operasi hitung dasar (penjumlahan, pengurangan, perkalian, pembagian) sesuai kondisi anak",
        "Kemampuan memahami materi pelajaran yang diberikan sesuai dengan kemampuan dan kondisi anak",
        "Kemampuan mempertahankan konsentrasi saat mengikuti kegiatan pembelajaran",
        "Kemampuan mengingat kembali materi yang telah diajarkan",
        "Kemampuan mengikuti instruksi atau arahan dalam pembelajaran",
        "Kemampuan menyelesaikan tugas yang diberikan",
        "Keaftifan anak dalam mengikuti kegiatan pembelajaran"
    ]

    cols = st.columns(3)
    jawaban = []

    for i, p in enumerate(pertanyaan):
        with cols[i % 3]:
            val = st.selectbox(p, ["Pilih", "RENDAH","SEDANG","TINGGI"], key=p)
            jawaban.append(skala[val])

    # ========================
    # PROSES KLASIFIKASI
    # ========================
    if st.button("🚀 Klasifikasi Sekarang"):

        total_skor = sum(jawaban)

        # RULE
        if total_skor <= 15:
            hasil = "RENDAH"
        elif total_skor <= 25:
            hasil = "SEDANG"
        else:
            hasil = "TINGGI"

        # ========================
        # OUTPUT SESUAI PERMINTAAN
        # ========================
        st.markdown("### 📊 Hasil Klasifikasi")
        st.success(f"Hasil Klasifikasi = {hasil}")
        st.write(f"Total Skor = {total_skor}")

        # STRATEGI
        st.markdown("### 🎯 Strategi Berdasarkan Hasil Klasifikasi")
        st.info(strategi[hasil])

        # SIMPAN DATA
        new_data = pd.DataFrame([{
            "Tanggal": datetime.now(),
            "Nama Guru": nama_guru,
            "Lama Mengajar": lama_mengajar,
            "Jenjang": jenjang,
            "Kelas": kelas,
            "Nama Anak": nama_anak,
            "Usia": usia,
            "Ketunaan": jenis_kebutuhan,
            "Total Skor": total_skor,
            "Hasil": hasil
        }])

        st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)

# ========================
# DASHBOARD
# ========================
elif menu == "📊 Dashboard Guru":

    st.markdown('<p class="main-title">📈 Dashboard Data Guru</p>', unsafe_allow_html=True)

    df = st.session_state.data

    if df.empty:
        st.warning("Belum ada data")
    else:
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])

        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Distribusi Klasifikasi")
        st.bar_chart(df['Hasil'].value_counts())

        # ========================
        # EXPORT PDF
        # ========================
        def generate_pdf(dataframe):
            file_path = "laporan_abk.pdf"
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []

            styles = getSampleStyleSheet()
            elements.append(Paragraph("Laporan Klasifikasi ABK", styles['Title']))

            data = [list(dataframe.columns)] + dataframe.astype(str).values.tolist()

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.grey),
                ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                ('GRID',(0,0),(-1,-1),1,colors.black)
            ]))

            elements.append(table)
            doc.build(elements)

            return file_path

        if st.button("📥 Download PDF"):
            pdf_file = generate_pdf(df)
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="Klik Download PDF",
                    data=f,
                    file_name="laporan_abk.pdf",
                    mime="application/pdf"
                )
