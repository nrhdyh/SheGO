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

# Admin WhatsApp: 012-5057046
ADMIN_WHATSAPP = "60125057046"

# Google Sheet dropdown:
# Open | Assigned | Completed | Cancelled
VISIBLE_STATUS = "open"


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
# WHITE RESPONSIVE UI
# ============================================================
st.markdown(
    """
    <style>
    :root { color-scheme: light !important; }

    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background:#ffffff !important;
        color:#171717 !important;
    }

    #MainMenu, footer { visibility:hidden; }

    header[data-testid="stHeader"] {
        background:rgba(255,255,255,.96) !important;
        border-bottom:1px solid #efefef;
        backdrop-filter:blur(10px);
    }

    .block-container {
        max-width:1220px;
        padding-top:1.15rem;
        padding-bottom:4rem;
    }

    /* ---------- BRAND ---------- */
    .brandbar {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:16px;
        margin:4px 0 20px;
    }

    .brand-left {
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
        font-size:21px;
        font-weight:900;
        background:linear-gradient(135deg,#e85c8a,#f08caf);
        box-shadow:0 9px 24px rgba(232,92,138,.19);
    }

    .brand-name {
        color:#171717;
        font-size:1.55rem;
        font-weight:900;
        line-height:1;
        letter-spacing:-.045em;
    }

    .brand-name span { color:#e85c8a; }

    .brand-sub {
        margin-top:5px;
        color:#777;
        font-size:.82rem;
    }

    .live-pill {
        display:inline-flex;
        align-items:center;
        gap:7px;
        padding:7px 11px;
        border-radius:999px;
        color:#147b58;
        background:#effaf5;
        border:1px solid #d7eee3;
        font-size:.75rem;
        font-weight:850;
    }

    .live-dot {
        width:7px;
        height:7px;
        border-radius:50%;
        background:#1b9b69;
    }

    /* ---------- HERO ---------- */
    .hero {
        padding:32px;
        border:1px solid #ececec;
        border-radius:26px;
        background:
            radial-gradient(circle at 94% 10%, #ffe8f0 0, transparent 24%),
            #ffffff;
        box-shadow:0 12px 34px rgba(0,0,0,.045);
        margin-bottom:22px;
        overflow:hidden;
    }

    .hero-badge {
        display:inline-flex;
        align-items:center;
        gap:7px;
        padding:7px 12px;
        border-radius:999px;
        color:#c84672;
        background:#fff3f7;
        border:1px solid #f2d6df;
        font-size:.76rem;
        font-weight:850;
        letter-spacing:.06em;
    }

    .hero h1 {
        max-width:780px;
        margin:16px 0 11px;
        color:#171717;
        font-size:clamp(2.05rem,5vw,3.65rem);
        line-height:1.03;
        letter-spacing:-.055em;
    }

    .hero p {
        max-width:850px;
        margin:0;
        color:#646464;
        line-height:1.75;
        font-size:1rem;
    }

    /* ---------- MINI STATS ---------- */
    .stats {
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:12px;
        margin:0 0 24px;
    }

    .stat {
        padding:16px 18px;
        border:1px solid #ededed;
        border-radius:18px;
        background:#fff;
    }

    .stat-label {
        color:#888;
        font-size:.75rem;
        font-weight:800;
        letter-spacing:.04em;
        text-transform:uppercase;
    }

    .stat-value {
        margin-top:5px;
        color:#171717;
        font-size:1.15rem;
        font-weight:900;
    }

    /* ---------- SECTION ---------- */
    .section-title {
        margin:8px 0 3px;
        color:#171717;
        font-size:1.08rem;
        font-weight:900;
    }

    .section-sub {
        margin-bottom:12px;
        color:#777;
        font-size:.84rem;
    }

    /* ---------- FORCE ALL STREAMLIT FILTERS TO LIGHT THEME ---------- */
    label,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {
        color:#262626 !important;
    }

    /* Text input */
    [data-testid="stTextInput"] div[data-baseweb="input"],
    [data-testid="stTextInput"] div[data-baseweb="input"] > div,
    [data-testid="stTextInput"] input,
    div[data-baseweb="base-input"] {
        background-color:#ffffff !important;
        color:#171717 !important;
        border-color:#dcdcdc !important;
    }

    [data-testid="stTextInput"] input {
        -webkit-text-fill-color:#171717 !important;
        caret-color:#e85c8a !important;
    }

    [data-testid="stTextInput"] input::placeholder {
        color:#999999 !important;
        -webkit-text-fill-color:#999999 !important;
        opacity:1 !important;
    }

    /* Selectbox + Multiselect outer shell */
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div {
        background-color:#ffffff !important;
        color:#171717 !important;
        border-color:#dcdcdc !important;
        box-shadow:none !important;
    }

    /* Text inside select/multiselect */
    [data-testid="stSelectbox"] div[data-baseweb="select"] span,
    [data-testid="stSelectbox"] div[data-baseweb="select"] div,
    [data-testid="stSelectbox"] div[data-baseweb="select"] input,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] span,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] input {
        color:#171717 !important;
        -webkit-text-fill-color:#171717 !important;
    }

    /* Arrow / clear icons */
    [data-testid="stSelectbox"] svg,
    [data-testid="stMultiSelect"] svg,
    div[data-baseweb="select"] svg {
        fill:#666666 !important;
        color:#666666 !important;
    }

    /* Selected multiselect chips */
    [data-baseweb="tag"] {
        background-color:#fde8ef !important;
        border:1px solid #f5cad8 !important;
        color:#b93e68 !important;
    }

    [data-baseweb="tag"] span,
    [data-baseweb="tag"] div {
        color:#b93e68 !important;
        -webkit-text-fill-color:#b93e68 !important;
    }

    [data-baseweb="tag"] svg {
        fill:#b93e68 !important;
        color:#b93e68 !important;
    }

    /* Dropdown menu/popover */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"],
    [data-baseweb="popover"] > div {
        background-color:#ffffff !important;
        color:#171717 !important;
        border-color:#e5e5e5 !important;
    }

    li[role="option"],
    div[role="option"] {
        background-color:#ffffff !important;
        color:#171717 !important;
        -webkit-text-fill-color:#171717 !important;
    }

    li[role="option"]:hover,
    div[role="option"]:hover,
    li[role="option"][aria-selected="true"],
    div[role="option"][aria-selected="true"] {
        background-color:#fff3f7 !important;
        color:#b93e68 !important;
    }

    /* Ensure filter widgets don't inherit dark system theme */
    [data-testid="stSelectbox"],
    [data-testid="stMultiSelect"],
    [data-testid="stTextInput"] {
        color-scheme:light !important;
    }

    /* Sorting now uses a selectbox for cleaner cross-version rendering. */

    /* ---------- FILTER BOX ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:#fff !important;
        border:1px solid #ececec !important;
        border-radius:20px !important;
        box-shadow:0 6px 20px rgba(0,0,0,.025);
    }

    .stButton > button {
        min-height:43px;
        border-radius:12px !important;
        border:1px solid #e1e1e1 !important;
        background:#fff !important;
        color:#171717 !important;
        font-weight:800 !important;
    }

    .stButton > button:hover {
        border-color:#e85c8a !important;
        color:#c84672 !important;
    }

    /* ---------- RESULT ---------- */
    .result-row {
        display:flex;
        align-items:center;
        justify-content:space-between;
        flex-wrap:wrap;
        gap:10px;
        margin:18px 0 13px;
    }

    .result-pill {
        display:inline-flex;
        align-items:center;
        gap:8px;
        padding:8px 13px;
        border-radius:999px;
        color:#c84672;
        background:#fff3f7;
        border:1px solid #f2d6df;
        font-size:.84rem;
        font-weight:850;
    }

    .result-note {
        color:#858585;
        font-size:.8rem;
    }

    /* ---------- DESKTOP TABLE ---------- */
    .table-wrap {
        width:100%;
        overflow-x:auto;
        border:1px solid #e8e8e8;
        border-radius:18px;
        background:#fff;
        box-shadow:0 7px 24px rgba(0,0,0,.03);
    }

    .job-table {
        width:100%;
        min-width:1320px;
        border-collapse:collapse;
        color:#171717;
        background:#fff;
    }

    .job-table th {
        padding:13px 14px;
        background:#fafafa;
        color:#5b5b5b;
        border-bottom:1px solid #e8e8e8;
        text-align:left;
        font-size:.75rem;
        font-weight:850;
        white-space:nowrap;
    }

    .job-table td {
        padding:14px;
        border-bottom:1px solid #eeeeee;
        vertical-align:middle;
        color:#222;
        font-size:.86rem;
    }

    .job-table tr:last-child td { border-bottom:none; }
    .job-table tbody tr:hover { background:#fffafb; }

    .booking-id {
        font-weight:900;
        white-space:nowrap;
    }

    .status-open {
        display:inline-flex;
        align-items:center;
        gap:5px;
        padding:5px 9px;
        border-radius:999px;
        color:#147b58;
        background:#edf9f3;
        border:1px solid #d6eee1;
        font-size:.7rem;
        font-weight:850;
        white-space:nowrap;
    }

    .route-cell {
        min-width:165px;
        font-weight:700;
    }

    .fare {
        white-space:nowrap;
        font-weight:900;
    }

    .claim-btn {
        display:inline-flex;
        align-items:center;
        justify-content:center;
        padding:9px 12px;
        border-radius:10px;
        background:#e85c8a;
        color:#fff !important;
        text-decoration:none !important;
        font-size:.77rem;
        font-weight:850;
        white-space:nowrap;
        transition:.15s ease;
    }

    .claim-btn:hover {
        background:#cd4774;
        transform:translateY(-1px);
    }

    .note-cell {
        min-width:190px;
        max-width:280px;
        color:#666 !important;
        white-space:normal;
        line-height:1.45;
    }

    .claim-help {
        margin-top:7px;
        color:#888;
        font-size:.73rem;
        line-height:1.45;
    }

    /* ---------- MOBILE CARDS ---------- */
    .mobile-list { display:none; }

    .job-card {
        border:1px solid #e9e9e9;
        border-radius:18px;
        background:#fff;
        padding:16px;
        margin-bottom:12px;
        box-shadow:0 5px 18px rgba(0,0,0,.025);
    }

    .card-top {
        display:flex;
        justify-content:space-between;
        gap:12px;
        align-items:flex-start;
        margin-bottom:13px;
    }

    .card-id {
        color:#171717;
        font-weight:900;
        font-size:1rem;
    }

    .card-fare {
        color:#171717;
        font-weight:900;
        font-size:1.05rem;
        text-align:right;
    }

    .mobile-route {
        padding:13px;
        border:1px solid #eeeeee;
        border-radius:14px;
        background:#fafafa;
        margin:12px 0;
    }

    .route-small {
        color:#8a8a8a;
        font-size:.68rem;
        font-weight:850;
        letter-spacing:.05em;
        margin-bottom:2px;
    }

    .route-main {
        color:#171717;
        font-size:.92rem;
        font-weight:800;
        line-height:1.4;
    }

    .route-arrow {
        margin:6px 0;
        color:#d86a92;
        font-weight:900;
    }

    .card-meta {
        display:grid;
        grid-template-columns:1fr 1fr;
        gap:9px;
        margin:12px 0;
    }

    .meta-box {
        padding:10px 11px;
        border:1px solid #eeeeee;
        border-radius:12px;
        background:#fff;
    }

    .meta-label {
        color:#8a8a8a;
        font-size:.67rem;
        font-weight:850;
        text-transform:uppercase;
        letter-spacing:.04em;
    }

    .meta-value {
        margin-top:2px;
        color:#242424;
        font-size:.84rem;
        font-weight:700;
    }

    .mobile-claim {
        display:flex;
        justify-content:center;
        width:100%;
        padding:11px 12px;
        margin-top:12px;
        border-radius:12px;
        background:#e85c8a;
        color:#fff !important;
        text-decoration:none !important;
        font-size:.83rem;
        font-weight:850;
    }

    /* ---------- NOTES ---------- */
    .privacy-note,
    .footer-note {
        margin-top:14px;
        padding:13px 15px;
        border-radius:14px;
        font-size:.82rem;
        line-height:1.6;
    }

    .privacy-note {
        color:#666;
        background:#fafafa;
        border:1px solid #ebebeb;
    }

    .footer-note {
        color:#755a31;
        background:#fffaf0;
        border:1px solid #eee1c4;
    }

    .empty-box {
        padding:28px 18px;
        border:1px dashed #dcdcdc;
        border-radius:17px;
        text-align:center;
        color:#777;
        background:#fff;
    }

    @media (max-width:760px) {
        .block-container {
            padding-left:.85rem;
            padding-right:.85rem;
            padding-top:.7rem;
        }

        .brandbar {
            align-items:flex-start;
        }

        .live-pill { display:none; }

        .logo {
            width:42px;
            height:42px;
            border-radius:12px;
        }

        .hero {
            padding:22px 18px;
            border-radius:20px;
        }

        .hero h1 {
            font-size:2.15rem;
        }

        .stats {
            grid-template-columns:1fr;
            gap:8px;
        }

        .stat {
            padding:13px 14px;
            border-radius:14px;
        }

        .table-wrap { display:none; }
        .mobile-list { display:block; }

        .result-row {
            align-items:flex-start;
        }

        .card-meta {
            grid-template-columns:1fr 1fr;
        }
    }

    @media (max-width:420px) {
        .card-meta {
            grid-template-columns:1fr;
        }
    }


    /* ==========================================================
       STREAMLIT / BASEWEB LIGHT THEME HARD OVERRIDE
       Fixes dark select/multiselect controls on newer Streamlit.
       ========================================================== */
    [data-testid="stTextInput"] input,
    [data-testid="stTextInput"] [data-baseweb="input"],
    [data-testid="stTextInput"] [data-baseweb="base-input"],
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
    [data-testid="stSelectbox"] [role="combobox"],
    [data-testid="stMultiSelect"] [role="combobox"] {
        background:#ffffff !important;
        background-color:#ffffff !important;
        color:#171717 !important;
        -webkit-text-fill-color:#171717 !important;
        border-color:#dedede !important;
        box-shadow:none !important;
        color-scheme:light !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div > div {
        background-color:#ffffff !important;
        color:#171717 !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSelectbox"] [data-baseweb="select"] input,
    [data-testid="stSelectbox"] [role="combobox"] *,
    [data-testid="stMultiSelect"] [data-baseweb="select"] span,
    [data-testid="stMultiSelect"] [data-baseweb="select"] input,
    [data-testid="stMultiSelect"] [role="combobox"] * {
        color:#171717 !important;
        -webkit-text-fill-color:#171717 !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] svg,
    [data-testid="stMultiSelect"] [data-baseweb="select"] svg {
        fill:#6d6d6d !important;
        color:#6d6d6d !important;
    }

    /* Multiselect tags must stay pink after broad white override. */
    [data-testid="stMultiSelect"] [data-baseweb="tag"],
    [data-testid="stMultiSelect"] [data-baseweb="tag"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="tag"] span {
        background:#fff0f5 !important;
        color:#bd426d !important;
        -webkit-text-fill-color:#bd426d !important;
    }

    [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        border:1px solid #f3c4d4 !important;
    }

    [data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
        fill:#bd426d !important;
        color:#bd426d !important;
    }

    /* Dropdown popup rendered in Streamlit portal. */
    body > div[data-baseweb="popover"],
    body > div[data-baseweb="popover"] > div,
    [data-baseweb="popover"] [data-baseweb="menu"],
    [data-baseweb="menu"],
    ul[role="listbox"] {
        background:#ffffff !important;
        background-color:#ffffff !important;
        color:#171717 !important;
        color-scheme:light !important;
    }

    [role="option"] {
        background:#ffffff !important;
        color:#171717 !important;
        -webkit-text-fill-color:#171717 !important;
    }

    [role="option"]:hover,
    [role="option"][aria-selected="true"] {
        background:#fff1f6 !important;
        color:#bd426d !important;
        -webkit-text-fill-color:#bd426d !important;
    }

    /* Cleaner filter controls. */
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        min-height:48px !important;
        border-radius:12px !important;
    }

    [data-testid="stSlider"] [role="slider"] {
        background:#e85c8a !important;
        border-color:#e85c8a !important;
    }

    [data-testid="stSlider"] [data-testid="stTickBarMin"],
    [data-testid="stSlider"] [data-testid="stTickBarMax"] {
        color:#666 !important;
    }

    /* Button treatment: reset is subtle, refresh remains neutral. */
    .stButton > button:focus,
    .stButton > button:focus-visible {
        outline:none !important;
        box-shadow:0 0 0 3px rgba(232,92,138,.12) !important;
        border-color:#e85c8a !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GOOGLE SHEET
# ============================================================
SHEET_CACHE_TTL = 15
ALLOWED_STATUSES = {"open", "assigned", "completed", "cancelled"}


def sheet_csv_url():
    return (
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq"
        f"?tqx=out:csv&sheet={quote(SHEET_TAB)}"
    )


@st.cache_data(ttl=SHEET_CACHE_TTL, show_spinner=False)
def load_jobs():
    """
    Read the Driver Board as strings so values such as Booking ID
    do not lose leading zeroes.
    """
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

    # Keep the original Google Sheet row number as an internal stable fallback.
    # Header is assumed to be row 1, therefore first data row is row 2.
    df["_source_row"] = range(2, len(df) + 2)

    if data_columns:
        non_empty_mask = (
            df[data_columns]
            .astype(str)
            .apply(lambda col: col.str.strip().ne(""))
            .any(axis=1)
        )
        df = df.loc[non_empty_mask].copy()

    return df


# ============================================================
# COLUMN DETECTION
# ============================================================
COLUMN_ALIASES = {
    "booking_id": [
        "Booking ID", "Job ID", "ID Tempahan",
        "No Tempahan", "No. Tempahan", "ID"
    ],
    "status": [
        "Status", "Status Job", "Status Tempahan", "Booking Status"
    ],
    "pickup": [
        "Pickup", "Lokasi Pickup", "Lokasi Ambil",
        "Lokasi Ambil (Pickup)", "Pickup Location", "Dari"
    ],
    "destination": [
        "Destinasi", "Destination", "Lokasi Destinasi",
        "Drop Off", "Drop-off", "Ke"
    ],
    "date": [
        "Tarikh", "Tarikh Perjalanan",
        "Tarikh Tempahan", "Trip Date", "Date"
    ],
    "time": [
        "Masa", "Masa Pickup", "Masa Ambil",
        "Waktu Pickup", "Pickup Time", "Time"
    ],
    "pax": [
        "Penumpang", "Bilangan Penumpang",
        "Jumlah Penumpang", "Pax", "No. of Passengers"
    ],
    "trip_type": [
        "Jenis Trip", "Jenis Perjalanan",
        "Trip Type", "Jenis Tempahan"
    ],
    "baggage": [
        "Bagasi", "Maklumat Bagasi", "Luggage"
    ],
    "notes": [
        "Nota", "Nota Tambahan", "Catatan",
        "Remarks", "Remark", "Additional Notes"
    ],
    "fare": [
        "Tambang (RM)", "Tambang", "Harga",
        "Fare", "Fare (RM)", "Price"
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

    # Prefer exact match first.
    for alias in COLUMN_ALIASES[key]:
        alias_n = normalize_header(alias)
        if alias_n in normalized:
            return normalized[alias_n]

    # Fuzzy match only for longer aliases to avoid unsafe match such as "ID".
    for alias in COLUMN_ALIASES[key]:
        alias_n = normalize_header(alias)

        if len(alias_n) < 4:
            continue

        for col_n, original in normalized.items():
            if alias_n in col_n or col_n in alias_n:
                return original

    return None


# ============================================================
# VALUE HELPERS
# ============================================================
def clean_text(value, fallback="-"):
    if pd.isna(value):
        return fallback

    value = str(value).strip()

    if value == "" or value.casefold() in {"nan", "none", "null"}:
        return fallback

    return value


def get_value(row, column, fallback="-"):
    if not column:
        return fallback

    return clean_text(row.get(column, ""), fallback)


def safe(value, fallback="-"):
    return html.escape(clean_text(value, fallback))


def unique_values(df, column):
    if not column or df.empty:
        return []

    values = (
        df[column]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    values = values[
        ~values.str.casefold().isin(
            {"", "nan", "none", "null", "-"}
        )
    ]

    return sorted(
        values.unique().tolist(),
        key=lambda x: x.casefold()
    )


def fare_to_number(value):
    if pd.isna(value):
        return None

    text = str(value).strip()

    if not text:
        return None

    # Malaysia fare format is normally 1,234.56.
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
        return safe(value, "Semak admin")

    return f"RM {number:,.2f}"


def display_date(value):
    """
    Only normalize clearly unambiguous ISO dates.
    Other date formats are preserved exactly as supplied by Google Sheet.
    """
    text = clean_text(value, "-")

    match = re.fullmatch(
        r"(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T].*)?",
        text,
    )

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

    # 08:30:00 -> 08:30
    match_24h = re.fullmatch(r"(\d{1,2}):(\d{2}):00", text)
    if match_24h:
        return f"{int(match_24h.group(1)):02d}:{match_24h.group(2)}"

    # Keep all other formats as supplied.
    return text


def fallback_booking_id(source_row):
    try:
        row_number = int(source_row)
    except (TypeError, ValueError):
        row_number = 0

    return f"SG-R{row_number:04d}" if row_number else "SG-TEMP"


def make_booking_display(row, booking_column):
    booking_id = get_value(row, booking_column, "")

    if booking_id:
        return booking_id

    return fallback_booking_id(row.get("_source_row"))


def reset_filters():
    for key in (
        "search_location",
        "filter_dates",
        "filter_trip_types",
        "filter_pax",
        "fare_range",
        "sort_option",
    ):
        st.session_state.pop(key, None)


# ============================================================
# BRAND + HERO
# ============================================================
st.markdown(
    """
    <div class="brandbar">
        <div class="brand-left">
            <div class="logo">S</div>
            <div>
                <div class="brand-name"><span>She</span>GO</div>
                <div class="brand-sub">Driver Job Board • Johor</div>
            </div>
        </div>
        <div class="live-pill">
            <span class="live-dot"></span>
            Google Sheet Sync
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <span class="hero-badge">🚗 JOB UNTUK PEMANDU SHEGO</span>
        <h1>Cari trip yang sesuai dengan masa dan kawasan anda.</h1>
        <p>
            Hanya tempahan berstatus <b>Open</b> dipaparkan.
            Permintaan claim melalui WhatsApp <b>belum dianggap confirmed</b>
            sehingga admin mengesahkan pemandu dan menukar status job kepada
            <b>Assigned</b>.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD + VALIDATE
# ============================================================
try:
    jobs = load_jobs()
except Exception as exc:
    st.error(str(exc))
    st.stop()

if jobs.empty:
    st.info("Google Sheet belum mempunyai data job.")
    st.stop()

cols = {
    key: find_column(jobs, key)
    for key in COLUMN_ALIASES
}

if not cols["status"]:
    st.error(
        "Column **Status** tidak dijumpai. "
        "Pastikan tab Driver Board mempunyai column bernama `Status`."
    )
    st.stop()

if not cols["pickup"] or not cols["destination"]:
    st.error(
        "Column Pickup atau Destinasi tidak dapat dikesan."
    )

    with st.expander("Column yang berjaya dibaca"):
        st.write([
            col for col in jobs.columns
            if not str(col).startswith("_")
        ])

    st.stop()

# Build a stable display/claim ID before filtering and sorting.
jobs["_booking_display"] = jobs.apply(
    lambda row: make_booking_display(row, cols["booking_id"]),
    axis=1,
)

# Data-quality checks.
if not cols["booking_id"]:
    st.warning(
        "Column **Booking ID** tidak dijumpai. "
        "Sistem sedang guna ID sementara berdasarkan nombor baris Google Sheet "
        "(contoh: SG-R0002). Untuk production, sangat disarankan sediakan "
        "Booking ID yang unik dan kekal."
    )
else:
    explicit_ids = (
        jobs[cols["booking_id"]]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    duplicate_mask = explicit_ids.ne("") & explicit_ids.duplicated(keep=False)

    if duplicate_mask.any():
        duplicated_values = sorted(
            explicit_ids[duplicate_mask].unique().tolist()
        )
        preview = ", ".join(duplicated_values[:5])
        more = "..." if len(duplicated_values) > 5 else ""

        st.warning(
            "Ada **Booking ID duplicate** dalam Google Sheet: "
            f"{preview}{more}. Sila jadikan setiap Booking ID unik "
            "supaya claim driver tidak tersalah job."
        )


# ============================================================
# EXACT STATUS LOGIC
# Open = visible
# Assigned / Completed / Cancelled = hidden
# ============================================================
normalized_status = (
    jobs[cols["status"]]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.casefold()
)

unknown_statuses = sorted(
    set(normalized_status.unique()) - ALLOWED_STATUSES - {""}
)

if unknown_statuses:
    st.warning(
        "Ada status yang tidak ikut dropdown standard dan tidak akan dipaparkan: "
        + ", ".join(unknown_statuses[:8])
    )

open_jobs = jobs[
    normalized_status.eq(VISIBLE_STATUS)
].copy()


# ============================================================
# TOP STATS
# ============================================================
unique_dates = (
    len(unique_values(open_jobs, cols["date"]))
    if cols["date"]
    else 0
)

unique_trip_types = (
    len(unique_values(open_jobs, cols["trip_type"]))
    if cols["trip_type"]
    else 0
)

st.markdown(
    f"""
    <div class="stats">
        <div class="stat">
            <div class="stat-label">Job Open</div>
            <div class="stat-value">🚘 {len(open_jobs)} tersedia</div>
        </div>
        <div class="stat">
            <div class="stat-label">Tarikh Aktif</div>
            <div class="stat-value">📅 {unique_dates if unique_dates else "-"}</div>
        </div>
        <div class="stat">
            <div class="stat-label">Jenis Trip</div>
            <div class="stat-value">🛣️ {unique_trip_types if unique_trip_types else "-"}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


if open_jobs.empty:
    st.markdown(
        """
        <div class="empty-box">
            <b>Tiada job Open buat masa ini.</b><br>
            Job baru akan muncul apabila admin menetapkan status kepada Open
            dan halaman dimuat semula.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
# FILTER
# ============================================================
st.markdown(
    """
    <div class="section-title">Cari Job</div>
    <div class="section-sub">
        Cari menggunakan lokasi atau Booking ID, kemudian tapis ikut tarikh,
        jenis trip, penumpang dan tambang.
    </div>
    """,
    unsafe_allow_html=True,
)

fare_min_filter = None
fare_max_filter = None
fare_filter_active = False

with st.container(border=True):

    c1, c2 = st.columns(2)

    with c1:
        location_search = st.text_input(
            "Pickup / Destinasi / Booking ID",
            placeholder="Contoh: Ulu Tiram, Senai, SG-001...",
            key="search_location",
        ).strip().casefold()

    with c2:
        date_options = unique_values(
            open_jobs,
            cols["date"],
        )

        selected_dates = (
            st.multiselect(
                "Tarikh",
                options=date_options,
                placeholder="Semua tarikh",
                key="filter_dates",
            )
            if date_options
            else []
        )

    c3, c4 = st.columns(2)

    with c3:
        trip_options = unique_values(
            open_jobs,
            cols["trip_type"],
        )

        selected_trip_types = (
            st.multiselect(
                "Jenis Trip",
                options=trip_options,
                placeholder="Semua jenis trip",
                key="filter_trip_types",
            )
            if trip_options
            else []
        )

    with c4:
        pax_options = unique_values(
            open_jobs,
            cols["pax"],
        )

        selected_pax = (
            st.multiselect(
                "Penumpang",
                options=pax_options,
                placeholder="Semua",
                key="filter_pax",
            )
            if pax_options
            else []
        )

    fare_numbers = []

    if cols["fare"]:
        fare_numbers = [
            n for n in (
                fare_to_number(v)
                for v in open_jobs[cols["fare"]]
            )
            if n is not None
        ]

    if fare_numbers:
        min_fare = int(min(fare_numbers))
        max_fare = int(max(fare_numbers))

        if min_fare == max_fare:
            st.caption(f"Tambang semasa: RM {min_fare:,}")
        else:
            selected_range = st.slider(
                "Julat Tambang (RM)",
                min_value=min_fare,
                max_value=max_fare,
                value=(min_fare, max_fare),
                key="fare_range",
            )

            fare_min_filter = float(selected_range[0])
            fare_max_filter = float(selected_range[1])
            fare_filter_active = selected_range != (min_fare, max_fare)

    sort_option = st.selectbox(
        "Susun Job",
        options=[
            "Asal dari Google Sheet",
            "Tambang tertinggi",
            "Tambang terendah",
        ],
        key="sort_option",
    )

    refresh_col, reset_col = st.columns(2)

    with refresh_col:
        if st.button(
            "↻ Refresh Data",
            use_container_width=True,
        ):
            load_jobs.clear()
            st.rerun()

    with reset_col:
        st.button(
            "✕ Reset Filter",
            use_container_width=True,
            on_click=reset_filters,
        )


# ============================================================
# APPLY FILTER
# ============================================================
filtered = open_jobs.copy()


if location_search:
    pickup_series = (
        filtered[cols["pickup"]]
        .fillna("")
        .astype(str)
        .str.casefold()
    )

    destination_series = (
        filtered[cols["destination"]]
        .fillna("")
        .astype(str)
        .str.casefold()
    )

    booking_series = (
        filtered["_booking_display"]
        .fillna("")
        .astype(str)
        .str.casefold()
    )

    filtered = filtered[
        pickup_series.str.contains(
            location_search,
            regex=False,
            na=False,
        )
        |
        destination_series.str.contains(
            location_search,
            regex=False,
            na=False,
        )
        |
        booking_series.str.contains(
            location_search,
            regex=False,
            na=False,
        )
    ]


if selected_dates and cols["date"]:
    filtered = filtered[
        filtered[cols["date"]]
        .astype(str)
        .str.strip()
        .isin(selected_dates)
    ]


if selected_trip_types and cols["trip_type"]:
    filtered = filtered[
        filtered[cols["trip_type"]]
        .astype(str)
        .str.strip()
        .isin(selected_trip_types)
    ]


if selected_pax and cols["pax"]:
    filtered = filtered[
        filtered[cols["pax"]]
        .astype(str)
        .str.strip()
        .isin(selected_pax)
    ]


# Only apply fare range when user actually narrows the slider.
# This prevents "Semak admin" rows from disappearing with the default range.
if (
    fare_filter_active
    and cols["fare"]
    and fare_min_filter is not None
    and fare_max_filter is not None
):
    fare_series = filtered[
        cols["fare"]
    ].apply(fare_to_number)

    filtered = filtered[
        fare_series.between(
            fare_min_filter,
            fare_max_filter,
        )
    ]


# Sort
if cols["fare"] and sort_option != "Asal dari Google Sheet":
    filtered = filtered.copy()

    filtered["_fare_num"] = filtered[
        cols["fare"]
    ].apply(fare_to_number)

    filtered = filtered.sort_values(
        "_fare_num",
        ascending=(sort_option == "Tambang terendah"),
        na_position="last",
        kind="stable",
    ).drop(columns=["_fare_num"])
else:
    filtered = filtered.sort_values(
        "_source_row",
        ascending=True,
        kind="stable",
    )


# ============================================================
# RESULT HEADER
# ============================================================
st.markdown(
    f"""
    <div class="result-row">
        <div class="result-pill">
            🚗 {len(filtered)} job sepadan
        </div>
        <div class="result-note">
            Claim melalui WhatsApp tertakluk kepada pengesahan admin.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.markdown(
        """
        <div class="empty-box">
            Tiada job yang sepadan dengan filter anda.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
# BUILD DESKTOP TABLE + MOBILE CARDS
# ============================================================
desktop_rows = []
mobile_cards = []


for _, row in filtered.iterrows():
    booking_id = clean_text(
        row.get("_booking_display", ""),
        fallback_booking_id(row.get("_source_row")),
    )

    pickup = get_value(
        row,
        cols["pickup"],
        "Tidak dinyatakan",
    )

    destination = get_value(
        row,
        cols["destination"],
        "Tidak dinyatakan",
    )

    trip_date_raw = get_value(
        row,
        cols["date"],
        "-",
    )
    trip_date = display_date(trip_date_raw)

    pickup_time_raw = get_value(
        row,
        cols["time"],
        "-",
    )
    pickup_time = display_time(pickup_time_raw)

    pax = get_value(
        row,
        cols["pax"],
        "-",
    )

    trip_type = get_value(
        row,
        cols["trip_type"],
        "-",
    )

    baggage = get_value(
        row,
        cols["baggage"],
        "-",
    )

    notes = get_value(
        row,
        cols["notes"],
        "-",
    )

    fare = get_value(
        row,
        cols["fare"],
        "Semak admin",
    )

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
        f"💰 Tambang: {display_fare(fare)}\n\n"
        "Boleh semak sama ada job ini masih Open dan confirmkan kepada saya?"
    )

    whatsapp_url = (
        f"https://wa.me/{ADMIN_WHATSAPP}"
        f"?text={quote(whatsapp_message)}"
    )

    safe_whatsapp = html.escape(
        whatsapp_url,
        quote=True,
    )

    # Desktop row
    desktop_rows.append(
        "<tr>"
        f'<td><span class="booking-id">{safe(booking_id)}</span></td>'
        f'<td><span class="status-open">● OPEN</span></td>'
        f'<td class="route-cell">📍 {safe(pickup)}</td>'
        f'<td class="route-cell">🏁 {safe(destination)}</td>'
        f"<td>{safe(trip_date)}</td>"
        f"<td>{safe(pickup_time)}</td>"
        f"<td>{safe(pax)}</td>"
        f"<td>{safe(trip_type)}</td>"
        f"<td>{safe(baggage)}</td>"
        f'<td class="note-cell">{safe(notes)}</td>'
        f'<td class="fare">{display_fare(fare)}</td>'
        f'<td><a class="claim-btn" href="{safe_whatsapp}" target="_blank" rel="noopener noreferrer">💬 Mohon Claim</a></td>'
        "</tr>"
    )

    # Mobile card
    mobile_cards.append(
        f"""
        <div class="job-card">
            <div class="card-top">
                <div>
                    <div class="card-id">{safe(booking_id)}</div>
                    <div style="margin-top:6px;">
                        <span class="status-open">● OPEN</span>
                    </div>
                </div>
                <div class="card-fare">{display_fare(fare)}</div>
            </div>

            <div class="mobile-route">
                <div class="route-small">PICKUP</div>
                <div class="route-main">📍 {safe(pickup)}</div>
                <div class="route-arrow">↓</div>
                <div class="route-small">DESTINASI</div>
                <div class="route-main">🏁 {safe(destination)}</div>
            </div>

            <div class="card-meta">
                <div class="meta-box">
                    <div class="meta-label">Tarikh</div>
                    <div class="meta-value">📅 {safe(trip_date)}</div>
                </div>
                <div class="meta-box">
                    <div class="meta-label">Masa</div>
                    <div class="meta-value">🕐 {safe(pickup_time)}</div>
                </div>
                <div class="meta-box">
                    <div class="meta-label">Penumpang</div>
                    <div class="meta-value">👥 {safe(pax)}</div>
                </div>
                <div class="meta-box">
                    <div class="meta-label">Jenis Trip</div>
                    <div class="meta-value">🚗 {safe(trip_type)}</div>
                </div>
                <div class="meta-box">
                    <div class="meta-label">Bagasi</div>
                    <div class="meta-value">🧳 {safe(baggage)}</div>
                </div>
                <div class="meta-box">
                    <div class="meta-label">Tambang</div>
                    <div class="meta-value">💰 {display_fare(fare)}</div>
                </div>
                <div class="meta-box" style="grid-column:1/-1;">
                    <div class="meta-label">Nota</div>
                    <div class="meta-value">📝 {safe(notes)}</div>
                </div>
            </div>

            <a class="mobile-claim"
               href="{safe_whatsapp}"
               target="_blank"
               rel="noopener noreferrer">
               💬 Mohon Claim melalui WhatsApp
            </a>
            <div class="claim-help">
                Job hanya dianggap Assigned selepas admin mengesahkan claim.
            </div>
        </div>
        """
    )


# ============================================================
# DISPLAY
# ============================================================
st.markdown(
    """
    <div class="section-title">Senarai Job Open</div>
    <div class="section-sub">
        Desktop menggunakan table. Pada telefon, paparan automatik bertukar kepada card.
    </div>
    """,
    unsafe_allow_html=True,
)


desktop_table = (
    '<div class="table-wrap">'
    '<table class="job-table">'
    "<thead><tr>"
    "<th>Booking ID</th>"
    "<th>Status</th>"
    "<th>Pickup</th>"
    "<th>Destinasi</th>"
    "<th>Tarikh</th>"
    "<th>Masa</th>"
    "<th>Penumpang</th>"
    "<th>Jenis Trip</th>"
    "<th>Bagasi</th>"
    "<th>Nota</th>"
    "<th>Tambang</th>"
    "<th>Tindakan</th>"
    "</tr></thead>"
    "<tbody>"
    + "".join(desktop_rows)
    + "</tbody></table></div>"
)

mobile_list = (
    '<div class="mobile-list">'
    + "".join(mobile_cards)
    + "</div>"
)

st.markdown(
    desktop_table + mobile_list,
    unsafe_allow_html=True,
)


# ============================================================
# NOTES
# ============================================================
st.markdown(
    """
    <div class="privacy-note">
        🔒 <b>Privasi pelanggan:</b> Driver Board ini sepatutnya hanya mengandungi
        maklumat yang selamat untuk dilihat oleh pemandu. Jika Google Sheet ini
        dibuka kepada public / “Anyone with the link”, jangan simpan nama,
        nombor telefon atau maklumat sensitif pelanggan dalam spreadsheet public
        yang sama.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="footer-note">
        💡 <b>Flow status:</b>
        <b>Open</b> = masih tersedia →
        driver hantar permintaan claim →
        admin sahkan pemandu dan tukar kepada <b>Assigned</b> →
        <b>Completed</b> = trip selesai →
        <b>Cancelled</b> = tempahan dibatalkan.
        Hanya <b>Open</b> akan muncul di Driver Board.
    </div>
    """,
    unsafe_allow_html=True,
)
