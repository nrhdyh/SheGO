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

# If a Status column exists, only these values are shown publicly.
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
# STYLE
# ============================================================
st.markdown(
    """
    <style>
        #MainMenu {visibility:hidden;}
        footer {visibility:hidden;}

        header[data-testid="stHeader"] {
            background:rgba(255,255,255,.78);
            backdrop-filter:blur(12px);
        }

        .stApp {
            background:
                radial-gradient(circle at 95% 0%, #ffe5ee 0, transparent 27%),
                linear-gradient(180deg,#fffafd 0%,#ffffff 38%);
        }

        .block-container {
            max-width:1120px;
            padding-top:1.25rem;
            padding-bottom:5rem;
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
            max-width:760px;
            color:#172033;
            font-size:clamp(2.1rem,5vw,4rem);
            line-height:1.02;
            letter-spacing:-.055em;
            margin:15px 0 12px;
        }

        .hero p {
            max-width:770px;
            color:#667085;
            font-size:1rem;
            margin:0;
        }

        .filter-title {
            color:#172033;
            font-weight:900;
            font-size:1rem;
            margin-bottom:2px;
        }

        .filter-sub {
            color:#7a8393;
            font-size:.82rem;
            margin-bottom:12px;
        }

        .summary-row {
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:12px;
            margin:18px 0 14px;
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
    Read a published/public Google Sheet tab as CSV.
    No Streamlit login or service account is used.
    """
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
            "Pastikan nama tab betul dan tab itu boleh dibaca melalui link Google Sheet."
        ) from exc

    # Clean column names
    df.columns = [str(col).strip() for col in df.columns]

    # Remove fully blank rows
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
    """
    1) Exact normalized match.
    2) Partial match for longer aliases.
    """
    normalized_columns = {
        normalize_header(col): col
        for col in df.columns
    }

    # Exact
    for alias in COLUMN_ALIASES[key]:
        normalized_alias = normalize_header(alias)
        if normalized_alias in normalized_columns:
            return normalized_columns[normalized_alias]

    # Partial
    for alias in COLUMN_ALIASES[key]:
        normalized_alias = normalize_header(alias)

        if len(normalized_alias) < 4:
            continue

        for normalized_col, original_col in normalized_columns.items():
            if (
                normalized_alias in normalized_col
                or normalized_col in normalized_alias
            ):
                return original_col

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


def safe_html(value, fallback="-"):
    return html.escape(clean_text(value, fallback))


def get_value(row, column, fallback="-"):
    if not column:
        return fallback

    return clean_text(
        row.get(column, ""),
        fallback,
    )


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

    value = str(value).strip()

    if not value:
        return None

    # Examples handled:
    # RM35, RM 35.00, 35, 35.50
    cleaned = re.sub(r"[^0-9.]", "", value)

    try:
        return float(cleaned)
    except (TypeError, ValueError):
        return None


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
            Gunakan filter untuk cari perjalanan mengikut kawasan, tarikh,
            jenis trip, penumpang atau tambang. Jika berminat, WhatsApp
            admin SheGO untuk claim job. Job hanya sah selepas admin
            memberi pengesahan.
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
        f"Pastikan Google Sheet mempunyai tab bernama **{SHEET_TAB}** "
        "dan data pada row pertama mempunyai tajuk column."
    )
    st.stop()


if jobs.empty:
    st.info("Belum ada job tersedia sekarang.")
    st.stop()


# Detect available columns
cols = {
    key: find_column(jobs, key)
    for key in COLUMN_ALIASES
}


# Pickup + destination are the only important fields for a useful job board.
if not cols["pickup"] and not cols["destination"]:
    st.error(
        "Saya tak dapat kesan column lokasi pickup atau destinasi dalam Google Sheet."
    )

    with st.expander("Lihat column yang app berjaya baca"):
        st.write(list(jobs.columns))

    st.info(
        "Contoh header yang disokong: `Pickup`, `Lokasi Ambil`, "
        "`Destinasi`, atau `Destination`."
    )
    st.stop()


# ============================================================
# STATUS LOGIC — STATUS COLUMN IS OPTIONAL
# ============================================================
public_jobs = jobs.copy()

if cols["status"]:
    normalized_status = (
        public_jobs[cols["status"]]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    # Blank status is also treated as visible.
    # This makes setup easier while the sheet is still new.
    public_jobs = public_jobs[
        normalized_status.isin(PUBLIC_STATUSES)
        | normalized_status.eq("")
    ].copy()


# ============================================================
# FILTER UI
# ============================================================
st.markdown(
    """
    <div class="filter-title">Cari job yang sesuai</div>
    <div class="filter-sub">Filter hanya akan muncul jika column tersebut ada dalam Google Sheet.</div>
    """,
    unsafe_allow_html=True,
)


with st.expander("🔎 Filter Job", expanded=True):

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        location_search = st.text_input(
            "Pickup / Destinasi",
            placeholder="Contoh: Ulu Tiram, JB, Senai...",
        ).strip().casefold()

    with row1_col2:
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

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
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

    with row2_col2:
        pax_options = unique_values(
            public_jobs,
            cols["pax"],
        )

        selected_pax = (
            st.multiselect(
                "Bilangan Penumpang",
                options=pax_options,
                placeholder="Semua",
            )
            if pax_options
            else []
        )

    # Fare filter
    fare_values = []

    if cols["fare"]:
        fare_values = [
            number
            for number in (
                fare_to_number(value)
                for value in public_jobs[cols["fare"]]
            )
            if number is not None
        ]

    min_fare_filter = None
    max_fare_filter = None

    if fare_values:
        fare_min = int(min(fare_values))
        fare_max = int(max(fare_values))

        st.markdown("**Julat Tambang**")

        if fare_min == fare_max:
            st.caption(f"Semua job yang ada sekarang: RM{fare_min}")
            min_fare_filter = float(fare_min)
            max_fare_filter = float(fare_max)
        else:
            fare_range = st.slider(
                "Tambang (RM)",
                min_value=fare_min,
                max_value=fare_max,
                value=(fare_min, fare_max),
            )

            min_fare_filter = float(fare_range[0])
            max_fare_filter = float(fare_range[1])

    action_col1, action_col2 = st.columns([1, 1])

    with action_col1:
        if st.button(
            "↻ Refresh Data",
            use_container_width=True,
        ):
            load_jobs.clear()
            st.rerun()

    with action_col2:
        st.caption(
            "Data refresh automatik setiap ±30 saat."
        )


# ============================================================
# APPLY FILTERS
# ============================================================
filtered_jobs = public_jobs.copy()


# Pickup / destination search
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
    numeric_fare = filtered_jobs[cols["fare"]].apply(
        fare_to_number
    )

    filtered_jobs = filtered_jobs[
        numeric_fare.isna()
        |
        numeric_fare.between(
            min_fare_filter,
            max_fare_filter,
        )
    ]


# ============================================================
# SUMMARY
# ============================================================
st.markdown(
    f"""
    <div class="summary-row">
        <span class="count-pill">
            🚘 {len(filtered_jobs)} job tersedia
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)


if filtered_jobs.empty:
    st.info(
        "Tiada job yang sepadan dengan filter anda. "
        "Cuba ubah atau kosongkan filter."
    )
    st.stop()


# ============================================================
# JOB CARDS
# ============================================================
for position, (index, row) in enumerate(
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
        "Semak dengan admin",
    )

    pickup_time = get_value(
        row,
        cols["time"],
        "Semak dengan admin",
    )

    pax = get_value(
        row,
        cols["pax"],
        "Tidak dinyatakan",
    )

    trip_type = get_value(
        row,
        cols["trip_type"],
        "Tidak dinyatakan",
    )

    baggage = get_value(
        row,
        cols["baggage"],
        "Tidak dinyatakan",
    )

    notes = get_value(
        row,
        cols["notes"],
        "Tiada",
    )

    fare = get_value(
        row,
        cols["fare"],
        "Semak dengan admin",
    )

    with st.container(border=True):

        left, right = st.columns(
            [4, 1],
            vertical_alignment="top",
        )

        with left:
            st.markdown(
                f"""
                <div class="job-id">{safe_html(booking_id)}</div>
                <span class="open-pill">● TERSEDIA</span>
                """,
                unsafe_allow_html=True,
            )

        with right:
            fare_number = fare_to_number(fare)

            if fare_number is not None:
                fare_display = f"RM {fare_number:,.2f}"
            else:
                fare_display = safe_html(fare)

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
                <div class="route-value">
                    📍 {safe_html(pickup)}
                </div>

                <div class="route-line"></div>

                <div class="route-label">DESTINASI</div>
                <div class="route-value">
                    🏁 {safe_html(destination)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        info1, info2, info3 = st.columns(3)

        with info1:
            st.markdown(
                f"**📅 Tarikh**  \n{trip_date}"
            )

        with info2:
            st.markdown(
                f"**🕐 Masa Pickup**  \n{pickup_time}"
            )

        with info3:
            st.markdown(
                f"**👥 Penumpang**  \n{pax}"
            )

        detail1, detail2 = st.columns(2)

        with detail1:
            st.markdown(
                f"**🚗 Jenis Trip**  \n{trip_type}"
            )

        with detail2:
            st.markdown(
                f"**🧳 Bagasi**  \n{baggage}"
            )

        if notes not in {
            "-",
            "Tiada",
            "Tidak dinyatakan",
        }:
            st.markdown(
                f"**📝 Nota:** {notes}"
            )

        st.markdown(
            """
            <div class="privacy">
                🔒 Nama dan nombor telefon pelanggan tidak dipaparkan
                pada Driver Board. Maklumat lanjut akan diberikan selepas
                admin mengesahkan driver untuk job ini.
            </div>
            """,
            unsafe_allow_html=True,
        )

        whatsapp_message = (
            f"Hi Admin SheGO, saya berminat nak claim job {booking_id}.\n\n"
            f"📍 Pickup: {pickup}\n"
            f"🏁 Destinasi: {destination}\n"
            f"📅 Tarikh: {trip_date}\n"
            f"🕐 Masa: {pickup_time}\n"
            f"👥 Penumpang: {pax}\n"
            f"🚗 Jenis trip: {trip_type}\n"
            f"💰 Tambang: {fare}\n\n"
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
        💡 <b>Nota:</b> Job yang dipaparkan tertakluk kepada ketersediaan.
        Claim melalui WhatsApp belum bermaksud job telah diberikan kepada
        anda sehingga mendapat pengesahan daripada admin SheGO.
    </div>
    """,
    unsafe_allow_html=True,
)
