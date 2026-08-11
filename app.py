from pathlib import Path
from urllib.parse import quote

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="SheGO Driver Board",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "shego_logo.png"


# ============================================================
# GOOGLE FORM / SHEET COLUMN NAMES
# ============================================================
CUSTOMER_COLUMNS = {
    "pickup": "Lokasi Ambil (Pickup)",
    "destination": "Destinasi",
    "date": "Tarikh Perjalanan",
    "time": "Masa Pickup",
    "pax": "Bilangan Penumpang",
    "trip_type": "Jenis Perjalanan",
    "return_time": "Anggaran Masa Balik",
    "baggage": "Bagasi",
    "notes": "Nota Tambahan",
}

# These columns are controlled manually by the admin in Google Sheets.
PUBLIC_COLUMNS = {
    "booking_id": "Booking ID",
    "status": "Status",
    "fare": "Tambang (RM)",
}


# ============================================================
# STYLE
# ============================================================
st.markdown(
    """
    <style>
        #MainMenu, footer {visibility:hidden;}
        .stApp { background:#fffafc; }
        .block-container {
            max-width:1160px;
            padding-top:1.2rem;
            padding-bottom:4.5rem;
        }

        .brand-row {
            display:flex;
            align-items:center;
            gap:12px;
            margin:0 0 10px;
        }
        .brand-name {
            font-weight:850;
            font-size:1.75rem;
            letter-spacing:-.045em;
            color:#172033;
        }
        .brand-name span { color:#d84f7d; }
        .brand-sub { color:#667085; font-size:.93rem; }

        .hero {
            background:
                radial-gradient(circle at 86% 18%, #ffd9e6 0, transparent 30%),
                linear-gradient(135deg,#ffffff 0%,#fff2f6 100%);
            border:1px solid #f0dae3;
            border-radius:28px;
            padding:30px;
            margin:10px 0 22px;
            box-shadow:0 14px 38px rgba(52,31,43,.06);
        }
        .hero-kicker {
            color:#b83c67;
            font-weight:850;
            font-size:.78rem;
            letter-spacing:.08em;
        }
        .hero-title {
            font-size:clamp(2rem,5vw,3.55rem);
            line-height:1.04;
            letter-spacing:-.05em;
            color:#172033;
            font-weight:850;
            margin:.35rem 0 .7rem;
        }
        .hero-copy {
            max-width:760px;
            color:#667085;
            font-size:1rem;
        }

        .job-pill {
            display:inline-flex;
            align-items:center;
            gap:7px;
            background:#fff0f5;
            color:#b83c67;
            border:1px solid #f0ccd9;
            border-radius:999px;
            padding:7px 12px;
            font-size:.82rem;
            font-weight:800;
        }
        .open-pill {
            display:inline-block;
            background:#eaf8f1;
            color:#157f5b;
            border:1px solid #d1eee0;
            border-radius:999px;
            padding:5px 10px;
            font-size:.77rem;
            font-weight:850;
        }
        .job-id {
            font-size:1.25rem;
            font-weight:850;
            color:#172033;
            margin-bottom:6px;
        }
        .route {
            background:#fff7fa;
            border:1px solid #f2e0e7;
            border-radius:18px;
            padding:17px 18px;
            margin:12px 0 15px;
        }
        .route-main {
            font-weight:800;
            color:#172033;
            font-size:1.03rem;
            line-height:1.55;
        }
        .route-arrow { color:#d84f7d; padding-left:2px; }
        .label { color:#667085; font-size:.78rem; font-weight:700; }
        .fare-box {
            text-align:right;
            min-width:105px;
        }
        .fare-label { color:#667085; font-size:.76rem; }
        .fare-value { color:#172033; font-size:1.35rem; font-weight:850; }
        .privacy {
            background:#f8f9fb;
            border:1px solid #e7e9ee;
            color:#667085;
            border-radius:14px;
            padding:11px 13px;
            font-size:.84rem;
            margin-top:10px;
        }
        .sheet-note {
            background:#fff7e9;
            border:1px solid #f1dfbf;
            color:#805d30;
            border-radius:14px;
            padding:11px 13px;
            font-size:.85rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background:#fff;
            border-color:#eddee4 !important;
            border-radius:22px !important;
            box-shadow:0 9px 24px rgba(50,32,40,.045);
        }
        .stLinkButton > a, .stButton > button {
            border-radius:13px !important;
            font-weight:800 !important;
            min-height:46px;
        }

        @media (max-width: 700px) {
            .block-container {
                padding-left:.9rem;
                padding-right:.9rem;
                padding-top:.8rem;
            }
            .hero { padding:22px 18px; border-radius:22px; }
            .hero-title { font-size:2.25rem; }
            .fare-box { text-align:left; margin-top:7px; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GOOGLE SHEETS — READ ONLY
# ============================================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


@st.cache_resource
def get_google_client():
    if "gcp_service_account" not in st.secrets:
        raise RuntimeError("Secret [gcp_service_account] belum diset.")

    info = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)


@st.cache_resource
def get_spreadsheet():
    try:
        spreadsheet_id = st.secrets["google_sheet"]["spreadsheet_id"]
    except Exception as exc:
        raise RuntimeError("Secret google_sheet.spreadsheet_id belum diset.") from exc

    return get_google_client().open_by_key(str(spreadsheet_id))


def find_booking_worksheet():
    ss = get_spreadsheet()

    for ws in ss.worksheets():
        headers = ws.row_values(1)
        if (
            CUSTOMER_COLUMNS["pickup"] in headers
            and CUSTOMER_COLUMNS["destination"] in headers
        ):
            return ws

    raise RuntimeError(
        "Tak jumpa tab response tempahan. Pastikan spreadsheet_id ialah Google Sheet daripada borang tempahan SheGO."
    )


@st.cache_data(ttl=30, show_spinner=False)
def load_bookings():
    ws = find_booking_worksheet()
    values = ws.get_all_values()

    if not values:
        return pd.DataFrame()

    headers = values[0]
    rows = values[1:]

    if not rows:
        return pd.DataFrame(columns=headers)

    normalized_rows = []
    for row_number, row in enumerate(rows, start=2):
        padded = row + [""] * max(0, len(headers) - len(row))
        item = dict(zip(headers, padded[: len(headers)]))
        item["__row_number"] = row_number
        normalized_rows.append(item)

    return pd.DataFrame(normalized_rows)


def safe_value(row, column, fallback="-"):
    if column not in row:
        return fallback
    value = row.get(column, "")
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def booking_id_for_row(row):
    existing = safe_value(row, PUBLIC_COLUMNS["booking_id"], "")
    if existing:
        return existing
    return f"SG-{int(row['__row_number']):05d}"


def secret_value(name, default=""):
    try:
        return str(st.secrets[name]).strip()
    except Exception:
        return default


# ============================================================
# BRAND
# ============================================================
def render_brand():
    col_logo, col_text = st.columns([1, 5], vertical_alignment="center")

    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=90)

    with col_text:
        st.markdown(
            '<div class="brand-row"><div>'
            '<div class="brand-name"><span>She</span>GO Driver Board</div>'
            '<div class="brand-sub">Job tersedia untuk rangkaian pemandu wanita SheGO.</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )


# ============================================================
# PUBLIC DRIVER BOARD
# ============================================================
def render_driver_board():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">SHEGO • JOB BOARD</div>
            <div class="hero-title">Tengok job. Pilih yang sesuai. WhatsApp admin.</div>
            <div class="hero-copy">
                Semua job di bawah telah dibuka oleh admin SheGO. Semak kawasan, tarikh,
                masa dan tambang. Jika berminat, hubungi admin untuk claim. Job hanya
                dianggap milik anda selepas mendapat pengesahan daripada admin.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = load_bookings()
    except Exception as exc:
        st.error(f"Tak dapat baca Google Sheet: {exc}")
        return

    if df.empty:
        st.info("Belum ada job tersedia sekarang.")
        return

    status_col = PUBLIC_COLUMNS["status"]
    fare_col = PUBLIC_COLUMNS["fare"]

    if status_col not in df.columns:
        st.warning(
            "Column 'Status' belum ada dalam Google Sheet. Tambah column Status dan isi 'Open' untuk job yang mahu dipaparkan."
        )
        return

    open_jobs = df[
        df[status_col].astype(str).str.strip().str.casefold() == "open"
    ].copy()

    search_col, refresh_col = st.columns([4, 1], vertical_alignment="bottom")

    with search_col:
        search = st.text_input(
            "Cari kawasan",
            placeholder="Contoh: Ulu Tiram, JB, Senai, Pasir Gudang...",
        ).strip().casefold()

    with refresh_col:
        if st.button("↻ Refresh", use_container_width=True):
            load_bookings.clear()
            st.rerun()

    if search and not open_jobs.empty:
        pickup = open_jobs.get(
            CUSTOMER_COLUMNS["pickup"], pd.Series(index=open_jobs.index, dtype=str)
        ).astype(str).str.casefold()

        destination = open_jobs.get(
            CUSTOMER_COLUMNS["destination"], pd.Series(index=open_jobs.index, dtype=str)
        ).astype(str).str.casefold()

        open_jobs = open_jobs[
            pickup.str.contains(search, regex=False, na=False)
            | destination.str.contains(search, regex=False, na=False)
        ]

    st.markdown(
        f'<span class="job-pill">🚗 {len(open_jobs)} job tersedia</span>',
        unsafe_allow_html=True,
    )
    st.write("")

    if open_jobs.empty:
        st.info("Tiada job tersedia untuk carian ini sekarang.")
        return

    admin_whatsapp = secret_value("ADMIN_WHATSAPP")

    for _, row in open_jobs.iterrows():
        job_id = booking_id_for_row(row)
        pickup = safe_value(row, CUSTOMER_COLUMNS["pickup"])
        destination = safe_value(row, CUSTOMER_COLUMNS["destination"])
        date = safe_value(row, CUSTOMER_COLUMNS["date"])
        pickup_time = safe_value(row, CUSTOMER_COLUMNS["time"])
        pax = safe_value(row, CUSTOMER_COLUMNS["pax"])
        trip_type = safe_value(row, CUSTOMER_COLUMNS["trip_type"])
        baggage = safe_value(row, CUSTOMER_COLUMNS["baggage"], "Tidak dinyatakan")
        notes = safe_value(row, CUSTOMER_COLUMNS["notes"], "Tiada")
        return_time = safe_value(row, CUSTOMER_COLUMNS["return_time"], "-")
        fare = safe_value(row, fare_col, "Belum dinyatakan")

        with st.container(border=True):
            title_col, fare_display_col = st.columns([4, 1], vertical_alignment="top")

            with title_col:
                st.markdown(
                    f'<div class="job-id">{job_id}</div>'
                    '<span class="open-pill">● OPEN</span>',
                    unsafe_allow_html=True,
                )

            with fare_display_col:
                fare_text = (
                    f"RM {fare}"
                    if fare not in ["-", "Belum dinyatakan"]
                    else fare
                )
                st.markdown(
                    f'<div class="fare-box"><div class="fare-label">TAMBANG</div>'
                    f'<div class="fare-value">{fare_text}</div></div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
                <div class="route">
                    <div class="label">PICKUP</div>
                    <div class="route-main">📍 {pickup}</div>
                    <div class="route-arrow">↓</div>
                    <div class="label">DESTINASI</div>
                    <div class="route-main">🏁 {destination}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            info1, info2, info3 = st.columns(3)
            info1.markdown(f"**📅 Tarikh**  \n{date}")
            info2.markdown(f"**🕐 Pickup**  \n{pickup_time}")
            info3.markdown(f"**👥 Penumpang**  \n{pax}")

            info4, info5 = st.columns(2)
            info4.markdown(f"**🚗 Jenis trip**  \n{trip_type}")
            info5.markdown(f"**🧳 Bagasi**  \n{baggage}")

            if return_time != "-":
                st.markdown(f"**↩️ Anggaran masa balik:** {return_time}")

            if notes != "Tiada":
                st.markdown(f"**📝 Nota tempahan:** {notes}")

            st.markdown(
                '<div class="privacy">🔒 Nama dan nombor telefon pelanggan tidak dipaparkan di halaman awam. Maklumat hubungan akan diberikan oleh admin selepas job disahkan.</div>',
                unsafe_allow_html=True,
            )

            message = (
                f"Hi Admin SheGO, saya berminat nak claim job {job_id}.\n\n"
                f"Pickup: {pickup}\n"
                f"Destinasi: {destination}\n"
                f"Tarikh: {date}\n"
                f"Masa: {pickup_time}\n\n"
                "Boleh semak sama ada job ini masih available?"
            )

            if admin_whatsapp:
                wa_url = (
                    f"https://wa.me/{admin_whatsapp}?text={quote(message)}"
                )
                st.link_button(
                    "💬 WhatsApp Admin untuk Claim Job",
                    wa_url,
                    type="primary",
                    use_container_width=True,
                )
            else:
                st.warning(
                    "ADMIN_WHATSAPP belum dimasukkan dalam Streamlit Secrets."
                )

    st.write("")
    st.markdown(
        '<div class="sheet-note">💡 Admin: urus <b>Status</b>, <b>Tambang (RM)</b> dan <b>Booking ID</b> terus dalam Google Sheet. Hanya row dengan Status = <b>Open</b> dipaparkan di sini.</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# APP
# ============================================================
render_brand()
st.write("")
render_driver_board()
