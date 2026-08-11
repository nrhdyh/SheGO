import html
import re
from urllib.parse import quote

import pandas as pd
import streamlit as st


# ============================================================
# SHEGO CONFIG
# ============================================================
SPREADSHEET_ID = "1Gq6boYuQfROpuJXpChvu0nkBtODZ-aXwtK6B6fyddgM"
SHEET_TAB = "Driver Board"
ADMIN_WHATSAPP = "60125057046"
VISIBLE_STATUS = "open"
SHEET_CACHE_TTL = 15
AUTO_REFRESH_INTERVAL = "2m"


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
# LIGHT RESPONSIVE UI
# Desktop = table | Tablet/Phone = cards
# ============================================================
st.markdown(
    """
<style>
:root { color-scheme: light !important; }

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: #fffafb !important;
    color: #1f1b1d !important;
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] {
    background: rgba(255,250,251,.94) !important;
    border-bottom: 1px solid rgba(231,92,137,.08);
    backdrop-filter: blur(12px);
}

.block-container {
    max-width: 1280px;
    padding-top: 1.15rem;
    padding-bottom: 4rem;
}

/* ---------- Brand bar ---------- */
.shego-topbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:16px;
    margin: 2px 0 18px;
}
.brand-wrap {
    display:flex;
    align-items:center;
    gap:12px;
}
.shego-logo {
    width:46px;
    height:46px;
    border-radius:15px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:linear-gradient(135deg,#ea5d8d,#f39ab6);
    color:#fff;
    font-weight:950;
    font-size:20px;
    box-shadow:0 8px 22px rgba(232,92,138,.22);
}
.shego-name {
    font-size:1.5rem;
    font-weight:950;
    line-height:1;
    letter-spacing:-.04em;
    color:#1f1b1d;
}
.shego-name span { color:#e85c8a; }
.shego-sub {
    color:#8d7d83;
    font-size:.8rem;
    margin-top:5px;
    font-weight:650;
}
.sync-pill {
    display:inline-flex;
    align-items:center;
    gap:8px;
    padding:8px 12px;
    border-radius:999px;
    background:#fff;
    color:#5f5056;
    border:1px solid #f0dbe2;
    font-size:.76rem;
    font-weight:800;
    box-shadow:0 5px 16px rgba(98,49,67,.04);
}
.sync-dot {
    width:8px;
    height:8px;
    border-radius:50%;
    background:#22a06b;
    box-shadow:0 0 0 4px rgba(34,160,107,.10);
}

/* ---------- Hero ---------- */
.shego-hero {
    position:relative;
    overflow:hidden;
    border:1px solid #f0dfe5;
    border-radius:26px;
    padding:34px 34px 32px;
    margin-bottom:18px;
    background:
        radial-gradient(circle at 92% 4%, rgba(255,213,228,.95) 0, rgba(255,213,228,.22) 28%, transparent 52%),
        linear-gradient(135deg,#ffffff 0%,#fff9fb 58%,#fff3f7 100%);
    box-shadow:0 16px 40px rgba(93,48,64,.07);
}
.hero-eyebrow {
    display:inline-flex;
    align-items:center;
    gap:7px;
    padding:7px 11px;
    border-radius:999px;
    background:#fff;
    color:#c44872;
    border:1px solid #f1d5df;
    font-size:.73rem;
    font-weight:900;
    letter-spacing:.04em;
    text-transform:uppercase;
}
.shego-hero h1 {
    max-width:780px;
    margin:16px 0 10px;
    color:#1f1b1d;
    font-size:clamp(2.1rem,5vw,3.55rem);
    line-height:1.02;
    letter-spacing:-.055em;
}
.shego-hero p {
    max-width:800px;
    margin:0;
    color:#76676d;
    line-height:1.7;
    font-size:.98rem;
}
.hero-note {
    display:flex;
    flex-wrap:wrap;
    gap:8px;
    margin-top:19px;
}
.hero-chip {
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:7px 10px;
    border-radius:10px;
    background:rgba(255,255,255,.82);
    border:1px solid #f1e3e8;
    color:#6d5f64;
    font-size:.75rem;
    font-weight:750;
}

/* ---------- Stats ---------- */
.stats-grid {
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:12px;
    margin: 0 0 22px;
}
.stat-card {
    position:relative;
    overflow:hidden;
    min-height:96px;
    padding:17px 18px;
    border-radius:18px;
    border:1px solid #eee1e5;
    background:#fff;
    box-shadow:0 6px 20px rgba(76,46,57,.035);
}
.stat-card:after {
    content:"";
    position:absolute;
    right:-16px;
    bottom:-28px;
    width:84px;
    height:84px;
    border-radius:50%;
    background:#fff2f6;
}
.stat-icon {
    font-size:1rem;
    margin-bottom:7px;
}
.stat-label {
    color:#96858b;
    font-size:.7rem;
    font-weight:850;
    letter-spacing:.055em;
    text-transform:uppercase;
}
.stat-value {
    position:relative;
    z-index:1;
    margin-top:3px;
    color:#241f21;
    font-size:1.45rem;
    font-weight:950;
    letter-spacing:-.025em;
}

/* ---------- Section headings ---------- */
.section-head {
    display:flex;
    align-items:flex-end;
    justify-content:space-between;
    gap:14px;
    flex-wrap:wrap;
    margin: 7px 0 11px;
}
.section-title {
    color:#251f21;
    font-size:1.12rem;
    font-weight:950;
    letter-spacing:-.02em;
}
.section-sub {
    color:#928188;
    font-size:.8rem;
    margin-top:3px;
}

/* ---------- Native Streamlit widgets ---------- */
label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
    color:#44393d !important;
    font-weight:750 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:rgba(255,255,255,.92) !important;
    border:1px solid #eedfe4 !important;
    border-radius:20px !important;
    box-shadow:0 8px 25px rgba(77,42,55,.035);
}

[data-testid="stTextInput"] div[data-baseweb="input"],
[data-testid="stTextInput"] div[data-baseweb="input"] > div,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
    background:#fff !important;
    border-color:#e5d9dd !important;
    color:#221d1f !important;
    box-shadow:none !important;
    border-radius:11px !important;
}

[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] input,
[data-testid="stMultiSelect"] input,
[data-testid="stSelectbox"] span,
[data-testid="stMultiSelect"] span {
    color:#221d1f !important;
    -webkit-text-fill-color:#221d1f !important;
}

[data-testid="stTextInput"] input::placeholder {
    color:#a5979c !important;
    -webkit-text-fill-color:#a5979c !important;
}

[data-baseweb="tag"] {
    background:#fff0f5 !important;
    border:1px solid #f3ccd9 !important;
    color:#b83e67 !important;
    border-radius:8px !important;
}
[data-baseweb="tag"] span, [data-baseweb="tag"] div {
    color:#b83e67 !important;
    -webkit-text-fill-color:#b83e67 !important;
}

div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
    background:#fff !important;
    color:#251f21 !important;
}
li[role="option"], div[role="option"] {
    background:#fff !important;
    color:#251f21 !important;
}
li[role="option"]:hover, div[role="option"]:hover,
li[role="option"][aria-selected="true"], div[role="option"][aria-selected="true"] {
    background:#fff1f5 !important;
    color:#b83e67 !important;
}

.stButton > button {
    min-height:42px;
    border-radius:11px !important;
    border:1px solid #e3d7db !important;
    background:#fff !important;
    color:#43373c !important;
    font-weight:850 !important;
    transition:.15s ease !important;
}
.stButton > button:hover {
    border-color:#e85c8a !important;
    color:#c84672 !important;
    transform:translateY(-1px);
}

/* ---------- Result bar ---------- */
.result-bar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin:12px 0;
    flex-wrap:wrap;
}
.result-count {
    display:inline-flex;
    align-items:center;
    gap:7px;
    padding:8px 12px;
    border-radius:999px;
    background:#fff0f5;
    color:#bc426b;
    border:1px solid #f1cfd9;
    font-size:.8rem;
    font-weight:900;
}
.result-note {
    color:#9a8a90;
    font-size:.76rem;
}

/* ---------- Desktop table ---------- */
.desktop-view { display:block; }
.mobile-view { display:none; }
.table-shell {
    width:100%;
    overflow-x:auto;
    border:1px solid #eadde2;
    border-radius:20px;
    background:#fff;
    box-shadow:0 10px 30px rgba(72,43,53,.045);
}
.job-table {
    width:100%;
    min-width:1040px;
    border-collapse:separate;
    border-spacing:0;
    background:#fff;
}
.job-table th {
    position:sticky;
    top:0;
    z-index:1;
    padding:13px 14px;
    text-align:left;
    background:#fff8fa;
    border-bottom:1px solid #eadde2;
    color:#806f75;
    font-size:.7rem;
    font-weight:900;
    letter-spacing:.035em;
    text-transform:uppercase;
    white-space:nowrap;
}
.job-table td {
    padding:14px;
    border-bottom:1px solid #f1eaed;
    color:#2d2729;
    font-size:.82rem;
    vertical-align:middle;
}
.job-table tr:last-child td { border-bottom:none; }
.job-table tbody tr { transition:.15s ease; }
.job-table tbody tr:hover { background:#fff9fb; }
.booking-cell {
    font-weight:950;
    color:#2b2427;
    white-space:nowrap;
}
.route-cell {
    min-width:230px;
    font-weight:720;
    line-height:1.45;
}
.route-arrow-inline {
    color:#e17b9d;
    margin:0 7px;
}
.fare-cell {
    color:#bb3f69;
    font-weight:950;
    white-space:nowrap;
}
.status-pill {
    display:inline-flex;
    align-items:center;
    gap:5px;
    padding:5px 8px;
    border-radius:999px;
    background:#eef9f4;
    color:#18815e;
    border:1px solid #d4eee2;
    font-size:.66rem;
    font-weight:900;
    white-space:nowrap;
}
.claim-link {
    display:inline-flex;
    align-items:center;
    justify-content:center;
    padding:9px 12px;
    border-radius:10px;
    background:linear-gradient(135deg,#e85c8a,#df4f80);
    color:white !important;
    text-decoration:none !important;
    font-size:.73rem;
    font-weight:900;
    white-space:nowrap;
    box-shadow:0 5px 14px rgba(232,92,138,.18);
    transition:.15s ease;
}
.claim-link:hover {
    transform:translateY(-1px);
    box-shadow:0 7px 18px rgba(232,92,138,.24);
}

/* ---------- Tablet / phone cards ---------- */
.mobile-cards {
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:14px;
}
.job-card {
    position:relative;
    overflow:hidden;
    border:1px solid #eadde2;
    border-radius:20px;
    background:#fff;
    padding:17px;
    box-shadow:0 8px 24px rgba(73,43,54,.045);
}
.job-card:before {
    content:"";
    position:absolute;
    left:0;
    top:0;
    bottom:0;
    width:4px;
    background:linear-gradient(180deg,#e85c8a,#f3aac0);
}
.card-head {
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:10px;
    margin-bottom:13px;
}
.card-kicker {
    color:#a28f96;
    font-size:.61rem;
    font-weight:900;
    letter-spacing:.07em;
    text-transform:uppercase;
    margin-bottom:3px;
}
.card-booking {
    color:#241f21;
    font-size:1.02rem;
    font-weight:950;
}
.card-fare {
    color:#bd426b;
    font-size:1.08rem;
    font-weight:950;
    text-align:right;
}
.card-route {
    position:relative;
    padding:13px 13px 13px 15px;
    background:#fff9fb;
    border:1px solid #f0e4e8;
    border-radius:14px;
    margin-bottom:12px;
}
.card-label {
    color:#9b8990;
    font-size:.62rem;
    font-weight:900;
    letter-spacing:.06em;
    text-transform:uppercase;
}
.card-place {
    color:#2c2528;
    font-size:.9rem;
    font-weight:760;
    line-height:1.4;
    margin-top:2px;
}
.card-route-arrow {
    color:#df7095;
    font-weight:950;
    margin:5px 0;
    padding-left:2px;
}
.card-meta {
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:8px;
    margin-bottom:10px;
}
.meta-item {
    border:1px solid #f0e7ea;
    border-radius:12px;
    padding:10px;
    background:#fff;
}
.meta-name {
    color:#a08e94;
    font-size:.61rem;
    font-weight:900;
    text-transform:uppercase;
    letter-spacing:.04em;
}
.meta-value {
    margin-top:3px;
    color:#352d30;
    font-size:.8rem;
    font-weight:720;
    overflow-wrap:anywhere;
}
.card-extra {
    color:#73656a;
    background:#fffafa;
    border:1px dashed #eadce1;
    border-radius:11px;
    padding:9px 10px;
    font-size:.75rem;
    line-height:1.55;
    margin:9px 0 12px;
}
.card-claim {
    display:flex;
    width:100%;
    box-sizing:border-box;
    align-items:center;
    justify-content:center;
    padding:11px 12px;
    border-radius:12px;
    background:linear-gradient(135deg,#e85c8a,#df4f80);
    color:white !important;
    text-decoration:none !important;
    font-size:.79rem;
    font-weight:900;
    box-shadow:0 6px 16px rgba(232,92,138,.18);
}

.info-strip {
    margin-top:16px;
    display:flex;
    gap:8px;
    align-items:flex-start;
    padding:12px 14px;
    border:1px solid #eee0e5;
    border-radius:14px;
    background:#fff;
    color:#77686e;
    font-size:.77rem;
    line-height:1.55;
}

@media (max-width:1024px) {
    .block-container {
        padding-left:1rem;
        padding-right:1rem;
        padding-top:.8rem;
    }
    .desktop-view { display:none !important; }
    .mobile-view { display:block !important; }
    .shego-hero { padding:27px 24px; }
}

@media (max-width:760px) {
    .sync-pill { display:none; }
    .stats-grid { grid-template-columns:1fr 1fr 1fr; gap:8px; }
    .stat-card { min-height:82px; padding:13px 12px; border-radius:15px; }
    .stat-value { font-size:1.18rem; }
    .stat-label { font-size:.59rem; }
    .mobile-cards { grid-template-columns:1fr; }
    .shego-hero { padding:22px 18px; border-radius:20px; }
    .shego-hero h1 { font-size:2rem; }
    .hero-note { gap:6px; }
    .hero-chip { font-size:.69rem; }
}

@media (max-width:430px) {
    .block-container { padding-left:.75rem; padding-right:.75rem; }
    .shego-logo { width:42px; height:42px; border-radius:13px; }
    .shego-name { font-size:1.35rem; }
    .stats-grid { grid-template-columns:1fr; }
    .stat-card { min-height:auto; }
    .card-meta { grid-template-columns:repeat(2,minmax(0,1fr)); }
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# GOOGLE SHEET
# ============================================================
def sheet_csv_url():
    return (
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq"
        f"?tqx=out:csv&sheet={quote(SHEET_TAB)}"
    )


@st.cache_data(ttl=SHEET_CACHE_TTL, show_spinner=False)
def load_jobs():
    try:
        df = pd.read_csv(
            sheet_csv_url(),
            dtype=str,
            keep_default_na=False,
            skip_blank_lines=False,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Tak dapat baca tab '{SHEET_TAB}'. "
            "Pastikan nama tab betul dan Google Sheet boleh dibaca."
        ) from exc

    df.columns = [str(col).strip() for col in df.columns]
    data_columns = list(df.columns)
    df["_source_row"] = range(2, len(df) + 2)

    if data_columns:
        non_empty = (
            df[data_columns]
            .astype(str)
            .apply(lambda col: col.str.strip().ne(""))
            .any(axis=1)
        )
        df = df.loc[non_empty].copy()

    return df


# ============================================================
# COLUMN DETECTION
# ============================================================
COLUMN_ALIASES = {
    "booking_id": [
        "Booking ID", "Job ID", "ID Tempahan",
        "No Tempahan", "No. Tempahan", "ID",
    ],
    "status": [
        "Status", "Status Job", "Status Tempahan", "Booking Status",
    ],
    "pickup": [
        "Pickup", "Lokasi Pickup", "Lokasi Ambil",
        "Lokasi Ambil (Pickup)", "Pickup Location", "Dari",
    ],
    "destination": [
        "Destinasi", "Destination", "Lokasi Destinasi",
        "Drop Off", "Drop-off", "Ke",
    ],
    "date": [
        "Tarikh", "Tarikh Perjalanan", "Tarikh Tempahan", "Trip Date", "Date",
    ],
    "time": [
        "Masa", "Masa Pickup", "Masa Ambil", "Waktu Pickup", "Pickup Time", "Time",
    ],
    "pax": [
        "Penumpang", "Bilangan Penumpang", "Jumlah Penumpang", "Pax", "No. of Passengers",
    ],
    "trip_type": [
        "Jenis Trip", "Jenis Perjalanan", "Trip Type", "Jenis Tempahan",
    ],
    "baggage": [
        "Bagasi", "Maklumat Bagasi", "Luggage",
    ],
    "notes": [
        "Nota", "Nota Tambahan", "Catatan", "Remarks", "Remark", "Additional Notes",
    ],
    "fare": [
        "Tambang (RM)", "Tambang", "Harga", "Fare", "Fare (RM)", "Price",
    ],
}


def normalize_header(value):
    value = str(value).strip().casefold()
    value = re.sub(r"[\s_\-()/.:]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def find_column(df, key):
    normalized = {
        normalize_header(col): col
        for col in df.columns
        if not str(col).startswith("_")
    }

    for alias in COLUMN_ALIASES[key]:
        alias_n = normalize_header(alias)
        if alias_n in normalized:
            return normalized[alias_n]

    for alias in COLUMN_ALIASES[key]:
        alias_n = normalize_header(alias)
        if len(alias_n) < 4:
            continue

        for col_n, original in normalized.items():
            if alias_n in col_n or col_n in alias_n:
                return original

    return None


# ============================================================
# HELPERS
# ============================================================
def clean_text(value, fallback="-"):
    if pd.isna(value):
        return fallback

    text = str(value).strip()
    if not text or text.casefold() in {"nan", "none", "null"}:
        return fallback

    return text


def get_value(row, column, fallback="-"):
    if not column:
        return fallback
    return clean_text(row.get(column, ""), fallback)


def unique_values(df, column):
    if not column or df.empty:
        return []

    values = df[column].fillna("").astype(str).str.strip()
    values = values[
        ~values.str.casefold().isin({"", "nan", "none", "null", "-"})
    ]

    return sorted(values.unique().tolist(), key=lambda x: x.casefold())


def fare_to_number(value):
    text = clean_text(value, "")
    if not text:
        return None

    cleaned = text.replace(",", "")
    cleaned = re.sub(r"[^0-9.\-]", "", cleaned)

    if cleaned in {"", "-", ".", "-."}:
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


def display_fare(value):
    number = fare_to_number(value)
    if number is None:
        return clean_text(value, "Semak admin")
    return f"RM {number:,.2f}"


def display_date(value):
    text = clean_text(value, "-")
    match = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T].*)?", text)

    if not match:
        return text

    year, month, day = match.groups()
    try:
        timestamp = pd.Timestamp(
            year=int(year),
            month=int(month),
            day=int(day),
        )
    except ValueError:
        return text

    return timestamp.strftime("%d/%m/%Y")


def display_time(value):
    text = clean_text(value, "-")
    match = re.fullmatch(r"(\d{1,2}):(\d{2}):00", text)
    if match:
        return f"{int(match.group(1)):02d}:{match.group(2)}"
    return text


def fallback_booking_id(source_row):
    try:
        row_number = int(source_row)
    except (TypeError, ValueError):
        return "SG-TEMP"
    return f"SG-R{row_number:04d}"


def booking_display(row, booking_column):
    booking_id = get_value(row, booking_column, "")
    if booking_id:
        return booking_id
    return fallback_booking_id(row.get("_source_row"))


def safe_text(value):
    return html.escape(clean_text(value, "-"))


def reset_filters():
    for key in (
        "search_location",
        "filter_dates",
        "filter_trip_types",
        "filter_pax",
        "sort_option",
    ):
        st.session_state.pop(key, None)


# ============================================================
# HEADER
# ============================================================
st.markdown(
    '<div class="shego-topbar">'
    '<div class="brand-wrap">'
    '<div class="shego-logo">S</div>'
    '<div><div class="shego-name"><span>She</span>GO</div>'
    '<div class="shego-sub">Driver Job Board • Johor</div></div>'
    '</div>'
    '<div class="sync-pill"><span class="sync-dot"></span>Auto Sync • setiap 2 minit</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<section class="shego-hero">'
    '<span class="hero-eyebrow">🚗 Job Board Pemandu</span>'
    '<h1>Pilih trip yang sesuai dengan masa dan kawasan anda.</h1>'
    '<p>Semua job di bawah masih berstatus <b>Open</b>. '
    'Tekan <b>Mohon Claim</b> untuk hubungi admin melalui WhatsApp. '
    'Job hanya menjadi milik pemandu selepas admin mengesahkan dan menukar status kepada <b>Assigned</b>.</p>'
    '<div class="hero-note">'
    '<span class="hero-chip">📍 Johor</span>'
    '<span class="hero-chip">🔄 Auto update</span>'
    '<span class="hero-chip">🔒 Maklumat pelanggan dilindungi</span>'
    '</div>'
    '</section>',
    unsafe_allow_html=True,
)


# ============================================================
# LIVE DATA BOARD
# Auto refresh every 2 minutes. Filters remain in session_state.
# ============================================================
@st.fragment(run_every=AUTO_REFRESH_INTERVAL)
def live_board():
    st.caption("🟢 Data diselaraskan automatik setiap 2 minit • Refresh manual masih tersedia")

    try:
        jobs = load_jobs()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    if jobs.empty:
        st.info("Google Sheet belum mempunyai data job.")
        st.stop()

    cols = {key: find_column(jobs, key) for key in COLUMN_ALIASES}

    if not cols["status"]:
        st.error(
            "Column **Status** tidak dijumpai. "
            "Pastikan tab Driver Board mempunyai column bernama `Status`."
        )
        st.stop()

    if not cols["pickup"] or not cols["destination"]:
        st.error("Column Pickup atau Destinasi tidak dapat dikesan.")
        with st.expander("Lihat column Google Sheet"):
            st.write([
                col for col in jobs.columns
                if not str(col).startswith("_")
            ])
        st.stop()

    jobs["_booking_display"] = jobs.apply(
        lambda row: booking_display(row, cols["booking_id"]),
        axis=1,
    )

    normalized_status = (
        jobs[cols["status"]]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    open_jobs = jobs[normalized_status.eq(VISIBLE_STATUS)].copy()

    if open_jobs.empty:
        st.success("Tiada job Open buat masa ini.")
        st.stop()


    # ============================================================
    # QUICK SUMMARY
    # ============================================================
    active_dates = len(unique_values(open_jobs, cols["date"])) if cols["date"] else 0
    trip_type_count = len(unique_values(open_jobs, cols["trip_type"])) if cols["trip_type"] else 0

    st.markdown(
        '<div class="stats-grid">'
        f'<div class="stat-card"><div class="stat-icon">🚘</div><div class="stat-label">Job Open</div><div class="stat-value">{len(open_jobs)}</div></div>'
        f'<div class="stat-card"><div class="stat-icon">📅</div><div class="stat-label">Tarikh Aktif</div><div class="stat-value">{active_dates if active_dates else "-"}</div></div>'
        f'<div class="stat-card"><div class="stat-icon">🛣️</div><div class="stat-label">Jenis Trip</div><div class="stat-value">{trip_type_count if trip_type_count else "-"}</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )


    # ============================================================
    # FILTERS
    # ============================================================
    st.markdown(
        '<div class="section-head"><div>'
        '<div class="section-title">🔎 Cari Job</div>'
        '<div class="section-sub">Cari lokasi atau Booking ID, kemudian tapis mengikut keperluan anda.</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        left, right = st.columns(2)

        with left:
            location_search = st.text_input(
                "Pickup / Destinasi / Booking ID",
                placeholder="Contoh: Ulu Tiram, Senai, SG-001...",
                key="search_location",
            ).strip().casefold()

        with right:
            date_options = unique_values(open_jobs, cols["date"])
            selected_dates = (
                st.multiselect(
                    "Tarikh",
                    options=date_options,
                    placeholder="Semua tarikh",
                    key="filter_dates",
                )
                if date_options else []
            )

        left2, right2 = st.columns(2)

        with left2:
            trip_options = unique_values(open_jobs, cols["trip_type"])
            selected_trip_types = (
                st.multiselect(
                    "Jenis Trip",
                    options=trip_options,
                    placeholder="Semua jenis trip",
                    key="filter_trip_types",
                )
                if trip_options else []
            )

        with right2:
            pax_options = unique_values(open_jobs, cols["pax"])
            selected_pax = (
                st.multiselect(
                    "Penumpang",
                    options=pax_options,
                    placeholder="Semua",
                    key="filter_pax",
                )
                if pax_options else []
            )

        sort_option = st.selectbox(
            "Susun Job",
            options=[
                "Asal dari Google Sheet",
                "Tambang tertinggi",
                "Tambang terendah",
            ],
            key="sort_option",
        )

        b1, b2 = st.columns(2)
        with b1:
            if st.button("↻ Refresh Data", use_container_width=True):
                load_jobs.clear()
                st.rerun()

        with b2:
            if st.button(
                "Reset Filter",
                use_container_width=True,
                on_click=reset_filters,
            ):
                st.rerun()


    # ============================================================
    # APPLY FILTERS
    # ============================================================
    filtered = open_jobs.copy()

    if location_search:
        pickup_series = filtered[cols["pickup"]].fillna("").astype(str).str.casefold()
        destination_series = filtered[cols["destination"]].fillna("").astype(str).str.casefold()
        booking_series = filtered["_booking_display"].fillna("").astype(str).str.casefold()

        filtered = filtered[
            pickup_series.str.contains(location_search, regex=False, na=False)
            | destination_series.str.contains(location_search, regex=False, na=False)
            | booking_series.str.contains(location_search, regex=False, na=False)
        ]

    if selected_dates and cols["date"]:
        filtered = filtered[
            filtered[cols["date"]].astype(str).str.strip().isin(selected_dates)
        ]

    if selected_trip_types and cols["trip_type"]:
        filtered = filtered[
            filtered[cols["trip_type"]].astype(str).str.strip().isin(selected_trip_types)
        ]

    if selected_pax and cols["pax"]:
        filtered = filtered[
            filtered[cols["pax"]].astype(str).str.strip().isin(selected_pax)
        ]

    if cols["fare"] and sort_option != "Asal dari Google Sheet":
        filtered = filtered.copy()
        filtered["_fare_num"] = filtered[cols["fare"]].apply(fare_to_number)
        filtered = filtered.sort_values(
            "_fare_num",
            ascending=(sort_option == "Tambang terendah"),
            na_position="last",
            kind="stable",
        ).drop(columns=["_fare_num"])
    else:
        filtered = filtered.sort_values("_source_row", ascending=True, kind="stable")


    # ============================================================
    # RESULT HEADER
    # ============================================================
    st.markdown(
        '<div class="section-head" style="margin-top:22px"><div>'
        '<div class="section-title">Available Trips</div>'
        '<div class="section-sub">Pilih job yang sesuai dan hantar permohonan claim kepada admin.</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="result-bar">'
        f'<div class="result-count">🚗 {len(filtered)} job sepadan</div>'
        '<div class="result-note">Desktop: table • Tablet/telefon: card view automatik</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if filtered.empty:
        st.warning("Tiada job yang sepadan dengan filter anda.")
        st.stop()


    # ============================================================
    # BUILD RESPONSIVE TABLE + CARDS
    # Important: generated as compact HTML to avoid Markdown code blocks
    # ============================================================
    desktop_rows = []
    mobile_cards = []

    for _, row in filtered.iterrows():
        booking_id = clean_text(
            row.get("_booking_display", ""),
            fallback_booking_id(row.get("_source_row")),
        )

        pickup = get_value(row, cols["pickup"], "Tidak dinyatakan")
        destination = get_value(row, cols["destination"], "Tidak dinyatakan")
        trip_date = display_date(get_value(row, cols["date"], "-"))
        pickup_time = display_time(get_value(row, cols["time"], "-"))
        pax = get_value(row, cols["pax"], "-")
        trip_type = get_value(row, cols["trip_type"], "-")
        baggage = get_value(row, cols["baggage"], "-")
        notes = get_value(row, cols["notes"], "-")
        fare = get_value(row, cols["fare"], "Semak admin")
        fare_display = display_fare(fare)

        whatsapp_message = (
            f"Hi Admin SheGO, saya nak mohon claim job {booking_id}.\n\n"
            f"📍 Pickup: {pickup}\n"
            f"🏁 Destinasi: {destination}\n"
            f"📅 Tarikh: {trip_date}\n"
            f"🕐 Masa: {pickup_time}\n"
            f"👥 Penumpang: {pax}\n"
            f"🚗 Jenis trip: {trip_type}\n"
            f"🧳 Bagasi: {baggage}\n"
            f"📝 Nota: {notes}\n"
            f"💰 Tambang: {fare_display}\n\n"
            "Boleh semak sama ada job ini masih Open dan confirmkan kepada saya?"
        )

        whatsapp_url = (
            f"https://wa.me/{ADMIN_WHATSAPP}"
            f"?text={quote(whatsapp_message)}"
        )
        safe_url = html.escape(whatsapp_url, quote=True)

        bid = safe_text(booking_id)
        pick = safe_text(pickup)
        dest = safe_text(destination)
        date_txt = safe_text(trip_date)
        time_txt = safe_text(pickup_time)
        pax_txt = safe_text(pax)
        type_txt = safe_text(trip_type)
        bag_txt = safe_text(baggage)
        note_txt = safe_text(notes)
        fare_txt = safe_text(fare_display)

        desktop_rows.append(
            '<tr>'
            f'<td class="booking-cell">{bid}</td>'
            '<td><span class="status-pill">● OPEN</span></td>'
            f'<td class="route-cell">📍 {pick}<span class="route-arrow-inline">→</span>🏁 {dest}</td>'
            f'<td>{date_txt}<br><span style="color:#888;font-size:.75rem">{time_txt}</span></td>'
            f'<td>{pax_txt}</td>'
            f'<td>{type_txt}</td>'
            f'<td>{bag_txt}</td>'
            f'<td class="fare-cell">{fare_txt}</td>'
            f'<td><a class="claim-link" href="{safe_url}" target="_blank" rel="noopener noreferrer">💬 Claim</a></td>'
            '</tr>'
        )

        extra_parts = []
        if baggage not in {"", "-"}:
            extra_parts.append(f"🧳 Bagasi: <b>{bag_txt}</b>")
        if notes not in {"", "-"}:
            extra_parts.append(f"📝 Nota: {note_txt}")

        extra_html = "<br>".join(extra_parts) if extra_parts else "Tiada nota tambahan."

        mobile_cards.append(
            '<div class="job-card">'
            '<div class="card-head">'
            f'<div><div class="card-kicker">Available Job</div><div class="card-booking">{bid}</div><div style="margin-top:6px"><span class="status-pill">● OPEN</span></div></div>'
            f'<div class="card-fare">{fare_txt}</div>'
            '</div>'
            '<div class="card-route">'
            '<div class="card-label">Pickup</div>'
            f'<div class="card-place">📍 {pick}</div>'
            '<div class="card-route-arrow">↓</div>'
            '<div class="card-label">Destinasi</div>'
            f'<div class="card-place">🏁 {dest}</div>'
            '</div>'
            '<div class="card-meta">'
            f'<div class="meta-item"><div class="meta-name">Tarikh</div><div class="meta-value">📅 {date_txt}</div></div>'
            f'<div class="meta-item"><div class="meta-name">Masa</div><div class="meta-value">🕐 {time_txt}</div></div>'
            f'<div class="meta-item"><div class="meta-name">Penumpang</div><div class="meta-value">👥 {pax_txt}</div></div>'
            f'<div class="meta-item"><div class="meta-name">Jenis Trip</div><div class="meta-value">🚗 {type_txt}</div></div>'
            '</div>'
            f'<div class="card-extra">{extra_html}</div>'
            f'<a class="card-claim" href="{safe_url}" target="_blank" rel="noopener noreferrer">💬 Mohon Claim di WhatsApp</a>'
            '</div>'
        )


    desktop_html = (
        '<div class="desktop-view"><div class="table-shell"><table class="job-table">'
        '<thead><tr>'
        '<th>Booking ID</th><th>Status</th><th>Route</th><th>Tarikh / Masa</th>'
        '<th>Pax</th><th>Jenis Trip</th><th>Bagasi</th><th>Tambang</th><th>Tindakan</th>'
        '</tr></thead><tbody>'
        + "".join(desktop_rows)
        + '</tbody></table></div></div>'
    )

    mobile_html = (
        '<div class="mobile-view"><div class="mobile-cards">'
        + "".join(mobile_cards)
        + '</div></div>'
    )

    st.markdown(desktop_html + mobile_html, unsafe_allow_html=True)


    # ============================================================
    # FOOTER
    # ============================================================
    st.markdown(
        '<div class="info-strip">🔒 <div><b>Privasi pelanggan</b><br>'
        'Nama dan nombor telefon pelanggan tidak dipaparkan pada Driver Board. '
        'Maklumat tersebut hanya diberikan selepas admin mengesahkan pemandu.</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="info-strip">ℹ️ <div><b>Flow status</b><br>'
        'Open → Assigned → Completed. Status Cancelled digunakan apabila tempahan dibatalkan.</div></div>',
        unsafe_allow_html=True,
    )



live_board()
