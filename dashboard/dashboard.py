import base64
import io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Air Quality Analysis — Beijing",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSETS = Path("assets")      # hasil dari siapkan_aset.py
TOP_N_STATION = 5            # jumlah stasiun pada grafik batang horizontal

MONTH_SHORT = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
               7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"}
MONTH_FULL = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei",
              6: "Juni", 7: "Juli", 8: "Agustus", 9: "September",
              10: "Oktober", 11: "November", 12: "Desember"}

BLUE = "#5b9cf6"
NAVY = "#12377d"


# =========================================================
# HELPERS
# =========================================================

def clean(s: str) -> str:
    """Hapus indentasi & baris kosong.
    Penyebab HTML tampil sebagai kotak kode: baris berindentasi >= 4 spasi
    dianggap code block oleh Markdown, dan baris kosong memutus blok HTML."""
    return "\n".join(line.strip() for line in s.splitlines() if line.strip())


def html(s: str):
    st.markdown(clean(s), unsafe_allow_html=True)


@st.cache_data
def img_uri(name: str) -> str:
    p = ASSETS / name
    if not p.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def bg(name: str) -> str:
    u = img_uri(name)
    return f"url('{u}')" if u else "none"


ICONS = {
    "air": "M14.5 17c0 1.65-1.35 3-3 3s-3-1.35-3-3h2c0 .55.45 1 1 1s1-.45 1-1-.45-1-1-1H2v-2h9.5c1.65 0 3 1.35 3 3zM19 6.5C19 4.57 17.43 3 15.5 3S12 4.57 12 6.5h2c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5S16.33 8 15.5 8H2v2h13.5c1.93 0 3.5-1.57 3.5-3.5zm-.5 4.5H2v2h16.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5v2c1.93 0 3.5-1.57 3.5-3.5S20.43 11 18.5 11z",
    "warning": "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z",
    "database": "M12 3C7.58 3 4 4.79 4 7v10c0 2.21 3.59 4 8 4s8-1.79 8-4V7c0-2.21-3.58-4-8-4zm6 14c0 .5-2.13 2-6 2s-6-1.5-6-2v-2.23c1.61.78 3.72 1.23 6 1.23s4.39-.45 6-1.23V17zm0-4.55c-1.3.95-3.58 1.55-6 1.55s-4.7-.6-6-1.55V9.64c1.47.83 3.61 1.36 6 1.36s4.53-.53 6-1.36v2.81zM12 9C8.13 9 6 7.5 6 7s2.13-2 6-2 6 1.5 6 2-2.13 2-6 2z",
    "pin": "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z",
    "bar": "M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z",
    "calendar": "M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10z",
    "building": "M17 11V3H7v4H3v14h8v-4h2v4h8V11h-4zM7 19H5v-2h2v2zm0-4H5v-2h2v2zm0-4H5V9h2v2zm4 4H9v-2h2v2zm0-4H9V9h2v2zm0-4H9V5h2v2zm4 8h-2v-2h2v2zm0-4h-2V9h2v2zm0-4h-2V5h2v2zm4 12h-2v-2h2v2zm0-4h-2v-2h2v2z",
    "pie": "M11 2v20c-5.07-.5-9-4.79-9-10s3.93-9.5 9-10zm2.03 0v8.99H22c-.47-4.74-4.24-8.52-8.97-8.99zm0 11.01V22c4.74-.47 8.5-4.25 8.97-8.99h-8.97z",
    "trophy": "M19 5h-2V3H7v2H5c-1.1 0-2 .9-2 2v1c0 2.55 1.92 4.63 4.39 4.94.63 1.5 1.98 2.63 3.61 2.96V19H7v2h10v-2h-4v-3.1c1.63-.33 2.98-1.46 3.61-2.96C19.08 12.63 21 10.55 21 8V7c0-1.1-.9-2-2-2zM5 8V7h2v3.82C5.84 10.4 5 9.3 5 8zm14 0c0 1.3-.84 2.4-2 2.82V7h2v1z",
    "star": "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z",
    "bulb": "M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z",
    "target": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm0-6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z",
    "leaf": "M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75C7 8 17 8 17 8z",
}


def icon(name: str, size: int = 20, color: str = "currentColor") -> str:
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="{color}">'
            f'<path d="{ICONS[name]}"/></svg>')


def yoy_change(frame: pd.DataFrame, agg: str):
    """Perubahan (%) tahun lengkap terakhir vs tahun lengkap sebelumnya.
    Tahun lengkap = punya >= 10 bulan data (2017 hanya Januari–Februari, jadi diabaikan).
    Mengembalikan None jika rentang filter hanya memuat < 2 tahun lengkap."""
    g = frame.groupby("year").agg(val=("PM2.5", agg), n=("month", "nunique"))
    g = g[g["n"] >= 10]
    if len(g) < 2 or not g["val"].iloc[-2]:
        return None
    a, b = g["val"].iloc[-2], g["val"].iloc[-1]
    return (b - a) / a * 100


def chip(change):
    if change is None:
        return ""
    # PM2.5 turun = baik (hijau), naik = buruk (merah)
    cls, arrow = ("chip-down", "↓") if change < 0 else ("chip-up", "↑")
    return f'<span class="chip {cls}">{arrow} {abs(change):.1f}%</span>'


def kpi(icon_name, tone, label, value, chip_html=""):
    return f"""
    <div class="kpi">
        <div class="kpi-ico kpi-{tone}">{icon(icon_name, 24)}</div>
        <div class="kpi-main">
            <div class="kpi-label">{label}</div>
            <div class="kpi-valrow">
                <span class="kpi-value">{value}</span>{chip_html}
            </div>
        </div>
    </div>
    """


def card_head(icon_name, title, subtitle):
    html(f"""
        <div class="card-head">
            <span class="card-head-ico">{icon(icon_name, 20)}</span>
            <span class="card-title">{title}</span>
        </div>
        <div class="card-sub">{subtitle}</div>
    """)


def style_ax(ax, grid="y"):
    ax.set_facecolor("none")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#dbe5f4")
    ax.tick_params(colors="#3f5a87", length=0, labelsize=9)
    ax.grid(axis=grid, color="#dfe8f6", linewidth=0.9, linestyle=(0, (4, 4)))
    ax.set_axisbelow(True)


def nice_top(v, step=25, headroom=1.12):
    return float(np.ceil(v * headroom / step) * step)


def show(fig):
    """Render grafik sebagai PNG transparan di dalam kartu (tanpa argumen
    use_container_width yang berubah antar versi Streamlit)."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, transparent=True)
    plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode()
    html(f'<img src="data:image/png;base64,{b64}" style="width:100%;display:block">')


plt.rcParams.update({"font.family": "sans-serif", "text.color": "#27406e",
                     "axes.labelcolor": "#27406e"})


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():
    data = pd.read_csv("main_data.csv")
    data["datetime"] = pd.to_datetime(data["datetime"])
    return data


df = load_data()


# =========================================================
# CUSTOM CSS
# =========================================================

NAV = ["Dashboard", "Analysis", "Data", "About"]
NAV_MATERIAL = {"Dashboard": "home", "Analysis": "bar_chart",
                "Data": "database", "About": "info"}

CSS = """
<style>

/* ---------- GLOBAL ---------- */
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

.stApp {
    background:
        __SAKURA__ right bottom / 290px auto no-repeat fixed,
        linear-gradient(160deg, #e1eafc 0%, #d4e2fb 50%, #c9dbf8 100%);
}
.main .block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"][aria-expanded="true"] {
    min-width: 255px !important;
    max-width: 255px !important;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f7f8ff 0%, #eef3ff 100%);
    border-right: 1px solid #dfe8f8;
}
section[data-testid="stSidebar"] > div { padding-top: 0.5rem; }

.brand { text-align: center; padding: 6px 10px 18px 10px; }
.brand img { width: 96px; }
.brand-fallback {
    width: 72px; height: 72px; margin: auto; border-radius: 22px;
    display: flex; align-items: center; justify-content: center;
    font-size: 36px; color: white;
    background: linear-gradient(135deg, #49a6ff, #146ee8);
    box-shadow: 0 10px 25px rgba(37,128,235,.25);
}
.brand-title { margin-top: 6px; font-size: 27px; font-weight: 800; color: #12377d; }
.brand-subtitle { color: #4d6694; font-size: 14px; line-height: 1.45; }

/* radio -> tombol menu (struktur Streamlit lama: label[data-baseweb] / baru: stRadioOption) */
section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 8px !important; }
section[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div { width: 100%; }

section[data-testid="stSidebar"] label[data-baseweb="radio"],
section[data-testid="stSidebar"] label[data-testid="stRadioOption"] {
    display: flex; align-items: center;
    width: 100%; margin: 0;
    padding: 12px 18px; border-radius: 16px;
    cursor: pointer; transition: all .15s ease;
}
/* sembunyikan bulatan radio */
section[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child,
section[data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div:first-child { display: none !important; }

/* warna teks + ikon: dipaksa agar tidak ikut tema gelap */
section[data-testid="stSidebar"] label[data-baseweb="radio"] *,
section[data-testid="stSidebar"] label[data-testid="stRadioOption"] * {
    color: #4d6694 !important; font-size: 16px; font-weight: 600;
}
section[data-testid="stSidebar"] label[data-baseweb="radio"] p,
section[data-testid="stSidebar"] label[data-testid="stRadioOption"] p { margin: 0; }

section[data-testid="stSidebar"] label[data-baseweb="radio"]:hover,
section[data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover { background: #e4eeff; }

section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked),
section[data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked) {
    background: linear-gradient(135deg, #3b9bff, #1a6cf0);
    box-shadow: 0 8px 20px rgba(26,108,240,.30);
}
section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) *,
section[data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked) * {
    color: #ffffff !important;
}

/* ilustrasi + chip bawah sidebar */
.sb-bottom { position: fixed; bottom: 0; left: 0; width: 255px; pointer-events: none; }
.sb-art { height: 290px; background: __SIDEBAR__ center bottom / 100% auto no-repeat; margin-bottom: -22px; }
.sb-chip {
    position: relative; margin: 0 18px 20px 18px; padding: 13px 16px;
    display: flex; align-items: center; gap: 12px;
    background: rgba(255,255,255,.72); backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,.9); border-radius: 18px;
    box-shadow: 0 8px 22px rgba(40,90,160,.10);
}
.sb-chip b { display: block; color: #12377d; font-size: 13px; }
.sb-chip span.sb-year { color: #4d6694; font-size: 15px; }

/* ---------- HERO ---------- */
.hero {
    position: relative; min-height: 130px;
    padding: 24px 28px; border-radius: 26px;
    background:
        __HERO__ right center / auto 100% no-repeat,
        linear-gradient(110deg, #d1defc 0%, #bcd3fb 100%);
    border: 1px solid rgba(255,255,255,.85);
    box-shadow: 0 10px 30px rgba(50,100,170,.12);
}
.hero-row { display: flex; align-items: center; gap: 16px; }
.hero-icon {
    width: 50px; height: 50px; border-radius: 50%; flex: none;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #3b9bff, #1a6cf0);
    box-shadow: 0 6px 16px rgba(26,108,240,.35);
}
.hero-title { font-size: 34px; font-weight: 800; color: #0d2e6f; line-height: 1.1; }
.hero-subtitle { margin: 12px 0 0 66px; color: #1b3f80; font-size: 16px; font-weight: 500; }

/* ---------- FILTER BAR ---------- */
.st-key-card_filter { padding: 14px 22px 12px 22px !important; }
.st-key-card_filter label p { color: #12377d !important; font-weight: 700; font-size: 13px; }
.st-key-card_filter div[data-baseweb="select"] > div {
    background: #f3f7fe; border: 1px solid #dbe6f7; border-radius: 12px; min-height: 42px;
}
.st-key-card_filter div[data-baseweb="select"] * { color: #12377d !important; font-weight: 600; font-size: 14px; }
.st-key-card_filter span[data-baseweb="tag"] { background: #d6e9ff !important; border-radius: 8px; }
.st-key-card_filter span[data-baseweb="tag"] * { color: #12377d !important; }
.st-key-card_filter [data-testid="stSlider"] [data-testid="stThumbValue"],
.st-key-card_filter [data-testid="stSlider"] [data-testid="stTickBarMin"],
.st-key-card_filter [data-testid="stSlider"] [data-testid="stTickBarMax"] { color: #12377d !important; font-weight: 700; }

/* ---------- KPI ---------- */
.kpi {
    display: flex; align-items: center; gap: 14px; min-height: 108px;
    padding: 18px 20px; border-radius: 22px;
    background: rgba(255,255,255,.94); border: 1px solid #e6eefa;
    box-shadow: 0 8px 24px rgba(38,88,150,.08);
}
.kpi-ico { width: 54px; height: 54px; border-radius: 50%; flex: none;
           display: flex; align-items: center; justify-content: center; }
.kpi-blue   { background: #d6e9ff; color: #3b8def; }
.kpi-purple { background: #e9ddff; color: #8b5cf6; }
.kpi-green  { background: #d2f4e9; color: #22b58a; }
.kpi-orange { background: #ffe6c8; color: #f59e2b; }
.kpi-main { min-width: 0; }
.kpi-label { color: #17366f; font-size: 14px; font-weight: 500; white-space: nowrap; }
.kpi-valrow { display: flex; align-items: baseline; flex-wrap: wrap; column-gap: 10px; margin-top: 4px; }
.kpi-value { color: #0b2d70; font-size: 28px; font-weight: 800; line-height: 1.15; white-space: nowrap; }
.chip { font-size: 12px; font-weight: 600; white-space: nowrap; }
.chip-down { color: #1fa971; }
.chip-up { color: #ef4444; }

/* ---------- CARD (kontainer ber-key card_*) ---------- */
div[class*="st-key-card_"] {
    background: rgba(255,255,255,.95);
    border: 1px solid #e6eefa; border-radius: 22px;
    padding: 18px 20px 14px 20px;
    box-shadow: 0 8px 25px rgba(35,75,130,.08);
    gap: .4rem;
}
/* tinggi seragam per baris */
.st-key-card_monthly, .st-key-card_yearly { min-height: 440px; }
.st-key-card_station, .st-key-card_category { min-height: 440px; }
.st-key-card_period { min-height: 450px; }

.card-head { display: flex; align-items: center; gap: 10px; }
.card-head-ico { color: #3b8def; display: flex; }
.card-title { color: #102f6e; font-size: 18px; font-weight: 800; }
.card-sub { color: #7890b4; font-size: 12.5px; margin: 2px 0 8px 30px; }

/* kartu statis (halaman Analysis / About) */
.card {
    background: rgba(255,255,255,.94); border-radius: 22px; padding: 22px;
    border: 1px solid #e6eefa; box-shadow: 0 8px 25px rgba(35,75,130,.08);
    margin-bottom: 15px; color: #1d3a6e;
}
.section-title { color: #102f6e; font-size: 19px; font-weight: 800; margin-bottom: 6px; }

/* ---------- INSIGHT ---------- */
.insight-card {
    color: #fff; border-radius: 22px; padding: 22px 24px; min-height: 450px;
    background:
        radial-gradient(circle at 85% 90%, rgba(255,255,255,.18), transparent 45%),
        linear-gradient(160deg, #1d5fb8 0%, #2a7ee0 100%);
    box-shadow: 0 12px 30px rgba(29,105,201,.28);
}
.insight-title { font-size: 20px; font-weight: 800; margin-bottom: 22px; }
.insight-item { display: flex; gap: 12px; margin-bottom: 20px; }
.insight-ico { flex: none; margin-top: 2px; display: flex; }
.insight-label { font-size: 13px; opacity: .9; }
.insight-value { font-size: 19px; font-weight: 800; line-height: 1.3; margin-top: 2px; }
.insight-text { font-size: 13.5px; line-height: 1.55; opacity: .95; margin-top: 4px; }

/* ---------- TABEL PERIODE ---------- */
/* spesifisitas tinggi + !important agar border hitam bawaan Streamlit hilang */
div[data-testid="stMarkdownContainer"] table.period {
    width: 100%; border-collapse: separate !important; border-spacing: 0 !important;
    border: none !important; font-size: 14px; margin-top: 4px;
}
div[data-testid="stMarkdownContainer"] table.period th,
div[data-testid="stMarkdownContainer"] table.period td {
    border: none !important; border-bottom: 1px solid #edf2fb !important;
    padding: 12px 14px !important; text-align: left; white-space: nowrap;
}
div[data-testid="stMarkdownContainer"] table.period th {
    color: #12377d; font-weight: 700; background: #f1f5fd; border-bottom: none !important;
}
div[data-testid="stMarkdownContainer"] table.period th:first-child { border-radius: 10px 0 0 10px; }
div[data-testid="stMarkdownContainer"] table.period th:last-child { border-radius: 0 10px 10px 0; }
div[data-testid="stMarkdownContainer"] table.period td { color: #17366f; }
div[data-testid="stMarkdownContainer"] table.period tr:last-child td { border-bottom: none !important; }
div[data-testid="stMarkdownContainer"] table.period td:last-child { font-weight: 700; }

/* ---------- STREAMLIT ELEMENTS ---------- */
[data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3,
[data-testid="stMetricLabel"] *, [data-testid="stMetricValue"] *,
[data-testid="stCaptionContainer"] * { color: #12377d !important; }
div[data-testid="stMetric"] { background: transparent; }
div[data-testid="stDataFrame"] { border-radius: 15px; overflow: hidden; }

</style>
"""

CSS = (CSS.replace("__HERO__", bg("hero.png"))
          .replace("__SIDEBAR__", bg("sidebar.png"))
          .replace("__SAKURA__", bg("sakura.png")))
html(CSS)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    logo = img_uri("logo.png")
    logo_html = (f'<img src="{logo}" alt="logo">' if logo
                 else '<div class="brand-fallback">🌫️</div>')
    html(f"""
        <div class="brand">
            {logo_html}
            <div class="brand-title">AirQuality</div>
            <div class="brand-subtitle">Beijing Air Quality<br>Monitoring</div>
        </div>
    """)

    page = st.radio(
        "Menu", NAV, label_visibility="collapsed",
        format_func=lambda x: f":material/{NAV_MATERIAL[x]}:  {x}",
    )

    html(f"""
        <div class="sb-bottom">
            <div class="sb-art"></div>
            <div class="sb-chip">
                <span style="color:#22b58a;display:flex">{icon("leaf", 22)}</span>
                <div>
                    <b>PM2.5 Monitoring</b>
                    <span class="sb-year">2013 – 2017</span>
                </div>
            </div>
        </div>
    """)


# =========================================================
# HERO
# =========================================================

HERO_TEXT = {
    "Dashboard": ("Beijing Air Quality", "Monitoring konsentrasi PM2.5 · 2013–2017"),
    "Analysis": ("Analysis", "Business questions, findings, dan recommendation"),
    "Data": ("Data", "Preview dataset hasil cleaning"),
    "About": ("About", "Tentang dashboard ini"),
}

years = sorted(int(y) for y in df["year"].unique())
stations = sorted(df["station"].unique())

title, subtitle = HERO_TEXT[page]
html(f"""
    <div class="hero">
        <div class="hero-row">
            <span class="hero-icon">{icon("air", 28, "#fff")}</span>
            <span class="hero-title">{title}</span>
        </div>
        <div class="hero-subtitle">{subtitle}</div>
    </div>
""")

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)


# =========================================================
# FILTER BAR (rentang tahun + banyak stasiun)
# =========================================================

year_range = (years[0], years[-1])
selected_stations = []

if page in ("Dashboard", "Data"):
    with st.container(key="card_filter"):
        f1, f2 = st.columns([1, 1.7], gap="large")
        with f1:
            if len(years) > 1:
                year_range = st.select_slider(
                    "📅  Rentang Tahun", options=years,
                    value=(years[0], years[-1]), key="f_year")
            else:
                st.caption(f"Data hanya tersedia untuk tahun {years[0]}.")
        with f2:
            selected_stations = st.multiselect(
                "📍  Stasiun", stations, default=[], key="f_station",
                placeholder="Semua stasiun (pilih satu atau lebih untuk menyaring)")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)


# =========================================================
# APPLY FILTER
# =========================================================

filtered_df = df[df["year"].between(year_range[0], year_range[1])]
if selected_stations:
    filtered_df = filtered_df[filtered_df["station"].isin(selected_stations)]
filtered_df = filtered_df.copy()


# =========================================================
# DASHBOARD PAGE
# =========================================================

if page == "Dashboard":

    if filtered_df.empty:
        st.warning("Tidak ada data untuk kombinasi filter ini.")
        st.stop()

    # ---------- KPI ----------
    avg_pm25 = filtered_df["PM2.5"].mean()
    max_pm25 = filtered_df["PM2.5"].max()
    total_records = len(filtered_df)
    total_stations = filtered_df["station"].nunique()

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        html(kpi("air", "blue", "Rata-rata PM2.5", f"{avg_pm25:.2f}",
                 chip(yoy_change(filtered_df, "mean"))))
    with k2:
        html(kpi("warning", "purple", "Nilai Maksimum", f"{max_pm25:.0f}",
                 chip(yoy_change(filtered_df, "max"))))
    with k3:
        html(kpi("database", "green", "Jumlah Data", f"{total_records:,}"))
    with k4:
        html(kpi("pin", "orange", "Stasiun", f"{total_stations}"))

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ---------- data turunan ----------
    monthly = filtered_df.groupby("month")["PM2.5"].mean().reset_index()
    monthly["label"] = monthly["month"].map(MONTH_SHORT)

    yearly = filtered_df.groupby("year")["PM2.5"].mean().reset_index()

    station_avg = (filtered_df.groupby("station")["PM2.5"].mean()
                   .sort_values(ascending=False))

    year_month = filtered_df.groupby(["year", "month"])["PM2.5"].mean().reset_index()
    top_period = year_month.sort_values("PM2.5", ascending=False).head(5).copy()
    top_period["Periode"] = (top_period["month"].map(MONTH_FULL) + " "
                             + top_period["year"].astype(str))

    highest_station = station_avg.index[0]
    highest_station_val = station_avg.iloc[0]
    peak = top_period.iloc[0]
    highest_month_name = MONTH_FULL[int(peak["month"])]
    highest_month_val = peak["PM2.5"]

    # ===== baris 1: tren bulanan | per tahun =====
    r1a, r1b = st.columns([1.6, 1.0], gap="medium")

    with r1a:
        with st.container(key="card_monthly"):
            card_head("bar", "Tren Rata-rata PM2.5 per Bulan",
                      "Pola konsentrasi PM2.5 sepanjang tahun.")
            fig, ax = plt.subplots(figsize=(8.0, 3.6))
            style_ax(ax, grid="both")
            x = np.arange(len(monthly))
            y = monthly["PM2.5"].values
            ax.plot(x, y, color="#2b7de9", lw=2.4, marker="o", ms=6.5,
                    mfc="#2b7de9", mec="white", mew=1.6, zorder=3)
            ax.set_xticks(x, monthly["label"])
            top = nice_top(y.max(), 25, 1.2)
            ax.set_ylim(0, top)
            ax.set_yticks(np.arange(0, top + 1, 25))
            ax.set_ylabel("Rata-rata PM2.5", fontsize=10, fontweight="bold")
            ax.margins(x=0.05)
            i = int(np.argmax(y))
            ax.annotate(f"{monthly['label'].iloc[i]}: {y[i]:.2f}", xy=(x[i], y[i]),
                        xytext=(34 if i < len(y) / 2 else -34, 24), textcoords="offset points",
                        ha="center", color="white", fontsize=9.5, fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.45", fc="#1d6fe8", ec="none"),
                        arrowprops=dict(arrowstyle="-", color="#1d6fe8", lw=1.2),
                        zorder=4)
            fig.tight_layout()
            show(fig)

    with r1b:
        with st.container(key="card_yearly"):
            card_head("calendar", "Rata-rata PM2.5 per Tahun",
                      "Perbandingan rata-rata antar tahun.")
            fig, ax = plt.subplots(figsize=(5.0, 3.6))
            style_ax(ax, grid="y")
            bars = ax.bar(yearly["year"].astype(str), yearly["PM2.5"],
                          color=BLUE, width=0.64, zorder=3)
            top = nice_top(yearly["PM2.5"].max(), 25, 1.12)
            ax.set_ylim(0, top)
            ax.set_yticks(np.arange(0, top + 1, 25))
            for b in bars:
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + top * 0.02,
                        f"{b.get_height():.2f}", ha="center", fontsize=9,
                        fontweight="bold", color="#0b2d70")
            fig.tight_layout()
            show(fig)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ===== baris 2: stasiun | kategori =====
    r2a, r2b = st.columns([1.6, 1.0], gap="medium")

    with r2a:
        with st.container(key="card_station"):
            card_head("building", "Rata-rata PM2.5 Berdasarkan Stasiun",
                      f"Perbandingan konsentrasi antar stasiun "
                      f"(maks. {TOP_N_STATION} tertinggi).")
            sc = station_avg.head(TOP_N_STATION)
            fig, ax = plt.subplots(figsize=(8.0, 3.6))
            style_ax(ax, grid="x")
            ax.spines["left"].set_visible(False)
            ax.tick_params(axis="y", labelsize=10)
            ax.barh(sc.index[::-1], sc.values[::-1], color=BLUE, height=0.6, zorder=3)
            xmax = nice_top(sc.max(), 20, 1.12)
            ax.set_xlim(0, xmax)
            ax.set_xticks(np.arange(0, xmax + 1, 20))
            for k, v in enumerate(sc.values[::-1]):
                ax.text(v + xmax * 0.015, k, f"{v:.2f}", va="center",
                        fontsize=10, fontweight="bold", color="#2b7de9")
            fig.tight_layout()
            show(fig)

    with r2b:
        with st.container(key="card_category"):
            card_head("pie", "Kategori PM2.5",
                      "Pengelompokan stasiun berdasarkan quartile.")
            if len(station_avg) >= 3:
                q1, q3 = station_avg.quantile(0.25), station_avg.quantile(0.75)
                labels = ["Rendah", "Sedang", "Tinggi"]
                cats = pd.cut(station_avg, bins=[-np.inf, q1, q3, np.inf], labels=labels)
                counts = cats.value_counts().reindex(labels).fillna(0)
                fig, ax = plt.subplots(figsize=(5.0, 3.6))
                style_ax(ax, grid="y")
                ax.tick_params(axis="x", labelsize=10)
                bars = ax.bar(counts.index, counts.values, width=0.66, zorder=3,
                              color=["#5b9cf6", "#a98bf8", "#6fd3f7"])
                top = max(counts.max() * 1.2, 2)
                ax.set_ylim(0, top)
                ax.set_yticks(range(0, int(top) + 1, 2))
                for b in bars:
                    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + top * 0.02,
                            f"{int(b.get_height())}", ha="center", fontsize=10,
                            fontweight="bold", color="#0b2d70")
                fig.tight_layout()
                show(fig)
            else:
                st.caption("Pilih minimal 3 stasiun (atau kosongkan filter stasiun) "
                           "untuk pengelompokan quartile.")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ===== baris 3: periode tertinggi | key insights =====
    r3a, r3b = st.columns([1.6, 1.0], gap="medium")

    with r3a:
        with st.container(key="card_period"):
            card_head("trophy", "Periode dengan PM2.5 Tertinggi",
                      "Lima periode dengan rata-rata tertinggi.")
            rows = "".join(
                f"<tr><td>{p}</td><td>{v:.2f}</td></tr>"
                for p, v in zip(top_period["Periode"], top_period["PM2.5"])
            )
            html(f"""
                <table class="period">
                    <tr><th>Periode</th><th>Rata-rata PM2.5</th></tr>
                    {rows}
                </table>
            """)

    with r3b:
        html(f"""
            <div class="insight-card">
                <div class="insight-title">
                    <span style="display:inline-flex;vertical-align:middle;color:#ffd66b">{icon("bulb", 24)}</span>
                    &nbsp;Key Insights
                </div>
                <div class="insight-item">
                    <span class="insight-ico" style="color:#d9c8ff">{icon("star", 22)}</span>
                    <div>
                        <div class="insight-label">Stasiun Tertinggi</div>
                        <div class="insight-value">{highest_station} ({highest_station_val:.2f})</div>
                    </div>
                </div>
                <div class="insight-item">
                    <span class="insight-ico" style="color:#ffd0d0">{icon("calendar", 22)}</span>
                    <div>
                        <div class="insight-label">Periode Tertinggi</div>
                        <div class="insight-value">{highest_month_name} {int(peak["year"])} ({highest_month_val:.2f})</div>
                    </div>
                </div>
                <div class="insight-item">
                    <span class="insight-ico" style="color:#ffd66b">{icon("target", 22)}</span>
                    <div>
                        <div class="insight-label" style="font-size:15px;font-weight:700;opacity:1">Rekomendasi</div>
                        <div class="insight-text">
                            Fokus pemantauan pada stasiun dengan konsentrasi
                            PM2.5 tinggi, terutama <b>{highest_station}</b>.
                        </div>
                    </div>
                </div>
            </div>
        """)


# =========================================================
# ANALYSIS PAGE
# =========================================================

elif page == "Analysis":

    html("""
        <div class="card">
            <div class="section-title">Business Question 1</div>
            <p>
                Bagaimana tren perubahan rata-rata konsentrasi PM2.5 secara bulanan
                dan tahunan di Beijing selama periode 2013–2017, serta pada tahun
                dan bulan apa konsentrasi tertinggi terjadi?
            </p>
            <hr>
            <b>Kesimpulan</b>
            <p>
                Rata-rata konsentrasi PM2.5 menunjukkan pola yang berfluktuasi secara
                bulanan dan tahunan. Berdasarkan kombinasi tahun dan bulan, konsentrasi
                tertinggi terjadi pada <b>Februari 2014 sebesar 153,81</b>.
            </p>
        </div>
    """)

    html("""
        <div class="card">
            <div class="section-title">Business Question 2</div>
            <p>
                Stasiun pemantauan mana yang memiliki rata-rata konsentrasi PM2.5
                tertinggi di Beijing selama periode 2013–2017?
            </p>
            <hr>
            <b>Kesimpulan</b>
            <p>
                <b>Dongsi</b> memiliki rata-rata konsentrasi PM2.5 tertinggi sebesar
                <b>86,14</b>, sedangkan Dingling memiliki rata-rata terendah sebesar
                <b>66,85</b>. Selisih keduanya sebesar <b>19,30</b>.
            </p>
        </div>
    """)

    html("""
        <div class="card">
            <div class="section-title">🎯 Recommendation</div>
            <p>
                Pemantauan kualitas udara dapat diprioritaskan pada stasiun dengan
                rata-rata PM2.5 yang relatif tinggi, khususnya
                <b>Dongsi, Nongzhanguan, dan Wanshouxigong</b>.
            </p>
            <p>
                Periode dengan konsentrasi PM2.5 yang cenderung tinggi, terutama
                <b>bulan Desember</b>, juga dapat menjadi perhatian dalam pemantauan
                kualitas udara.
            </p>
        </div>
    """)


# =========================================================
# DATA PAGE
# =========================================================

elif page == "Data":

    d1, d2, d3 = st.columns(3)
    d1.metric("Jumlah Baris", f"{len(filtered_df):,}")
    d2.metric("Jumlah Kolom", len(filtered_df.columns))
    d3.metric("Jumlah Stasiun", filtered_df["station"].nunique())

    st.markdown("---")
    st.subheader("Preview Data")
    try:
        st.dataframe(filtered_df.head(100), width="stretch", hide_index=True)
    except TypeError:                      # Streamlit versi lama
        st.dataframe(filtered_df.head(100), use_container_width=True, hide_index=True)


# =========================================================
# ABOUT PAGE
# =========================================================

elif page == "About":

    html("""
        <div class="card">
            <div class="section-title">🌫️ Air Quality Analysis — Beijing</div>
            <p>
                Dashboard ini merupakan bagian dari proyek analisis data menggunakan
                Air Quality Dataset.
            </p>
            <p>
                Dataset berisi data kualitas udara dari beberapa stasiun pemantauan
                di Beijing pada periode 2013–2017.
            </p>
            <hr>
            <b>Fokus Analisis</b>
            <ul>
                <li>Tren konsentrasi PM2.5</li>
                <li>Perbandingan antarstasiun</li>
                <li>Periode dengan konsentrasi tertinggi</li>
                <li>Pengelompokan stasiun berdasarkan PM2.5</li>
            </ul>
        </div>
    """)
