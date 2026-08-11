import html
from datetime import datetime
from urllib.parse import quote

import pandas as pd
import streamlit as st


# ============================================================
# SHEGO CONFIG — EDIT HERE ONLY IF NEEDED
# ============================================================
SPREADSHEET_ID = "1Gq6boYuQfROpuJXpChvu0nkBtODZ-aXwtK6B6fyddgM"
SHEET_TAB = "Driver Board"

# 0125057046 -> WhatsApp international format
ADMIN_WHATSAPP = "60125057046"

# Only jobs with this status will be shown
OPEN_STATUS = "Open"


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="SheGO Driver Board",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# STYLE
# ============================================================
st.markdown(
    """
    <style>
        #MainMenu {visibility:hidden;}
        footer {visibility:hidden;}
        header[data-testid="stHeader"] {background:rgba(255,255,255,.72);}

        .stApp {
            background:
              radial-gradient(circle at 95% 0%, #ffe6ef 0, transparent 28%),
              linear-gradient(180deg,#fffafd 0%,#ffffff 38%);
        }

        .block-container {
            max-width: 1120px;
            padding-top: 1.4rem;
            padding-bottom: 5rem;
        }

        .topbar {
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:16px;
            margin-bottom:18px;
        }

        .brand {
            display:flex;
            align-items:center;
            gap:12px;
        }

        .logo {
            width:48px;
            height:48px;
            border-radius:15px;
            display:grid;
            place-items:center;
            color:white;
            font-size:22px;
            font-weight:900;
            background:linear-gradient(135deg,#d84f7d,#f08dae);
            box-shadow:0 10px 28px rgba(216,79,125,.24);
        }

        .brand-title {
            font-size:1.55rem;
            font-weight:900;
            letter-spacing:-.04em;
            color:#172033;
            line-height:1;
        }

        .brand-title span {color:#d84f7d;}

        .brand-sub {
            color:#778093;
            font-size:.82rem;
            margin-top:5px;
        }

        .hero {
            position:relative;
            overflow:hidden;
            padding:34px;
            border-radius:30px;
            border:1px solid #f0dce4;
            background:
              radial-gradient(circle at 88% 20%, rgba(255,206,222,.9), transparent 28%),
              linear-gradient(135deg,#ffffff,#fff3f7);
            box-shadow:0 18px 48px rgba(53,31,42,.07);
            margin-bottom:24px;
        }

        .hero::after {
            content:"";
            position:absolute;
            width:160px;
            height:160px;
            border-radius:50%;
            right:-60px;
            bottom:-80px;
            background:rgba(216,79,125,.08);
        }

        .kicker {
            display:inline-flex;
            align-items:center;
            gap:7px;
            border-radius:999px;
            padding:7px 12px;
            background:#fff;
            border:1px solid #f1d7e1;
            color:#b83c67;
            font-weight:850;
            font-size:.76rem;
            letter-spacing:.07em;
        }

        .hero h1 {
            max-width:720px;
            color:#172033;
            font-size:clamp(2.1rem,5vw,4rem);
            line-height:1.02;
            letter-spacing:-.055em;
            margin:15px 0 12px;
        }

        .hero p {
            max-width:760px;
            color:#667085;
            font-size:1rem;
            margin:0;
        }

        .summary-row {
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:12px;
            margin:4px 0 14px;
        }

        .count-pill {
            display:inline-flex;
            align-items:center;
            gap:8px;
            background:#fff0f5;
            border:1px solid #f0ccd9;
            color:#b83c67;
            padding:8px 13px;
            border-radius:999px;
            font-size:.84rem;
            font-weight:850;
        }

        .job-id {
            font-weight:900;
            color:#172033;
            font-size:1.25rem;
            letter-spacing:-.02em;
        }

        .open-pill {
            display:inline-flex;
            align-items:center;
            gap:6px;
            color:#147b58;
            background:#eaf8f1;
            border:1px solid #d0eddf;
            border-radius:999px;
            padding:5px 10px;
            font-size:.75rem;
            font-weight:850;
            margin-top:6px;
        }

        .fare {
            text-align:right;
        }

        .fare small {
            color:#7a8393;
            font-size:.72rem;
            font-weight:800;
            letter-spacing:.06em;
        }

        .fare strong {
            display:block;
            color:#172033;
            font-size:1.45rem;
            line-height:1.1;
            margin-top:3px;
        }

        .route-card {
            background:#fff7fa;
            border:1px solid #f2dfe7;
            border-radius:18px;
            padding:16px 18px;
            margin:14px 0 16px;
        }

        .route-label {
            color:#8b7180;
            font-size:.70rem;
            font-weight:850;
            letter-spacing:.07em;
        }

        .route-value {
            color:#172033;
            font-size:1rem;
            font-weight:800;
            margin-top:2px;
            word-break:break-word;
        }

        .route-line {
            width:2px;
            height:13px;
            background:#e6a3b9;
            margin:5px 0 5px 8px;
        }

        .privacy {
            margin-top:12px;
            padding:11px 13px;
            border-radius:13px;
            background:#f7f8fa;
            border:1px solid #e6e8ec;
            color:#667085;
            font-size:.82rem;
        }

        .footer-note {
            margin-top:26px;
            padding:14px 16px;
            border-radius:16px;
            background:#fff8e8;
            border:1px solid #efdfbd;
            color:#755a31;
            font-size:.83rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background:white;
            border:1px solid #eedfe5 !important;
            border-radius:24px !important;
            box-shadow:0 11px 30px rgba(51,31,41,.05);
            overflow:hidden;
        }

        .stLinkButton > a,
        .stButton > button {
            border-radius:13px !important;
            min-height:46px;
            font-weight:850 !important;
        }

        @media (max-width: 720px) {
            .block-container {
                padding-left:.9rem;
                padding-right:.9rem;
                padding-top:.8rem;
            }

            .hero {
                padding:23px 18px;
                border-radius:23px;
            }

            .hero h1 {
                font-size:2.3rem;
            }

            .topbar {
                align-items:flex-start;
            }

            .logo {
                width:43px;
                height:43px;
                border-radius:13px;
            }

            .fare {
                text-align:left;
                margin-top:9px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GOOGLE SHEET
# ============================================================
def sheet_csv_url():
    """
    Reads only the public/published tab named 'Driver Board'.
    No Google Service Account or Streamlit Secrets are needed.
    """
    return (
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq"
        f"?tqx=out:csv&sheet={quote(SHEET_TAB)}"
    )


@st.cache_data(ttl=30, show_spinner=False)
def load_jobs():
    url = sheet_csv_url()

    try:
        df = pd.read_csv(url)
    except Exception as exc:
        raise RuntimeError(
            "Tak dapat baca tab 'Driver Board'. "
            "Pastikan tab itu wujud dan telah dipublish ke web."
        ) from exc

    # Clean header names
    df.columns = [str(c).strip() for c in df.columns]

    # Remove completely empty rows
    df = df.dropna(how="all").copy()

    return df


# ============================================================
# COLUMN HELPERS
# ============================================================
COLUMN_ALIASES = {
    "booking_id": ["Booking ID", "ID", "Job ID"],
    "status": ["Status"],
    "pickup": ["Pickup", "Lokasi Ambil", "Lokasi Ambil (Pickup)"],
    "destination": ["Destinasi", "Destination"],
    "date": ["Tarikh", "Tarikh Perjalanan"],
    "time": ["Masa", "Masa Pickup"],
    "pax": ["Penumpang", "Bilangan Penumpang", "Pax"],
    "trip_type": ["Jenis Trip", "Jenis Perjalanan"],
    "baggage": ["Bagasi"],
    "notes": ["Nota", "Nota Tambahan"],
    "fare": ["Tambang (RM)", "Tambang", "Fare"],
}


def find_column(df, key):
    for candidate in COLUMN_ALIASES[key]:
        if candidate in df.columns:
            return candidate
    return None


def text(value, fallback="-"):
    if pd.isna(value):
        return fallback

    value = str(value).strip()

    if value == "" or value.lower() == "nan":
        return fallback

    return value


def safe_html(value, fallback="-"):
    return html.escape(text(value, fallback))


def get_value(row, column, fallback="-"):
    if not column:
        return fallback
    return text(row.get(column, ""), fallback)


# ============================================================
# BRAND
# ============================================================
st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            <div class="logo">S</div>
            <div>
                <div class="brand-title"><span>She</span>GO</div>
                <div class="brand-sub">Driver Job Board • Johor</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================
st.markdown(
    """
    <section class="hero">
        <span class="kicker">🚗 SHEGO • JOB TERSEDIA</span>
        <h1>Pilih perjalanan yang sesuai dengan anda.</h1>
        <p>
            Semak lokasi, tarikh, masa dan tambang. Jika berminat,
            tekan butang WhatsApp untuk claim job dengan admin SheGO.
            Job hanya dianggap sah selepas admin memberi pengesahan.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================
try:
    jobs = load_jobs()
except Exception as exc:
    st.error(str(exc))
    st.info(
        "Dalam Google Sheet, buat tab bernama **Driver Board** dan publish "
        "tab itu melalui **File → Share → Publish to web**."
    )
    st.stop()


if jobs.empty:
    st.info("Belum ada job tersedia sekarang.")
    st.stop()


# Resolve columns
cols = {
    key: find_column(jobs, key)
    for key in COLUMN_ALIASES
}


if not cols["status"]:
    st.error(
        "Column **Status** tak dijumpai. "
        "Pastikan tab Driver Board mempunyai column bernama `Status`."
    )
    st.stop()


# Only show Open jobs
open_jobs = jobs[
    jobs[cols["status"]]
    .astype(str)
    .str.strip()
    .str.casefold()
    .eq(OPEN_STATUS.casefold())
].copy()


# ============================================================
# FILTER
# ============================================================
filter_col, refresh_col = st.columns([4, 1], vertical_alignment="bottom")

with filter_col:
    search = st.text_input(
        "Cari kawasan",
        placeholder="Contoh: Ulu Tiram, JB, Senai, Pasir Gudang...",
    ).strip().casefold()

with refresh_col:
    if st.button("↻ Refresh", use_container_width=True):
        load_jobs.clear()
        st.rerun()


if search and not open_jobs.empty:
    pickup_series = (
        open_jobs[cols["pickup"]].astype(str).str.casefold()
        if cols["pickup"]
        else pd.Series("", index=open_jobs.index)
    )

    destination_series = (
        open_jobs[cols["destination"]].astype(str).str.casefold()
        if cols["destination"]
        else pd.Series("", index=open_jobs.index)
    )

    open_jobs = open_jobs[
        pickup_series.str.contains(search, regex=False, na=False)
        | destination_series.str.contains(search, regex=False, na=False)
    ]


st.markdown(
    f'<div class="summary-row">'
    f'<span class="count-pill">🚘 {len(open_jobs)} job tersedia</span>'
    f'</div>',
    unsafe_allow_html=True,
)


if open_jobs.empty:
    st.info("Tiada job yang sepadan dengan carian anda sekarang.")
    st.stop()


# ============================================================
# JOB CARDS
# ============================================================
for index, row in open_jobs.iterrows():

    # Fallback ID if no Booking ID column/value
    booking_id = get_value(row, cols["booking_id"], "")
    if not booking_id:
        booking_id = f"SG-{index + 1:05d}"

    pickup = get_value(row, cols["pickup"])
    destination = get_value(row, cols["destination"])
    trip_date = get_value(row, cols["date"])
    pickup_time = get_value(row, cols["time"])
    pax = get_value(row, cols["pax"])
    trip_type = get_value(row, cols["trip_type"])
    baggage = get_value(row, cols["baggage"], "Tidak dinyatakan")
    notes = get_value(row, cols["notes"], "Tiada")
    fare = get_value(row, cols["fare"], "Semak dengan admin")

    with st.container(border=True):

        left, right = st.columns([4, 1], vertical_alignment="top")

        with left:
            st.markdown(
                f"""
                <div class="job-id">{safe_html(booking_id)}</div>
                <span class="open-pill">● OPEN</span>
                """,
                unsafe_allow_html=True,
            )

        with right:
            fare_display = (
                f"RM {safe_html(fare)}"
                if fare not in ["-", "Semak dengan admin"]
                else safe_html(fare)
            )

            st.markdown(
                f"""
                <div class="fare">
                    <small>TAMBANG</small>
                    <strong>{fare_display}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="route-card">
                <div class="route-label">PICKUP</div>
                <div class="route-value">📍 {safe_html(pickup)}</div>
                <div class="route-line"></div>
                <div class="route-label">DESTINASI</div>
                <div class="route-value">🏁 {safe_html(destination)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        a, b, c = st.columns(3)

        with a:
            st.markdown(f"**📅 Tarikh**  \n{trip_date}")

        with b:
            st.markdown(f"**🕐 Masa Pickup**  \n{pickup_time}")

        with c:
            st.markdown(f"**👥 Penumpang**  \n{pax}")

        d, e = st.columns(2)

        with d:
            st.markdown(f"**🚗 Jenis Trip**  \n{trip_type}")

        with e:
            st.markdown(f"**🧳 Bagasi**  \n{baggage}")

        if notes not in ["-", "Tiada"]:
            st.markdown(f"**📝 Nota:** {notes}")

        st.markdown(
            """
            <div class="privacy">
                🔒 Maklumat nama dan nombor telefon pelanggan tidak dipaparkan
                kepada umum. Detail lanjut akan diberikan selepas admin
                mengesahkan driver untuk job tersebut.
            </div>
            """,
            unsafe_allow_html=True,
        )

        whatsapp_message = (
            f"Hi Admin SheGO, saya berminat nak claim job {booking_id}.\n\n"
            f"Pickup: {pickup}\n"
            f"Destinasi: {destination}\n"
            f"Tarikh: {trip_date}\n"
            f"Masa: {pickup_time}\n"
            f"Tambang: {fare}\n\n"
            "Boleh semak sama ada job ini masih available?"
        )

        whatsapp_url = (
            f"https://wa.me/{ADMIN_WHATSAPP}"
            f"?text={quote(whatsapp_message)}"
        )

        st.link_button(
            "💬 WhatsApp Admin untuk Claim Job",
            whatsapp_url,
            type="primary",
            use_container_width=True,
        )


# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class="footer-note">
        💡 <b>Nota:</b> Senarai ini dikemas kini berdasarkan Google Sheet SheGO.
        Selepas job telah diambil, status akan ditukar oleh admin dan job tersebut
        tidak lagi dipaparkan sebagai Open.
    </div>
    """,
    unsafe_allow_html=True,
)
