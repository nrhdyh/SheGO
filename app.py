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

# Jika column Status wujud, hanya status ini akan dipaparkan.
PUBLIC_STATUSES = {
    "open",
    "available",
    "tersedia",
    "job tersedia",
}


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
# WHITE UI THEME
# ============================================================
st.markdown(
    """
    <style>
    /* =========================
       GLOBAL
       ========================= */
    :root {
        color-scheme: light !important;
    }

    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background: #ffffff !important;
        color: #171717 !important;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: rgba(255,255,255,.97) !important;
        border-bottom: 1px solid #eeeeee;
    }

    .block-container {
        max-width: 1220px;
        padding-top: 1.15rem;
        padding-bottom: 4rem;
    }

    /* =========================
       BRAND
       ========================= */
    .shego-topbar {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 4px 0 20px;
    }

    .shego-logo {
        width: 48px;
        height: 48px;
        border-radius: 15px;
        display: grid;
        place-items: center;
        color: #ffffff;
        background: #e85c8a;
        font-size: 22px;
        font-weight: 900;
        box-shadow: 0 8px 22px rgba(232,92,138,.18);
    }

    .shego-name {
        font-size: 1.55rem;
        font-weight: 900;
        line-height: 1;
        letter-spacing: -.04em;
        color: #171717;
    }

    .shego-name span {
        color: #e85c8a;
    }

    .shego-subtitle {
        margin-top: 5px;
        color: #777777;
        font-size: .83rem;
    }

    /* =========================
       HERO
       ========================= */
    .hero {
        padding: 30px 32px;
        border: 1px solid #ececec;
        border-radius: 24px;
        background: #ffffff;
        box-shadow: 0 10px 30px rgba(0,0,0,.04);
        margin-bottom: 28px;
    }

    .hero-badge {
        display: inline-flex;
        padding: 7px 12px;
        border-radius: 999px;
        background: #fff3f7;
        border: 1px solid #f2d6df;
        color: #c84672;
        font-size: .76rem;
        font-weight: 850;
        letter-spacing: .07em;
    }

    .hero h1 {
        max-width: 760px;
        margin: 15px 0 12px;
        color: #171717;
        font-size: clamp(2.05rem, 5vw, 3.65rem);
        line-height: 1.03;
        letter-spacing: -.055em;
    }

    .hero p {
        max-width: 850px;
        margin: 0;
        color: #666666;
        font-size: 1rem;
        line-height: 1.75;
    }

    /* =========================
       SECTION TITLES
       ========================= */
    .section-title {
        margin: 6px 0 2px;
        color: #171717;
        font-size: 1.1rem;
        font-weight: 900;
    }

    .section-subtitle {
        margin-bottom: 13px;
        color: #777777;
        font-size: .85rem;
    }

    /* =========================
       STREAMLIT INPUTS - FORCE WHITE
       ========================= */
    label,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {
        color: #313131 !important;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"],
    .stTextInput input {
        background: #ffffff !important;
        color: #171717 !important;
        border-color: #dddddd !important;
    }

    .stTextInput input {
        -webkit-text-fill-color: #171717 !important;
    }

    .stTextInput input::placeholder {
        color: #999999 !important;
        -webkit-text-fill-color: #999999 !important;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input {
        color: #171717 !important;
        -webkit-text-fill-color: #171717 !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"] {
        background: #ffffff !important;
        color: #171717 !important;
    }

    li[role="option"] {
        background: #ffffff !important;
        color: #171717 !important;
    }

    li[role="option"]:hover {
        background: #fff3f7 !important;
    }

    /* Slider */
    [data-testid="stSlider"] {
        color: #171717 !important;
    }

    /* Filter box */
    .filter-box {
        border: 1px solid #ececec;
        border-radius: 20px;
        padding: 18px 18px 6px;
        background: #ffffff;
        box-shadow: 0 6px 20px rgba(0,0,0,.025);
        margin-bottom: 20px;
    }

    /* =========================
       BUTTONS
       ========================= */
    .stButton > button {
        min-height: 44px;
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
        background: #ffffff !important;
        color: #171717 !important;
        font-weight: 800 !important;
    }

    .stButton > button:hover {
        border-color: #e85c8a !important;
        color: #c84672 !important;
    }

    /* =========================
       RESULT SUMMARY
       ========================= */
    .result-summary {
        display: flex;
        align-items: center;
        gap: 8px;
        width: fit-content;
        margin: 16px 0 14px;
        padding: 8px 13px;
        border-radius: 999px;
        background: #fff3f7;
        border: 1px solid #f2d6df;
        color: #c84672;
        font-size: .84rem;
        font-weight: 850;
    }

    /* =========================
       CUSTOM WHITE TABLE
       ========================= */
    .job-table-wrap {
        width: 100%;
        overflow-x: auto;
        border: 1px solid #e8e8e8;
        border-radius: 17px;
        background: #ffffff;
        box-shadow: 0 6px 22px rgba(0,0,0,.03);
        margin-bottom: 24px;
    }

    table.job-table {
        width: 100%;
        min-width: 1080px;
        border-collapse: collapse;
        background: #ffffff;
        color: #171717;
    }

    .job-table th {
        position: sticky;
        top: 0;
        z-index: 1;
        padding: 13px 14px;
        background: #fafafa;
        color: #525252;
        border-bottom: 1px solid #e8e8e8;
        text-align: left;
        font-size: .76rem;
        font-weight: 850;
        letter-spacing: .02em;
        white-space: nowrap;
    }

    .job-table td {
        padding: 14px;
        border-bottom: 1px solid #eeeeee;
        vertical-align: top;
        color: #222222;
        font-size: .88rem;
    }

    .job-table tbody tr:last-child td {
        border-bottom: none;
    }

    .job-table tbody tr:hover {
        background: #fffafb;
    }

    .job-id {
        font-weight: 900;
        color: #171717;
        white-space: nowrap;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        padding: 5px 9px;
        border-radius: 999px;
        background: #edf9f3;
        border: 1px solid #d5edde;
        color: #147b58;
        font-size: .72rem;
        font-weight: 850;
        white-space: nowrap;
    }

    .pickup-cell,
    .destination-cell {
        min-width: 170px;
        font-weight: 700;
    }

    .fare-cell {
        font-weight: 900;
        white-space: nowrap;
    }

    .claim-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 9px 12px;
        border-radius: 10px;
        background: #e85c8a;
        color: #ffffff !important;
        text-decoration: none !important;
        font-size: .78rem;
        font-weight: 850;
        white-space: nowrap;
        transition: .15s ease;
    }

    .claim-btn:hover {
        background: #cf4775;
        transform: translateY(-1px);
    }

    .no-data {
        padding: 24px;
        border: 1px dashed #dddddd;
        border-radius: 15px;
        color: #777777;
        background: #ffffff;
        text-align: center;
    }

    .privacy-note {
        margin-top: 12px;
        padding: 13px 15px;
        border: 1px solid #ebebeb;
        border-radius: 14px;
        background: #fafafa;
        color: #666666;
        font-size: .83rem;
        line-height: 1.6;
    }

    .footer-note {
        margin-top: 16px;
        padding: 13px 15px;
        border-radius: 14px;
        background: #fffaf0;
        border: 1px solid #eee1c4;
        color: #755a31;
        font-size: .83rem;
        line-height: 1.6;
    }

    /* =========================
       MOBILE
       ========================= */
    @media (max-width: 720px) {
        .block-container {
            padding-left: .9rem;
            padding-right: .9rem;
            padding-top: .75rem;
        }

        .hero {
            padding: 22px 18px;
            border-radius: 20px;
        }

        .hero h1 {
            font-size: 2.18rem;
        }

        .shego-logo {
            width: 42px;
            height: 42px;
            border-radius: 12px;
        }

        .job-table th,
        .job-table td {
            padding: 11px 12px;
            font-size: .81rem;
        }

        .filter-box {
            padding: 14px 14px 2px;
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
    return (
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq"
        f"?tqx=out:csv&sheet={quote(SHEET_TAB)}"
    )


@st.cache_data(ttl=30, show_spinner=False)
def load_jobs():
    try:
        df = pd.read_csv(sheet_csv_url())
    except Exception as exc:
        raise RuntimeError(
            f"Tak dapat baca tab '{SHEET_TAB}'. "
            "Pastikan nama tab betul dan Google Sheet boleh dibaca."
        ) from exc

    df.columns = [str(col).strip() for col in df.columns]
    df = df.dropna(how="all").copy()

    return df


# ============================================================
# SMART COLUMN DETECTION
# ============================================================
COLUMN_ALIASES = {
    "booking_id": [
        "Booking ID",
        "Job ID",
        "ID Tempahan",
        "No Tempahan",
        "No. Tempahan",
        "ID",
    ],
    "status": [
        "Status",
        "Status Job",
        "Status Tempahan",
        "Booking Status",
    ],
    "pickup": [
        "Pickup",
        "Lokasi Pickup",
        "Lokasi Ambil",
        "Lokasi Ambil (Pickup)",
        "Pickup Location",
        "Dari",
    ],
    "destination": [
        "Destinasi",
        "Destination",
        "Lokasi Destinasi",
        "Drop Off",
        "Drop-off",
        "Ke",
    ],
    "date": [
        "Tarikh",
        "Tarikh Perjalanan",
        "Tarikh Tempahan",
        "Trip Date",
        "Date",
    ],
    "time": [
        "Masa",
        "Masa Pickup",
        "Masa Ambil",
        "Waktu Pickup",
        "Pickup Time",
        "Time",
    ],
    "pax": [
        "Penumpang",
        "Bilangan Penumpang",
        "Jumlah Penumpang",
        "Pax",
        "No. of Passengers",
    ],
    "trip_type": [
        "Jenis Trip",
        "Jenis Perjalanan",
        "Trip Type",
        "Jenis Tempahan",
    ],
    "baggage": [
        "Bagasi",
        "Maklumat Bagasi",
        "Luggage",
    ],
    "notes": [
        "Nota",
        "Nota Tambahan",
        "Catatan",
        "Remarks",
        "Additional Notes",
    ],
    "fare": [
        "Tambang (RM)",
        "Tambang",
        "Harga",
        "Fare",
        "Fare (RM)",
        "Price",
    ],
}


def normalize_header(value):
    value = str(value).strip().casefold()
    value = re.sub(r"[\s_\-()/.:]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def find_column(df, key):
    normalized_columns = {
        normalize_header(col): col
        for col in df.columns
    }

    # Exact normalized match
    for alias in COLUMN_ALIASES[key]:
        alias_norm = normalize_header(alias)
        if alias_norm in normalized_columns:
            return normalized_columns[alias_norm]

    # Partial match
    for alias in COLUMN_ALIASES[key]:
        alias_norm = normalize_header(alias)

        if len(alias_norm) < 4:
            continue

        for column_norm, original_column in normalized_columns.items():
            if alias_norm in column_norm or column_norm in alias_norm:
                return original_column

    return None


# ============================================================
# HELPERS
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

    return clean_text(
        row.get(column, ""),
        fallback,
    )


def safe(value, fallback="-"):
    return html.escape(clean_text(value, fallback))


def unique_values(df, column):
    if not column or df.empty:
        return []

    values = (
        df[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    values = values[
        ~values.str.casefold().isin(
            ["", "nan", "none", "null", "-"]
        )
    ]

    return sorted(
        values.unique().tolist(),
        key=lambda x: x.casefold(),
    )


def fare_to_number(value):
    if pd.isna(value):
        return None

    cleaned = re.sub(
        r"[^0-9.]",
        "",
        str(value).strip(),
    )

    if not cleaned:
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


def fare_display(value):
    number = fare_to_number(value)

    if number is None:
        return safe(value, "Semak admin")

    return f"RM {number:,.2f}"


# ============================================================
# HEADER
# ============================================================
st.markdown(
    """
    <div class="shego-topbar">
        <div class="shego-logo">S</div>
        <div>
            <div class="shego-name"><span>She</span>GO</div>
            <div class="shego-subtitle">Driver Job Board • Johor</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <span class="hero-badge">🚗 SHEGO • JOB TERSEDIA</span>
        <h1>Pilih perjalanan yang sesuai dengan anda.</h1>
        <p>
            Gunakan filter untuk cari perjalanan mengikut kawasan, tarikh,
            jenis trip dan bilangan penumpang. Semua job yang sepadan akan
            terus dipaparkan dalam jadual di bawah. Jika berminat, tekan
            WhatsApp untuk claim dengan admin SheGO.
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
    st.stop()

if jobs.empty:
    st.info("Belum ada job tersedia sekarang.")
    st.stop()

cols = {
    key: find_column(jobs, key)
    for key in COLUMN_ALIASES
}

if not cols["pickup"] and not cols["destination"]:
    st.error("Column Pickup / Destinasi tak dapat dikesan.")

    with st.expander("Lihat column yang app berjaya baca"):
        st.write(list(jobs.columns))

    st.stop()


# ============================================================
# STATUS FILTER
# ============================================================
public_jobs = jobs.copy()

if cols["status"]:
    status_series = (
        public_jobs[cols["status"]]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    public_jobs = public_jobs[
        status_series.isin(PUBLIC_STATUSES)
        | status_series.eq("")
    ].copy()


# ============================================================
# FILTER UI
# ============================================================
st.markdown(
    """
    <div class="section-title">Filter Job</div>
    <div class="section-subtitle">
        Filter yang tersedia akan ikut column yang wujud dalam Google Sheet.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="filter-box">', unsafe_allow_html=True)

f1, f2 = st.columns(2)

with f1:
    location_search = st.text_input(
        "Pickup / Destinasi",
        placeholder="Contoh: Ulu Tiram, JB, Senai...",
    ).strip().casefold()

with f2:
    date_options = unique_values(
        public_jobs,
        cols["date"],
    )

    selected_dates = (
        st.multiselect(
            "Tarikh",
            options=date_options,
            placeholder="Semua tarikh",
        )
        if date_options
        else []
    )

f3, f4 = st.columns(2)

with f3:
    trip_options = unique_values(
        public_jobs,
        cols["trip_type"],
    )

    selected_trip_types = (
        st.multiselect(
            "Jenis Trip",
            options=trip_options,
            placeholder="Semua jenis trip",
        )
        if trip_options
        else []
    )

with f4:
    pax_options = unique_values(
        public_jobs,
        cols["pax"],
    )

    selected_pax = (
        st.multiselect(
            "Penumpang",
            options=pax_options,
            placeholder="Semua",
        )
        if pax_options
        else []
    )


# Tambang filter hanya muncul jika ada numeric fare
fare_values = []

if cols["fare"]:
    fare_values = [
        number
        for number in (
            fare_to_number(v)
            for v in public_jobs[cols["fare"]]
        )
        if number is not None
    ]

min_fare_filter = None
max_fare_filter = None

if fare_values:
    fare_min = int(min(fare_values))
    fare_max = int(max(fare_values))

    if fare_min == fare_max:
        st.caption(f"Tambang semasa: RM{fare_min}")
        min_fare_filter = float(fare_min)
        max_fare_filter = float(fare_max)
    else:
        selected_fare = st.slider(
            "Julat Tambang (RM)",
            min_value=fare_min,
            max_value=fare_max,
            value=(fare_min, fare_max),
        )

        min_fare_filter = float(selected_fare[0])
        max_fare_filter = float(selected_fare[1])


if st.button(
    "↻ Refresh Data",
    use_container_width=True,
):
    load_jobs.clear()
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# APPLY FILTERS
# ============================================================
filtered_jobs = public_jobs.copy()


# Location
if location_search:
    pickup_series = (
        filtered_jobs[cols["pickup"]]
        .fillna("")
        .astype(str)
        .str.casefold()
        if cols["pickup"]
        else pd.Series("", index=filtered_jobs.index)
    )

    destination_series = (
        filtered_jobs[cols["destination"]]
        .fillna("")
        .astype(str)
        .str.casefold()
        if cols["destination"]
        else pd.Series("", index=filtered_jobs.index)
    )

    filtered_jobs = filtered_jobs[
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
    ]


# Date
if selected_dates and cols["date"]:
    filtered_jobs = filtered_jobs[
        filtered_jobs[cols["date"]]
        .astype(str)
        .str.strip()
        .isin(selected_dates)
    ]


# Trip type
if selected_trip_types and cols["trip_type"]:
    filtered_jobs = filtered_jobs[
        filtered_jobs[cols["trip_type"]]
        .astype(str)
        .str.strip()
        .isin(selected_trip_types)
    ]


# Pax
if selected_pax and cols["pax"]:
    filtered_jobs = filtered_jobs[
        filtered_jobs[cols["pax"]]
        .astype(str)
        .str.strip()
        .isin(selected_pax)
    ]


# Fare
if (
    cols["fare"]
    and min_fare_filter is not None
    and max_fare_filter is not None
):
    numeric_fare = filtered_jobs[
        cols["fare"]
    ].apply(fare_to_number)

    filtered_jobs = filtered_jobs[
        numeric_fare.isna()
        |
        numeric_fare.between(
            min_fare_filter,
            max_fare_filter,
        )
    ]


# ============================================================
# RESULT COUNT
# ============================================================
st.markdown(
    f"""
    <div class="result-summary">
        🚘 {len(filtered_jobs)} job tersedia
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-title">Senarai Job</div>
    <div class="section-subtitle">
        Scroll ke kanan pada telefon jika mahu lihat semua column.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# WHITE HTML TABLE
# ============================================================
if filtered_jobs.empty:
    st.markdown(
        """
        <div class="no-data">
            Tiada job yang sepadan dengan filter anda sekarang.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    rows_html = []

    for position, (_, row) in enumerate(
        filtered_jobs.iterrows(),
        start=1,
    ):
        booking_id = get_value(
            row,
            cols["booking_id"],
            "",
        )

        if not booking_id:
            booking_id = f"SG-{position:05d}"

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

        trip_date = get_value(
            row,
            cols["date"],
            "-",
        )

        pickup_time = get_value(
            row,
            cols["time"],
            "-",
        )

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
            f"Hi Admin SheGO, saya berminat nak claim job {booking_id}.\n\n"
            f"📍 Pickup: {pickup}\n"
            f"🏁 Destinasi: {destination}\n"
            f"📅 Tarikh: {trip_date}\n"
            f"🕐 Masa: {pickup_time}\n"
            f"👥 Penumpang: {pax}\n"
            f"🚗 Jenis trip: {trip_type}\n"
            f"🧳 Bagasi: {baggage}\n"
            f"💰 Tambang: {fare}\n\n"
            "Boleh semak sama ada job ini masih available?"
        )

        whatsapp_url = (
            f"https://wa.me/{ADMIN_WHATSAPP}"
            f"?text={quote(whatsapp_message)}"
        )

        rows_html.append(
            "<tr>"
            f'<td><span class="job-id">{safe(booking_id)}</span></td>'
            f'<td><span class="status-pill">● TERSEDIA</span></td>'
            f'<td class="pickup-cell">📍 {safe(pickup)}</td>'
            f'<td class="destination-cell">🏁 {safe(destination)}</td>'
            f"<td>{safe(trip_date)}</td>"
            f"<td>{safe(pickup_time)}</td>"
            f"<td>{safe(pax)}</td>"
            f"<td>{safe(trip_type)}</td>"
            f"<td>{safe(baggage)}</td>"
            f"<td>{safe(notes)}</td>"
            f'<td class="fare-cell">{fare_display(fare)}</td>'
            f'<td><a class="claim-btn" target="_blank" rel="noopener" href="{html.escape(whatsapp_url, quote=True)}">💬 Claim Job</a></td>'
            "</tr>"
        )

    table_html = (
        '<div class="job-table-wrap">'
        '<table class="job-table">'
        "<thead>"
        "<tr>"
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
        "</tr>"
        "</thead>"
        "<tbody>"
        + "".join(rows_html)
        + "</tbody>"
        "</table>"
        "</div>"
    )

    st.markdown(
        table_html,
        unsafe_allow_html=True,
    )


# ============================================================
# PRIVACY + FOOTER
# ============================================================
st.markdown(
    """
    <div class="privacy-note">
        🔒 <b>Privasi pelanggan:</b> nama dan nombor telefon pelanggan
        tidak dipaparkan pada Driver Board. Maklumat lanjut hanya diberikan
        selepas admin mengesahkan pemandu untuk job tersebut.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="footer-note">
        💡 <b>Nota:</b> Menekan “Claim Job” akan membuka WhatsApp admin.
        Claim belum bermaksud job telah diberikan kepada anda sehingga
        admin SheGO memberi pengesahan.
    </div>
    """,
    unsafe_allow_html=True,
)
