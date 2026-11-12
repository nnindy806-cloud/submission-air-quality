# Proyek Analisis Data: Air Quality Dataset (Beijing)

Analisis konsentrasi PM2.5 di 12 stasiun pemantauan Beijing (Maret 2013 – Februari 2017) beserta dashboard interaktif Streamlit.

**Nama:** Nindy Viviva Asri
**ID Dicoding:** DS296B6X1381

## Pertanyaan Bisnis
1. Bagaimana tren rata-rata PM2.5 bulanan dan tahunan, serta kapan konsentrasi tertinggi terjadi?
2. Stasiun mana yang memiliki rata-rata PM2.5 tertinggi, dan berapa selisihnya dibanding stasiun lain?

Analisis lanjutan: *binning* (manual grouping) stasiun berdasarkan kuartil rata-rata PM2.5.

## Struktur Direktori
```
submission
├── dashboard
│   ├── assets/           # gambar untuk tampilan dashboard
│   ├── dashboard.py
│   └── main_data.csv
├── data/                 # 12 file CSV dataset asli
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment
```
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

## Menjalankan Dashboard
```
cd dashboard
streamlit run dashboard.py
```
Dashboard terbuka di `http://localhost:8501`. Gunakan filter **Rentang Tahun** dan **Stasiun** (bisa memilih lebih dari satu) di bagian atas halaman Dashboard.

## Dashboard Online
Lihat tautan pada `url.txt`.
