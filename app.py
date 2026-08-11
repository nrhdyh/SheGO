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
# WHITE THEME
# ============================================================
st.markdown(
    """
    <style>
        #MainMenu {visibility:hidden;}
        footer {visibility:hidden;}

        html, body, [data-testid="stAppViewContainer"], .stApp {
            background:#ffffff !important;
        }

        header[data-testid="stHeader"] {
            background:rgba(255,255,255,.96) !important;
            border-bottom:1px solid #eeeeee;
        }

        .block-container {
            max-width:1180px;
            padding-top:1.25rem;
            padding-bottom:5rem;
        }

        .topbar {
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:16px;
            margin-bottom:20px;
        }

        .brand {
            display:flex;
            align-items:center;
            gap:12px;
        }

        .logo {
            width:46px;
            height:46px;
            border-radius:14px;
            display:grid;
            place-items:center;
            color:white;
            font-size:21px;
            font-weight:900;
            background:#e95d8b;
            box-shadow:0 8px 22px rgba(233,93,139,.18);
        }

        .brand-title {
            font-size:1.5rem;
            font-weight:900;
            letter-spacing:-.04em;
            color:#171717;
            line-height:1;
        }

        .brand-title span {
            color:#e95d8b;
        }

        .brand-sub {
            color:#777;
            font-size:.82rem;
            margin-top:5px;
        }

        .hero {
            padding:32px;
            border-radius:24px;
            border:1px solid #ececec;
            background:#ffffff;
            box-shadow:0 10px 30px rgba(0,0,0,.04);
            margin-bottom:24px;
        }

        .kicker {
            display:inline-flex;
            align-items:center;
            gap:7px;
            border-radius:999px;
            padding:7px 12px;
            background:#fff3f7;
            border:1px solid #f5d9e3;
            color:#c74773;
            font-weight:850;
            font-size:.76rem;
            letter-spacing:.07em;
        }

        .hero h1 {
            max-width:760px;
            color:#171717;
            font-size:clamp(2rem,5vw,3.6rem);
            line-height:1.04;
            letter-spacing:-.05em;
            margin:15px 0 12px;
        }

        .hero p {
            max-width:790px;
            color:#666;
            font-size:1rem;
            margin:0;
        }

        .section-title {
            font-size:1.05rem;
            color:#171717;
            font-weight:900;
            margin:8px 0 3px;
        }

        .section-sub {
            color:#777;
            font-size:.84rem;
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
            background:#fff3f7;
            border:1px solid #f1d7e1;
            color:#c74773;
            padding:8px 13px;
            border-radius:999px;
            font-size:.84rem;
            font-weight:850;
        }

        .job-id {
            font-weight:900;
            color:#171717;
            font-size:1.2rem;
            letter-spacing:-.02em;
        }

        .open-pill {
            display:inline-flex;
            align-items:center;
            gap:6px;
            color:#147b58;
            background:#edf9f3;
            border:1px solid #d8efe4;
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
            color:#888;
            font-size:.72rem;
            font-weight:800;
            letter-spacing:.06em;
        }

        .fare strong {
            display:block;
            color:#171717;
            font-size:1.35rem;
            line-height:1.1;
            margin-top:3px;
        }

        .route-card {
            background:#fafafa;
            border:1px solid #ececec;
            border-radius:16px;
            padding:16px 18px;
            margin:14px 0 16px;
        }

        .route-label {
            color:#888;
            font-size:.70rem;
            font-weight:850;
            letter-spacing:.07em;
        }

        .route-value {
            color:#171717;
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
            border-radius:12px;
            background:#fafafa;
            border:1px solid #ebebeb;
            color:#666;
            font-size:.82rem;
        }

        .footer-note {
            margin-top:26px;
            padding:14px 16px;
            border-radius:14px;
            background:#fffaf0;
            border:1px solid #eee1c4;
            color:#755a31;
            font-size:.83rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background:#ffffff;
            border:1px solid #ececec !important;
            border-radius:20px !important;
            box-shadow:0 8px 22px rgba(0,0,0,.035);
            overflow:hidden;
        }

        .stLinkButton > a,
        .stButton > button {
            border-radius:12px !important;
            min-height:44px;
            font-weight:850 !important;
        }

        div[data-testid="stDataFrame"] {
            border:1px solid #ececec;
            border-radius:14px;
            overflow:hidden;
            background:#fff;
        }

        @media (max-width:720px) {
            .block-container {
                padding-left:.9rem;
                padding-right:.9rem;
                padding-top:.8rem;
            }

            .hero {
                padding:22px 18px;
                border-radius:20px;
            }

            .hero h1 {
                font-size:2.15rem;
            }

            .logo {
                width:42px;
                height:42px;
                border-radius:12px;
            }

            .fare {
                text-align:left;
                margin-top:8px;
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
# COLUMN DETECTION
# ============================================================
COLUMN_ALIASES = {
    "booking_id": [
        "Booking ID", "Job ID", "ID Tempahan", "No Tempahan",
        "No. Tempahan", "ID"
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
        "Tarikh", "Tarikh Perjalanan", "Tarikh Tempahan",
        "Trip Date", "Date"
    ],
    "time": [
        "Masa", "Masa Pickup", "Masa Ambil",
        "Waktu Pickup", "Pickup Time", "Time"
    ],
    "pax": [
        "Penumpang", "Bilangan Penumpang", "Jumlah Penumpang",
        "Pax", "No. of Passengers"
    ],
    "trip_type": [
        "Jenis Trip", "Jenis Perjalanan", "Trip Type", "Jenis Tempahan"
    ],
    "baggage": [
        "Bagasi", "Maklumat Bagasi", "Luggage"
    ],
    "notes": [
        "Nota", "Nota Tambahan", "Catatan", "Remarks", "Additional Notes"
    ],
    "fare": [
        "Tambang (RM)", "Tambang", "Harga", "Fare", "Fare (RM)", "Price"
    ],
}


def normalize_header(value):
    value = str(value).strip().casefold()
    value = re.sub(r"[\s_\-()/.:]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def find_column(df, key):
    normalized_columns = {
        normalize_header(col): col for col in df.columns
    }

    for alias in COLUMN_ALIASES[key]:
        n_alias = normalize_header(alias)
        if n_alias in normalized_columns:
            return normalized_columns[n_alias]

    for alias in COLUMN_ALIASES[key]:
        n_alias = normalize_header(alias)
        if len(n_alias) < 4:
            continue

        for n_col, original_col in normalized_columns.items():
            if n_alias in n_col or n_col in n_alias:
                return original_col

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


def safe_html(value, fallback="-"):
    return html.escape(clean_text(value, fallback))


def get_value(row, column, fallback="-"):
    if not column:
        return fallback
    return clean_text(row.get(column, ""), fallback)


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

    cleaned = re.sub(r"[^0-9.]", "", str(value).strip())

    if not cleaned:
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


# ============================================================
# HEADER
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


st.markdown(
    """
    <section class="hero">
        <span class="kicker">🚗 SHEGO • JOB TERSEDIA</span>
        <h1>Pilih perjalanan yang sesuai dengan anda.</h1>
        <p>
            Cari job mengikut lokasi, tarikh, jenis perjalanan,
            bilangan penumpang dan tambang. Tekan WhatsApp Admin
            jika berminat untuk claim job.
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
    st.error(
        "Column Pickup / Destinasi tak dapat dikesan."
    )

    with st.expander("Column yang app berjaya baca"):
        st.write(list(jobs.columns))

    st.stop()


# ============================================================
# STATUS
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
# FILTERS
# ============================================================
st.markdown(
    """
    <div class="section-title">Filter Job</div>
    <div class="section-sub">Gunakan filter di bawah untuk cari job yang sesuai.</div>
    """,
    unsafe_allow_html=True,
)


with st.container(border=True):

    c1, c2 = st.columns(2)

    with c1:
        location_search = st.text_input(
            "Pickup / Destinasi",
            placeholder="Contoh: Ulu Tiram, JB, Senai...",
        ).strip().casefold()

    with c2:
        date_options = unique_values(public_jobs, cols["date"])

        selected_dates = (
            st.multiselect(
                "Tarikh",
                options=date_options,
                placeholder="Semua tarikh",
            )
            if date_options
            else []
        )

    c3, c4 = st.columns(2)

    with c3:
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

    with c4:
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
        fmin = int(min(fare_values))
        fmax = int(max(fare_values))

        if fmin == fmax:
            st.caption(f"Tambang semasa: RM{fmin}")
            min_fare_filter = float(fmin)
            max_fare_filter = float(fmax)
        else:
            fare_range = st.slider(
                "Julat Tambang (RM)",
                min_value=fmin,
                max_value=fmax,
                value=(fmin, fmax),
            )

            min_fare_filter = float(fare_range[0])
            max_fare_filter = float(fare_range[1])

    if st.button(
        "↻ Refresh Data",
        use_container_width=True,
    ):
        load_jobs.clear()
        st.rerun()


# ============================================================
# APPLY FILTERS
# ============================================================
filtered_jobs = public_jobs.copy()


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


if selected_dates and cols["date"]:
    filtered_jobs = filtered_jobs[
        filtered_jobs[cols["date"]]
        .astype(str)
        .str.strip()
        .isin(selected_dates)
    ]


if selected_trip_types and cols["trip_type"]:
    filtered_jobs = filtered_jobs[
        filtered_jobs[cols["trip_type"]]
        .astype(str)
        .str.strip()
        .isin(selected_trip_types)
    ]


if selected_pax and cols["pax"]:
    filtered_jobs = filtered_jobs[
        filtered_jobs[cols["pax"]]
        .astype(str)
        .str.strip()
        .isin(selected_pax)
    ]


if (
    cols["fare"]
    and min_fare_filter is not None
    and max_fare_filter is not None
):
    fare_num = filtered_jobs[cols["fare"]].apply(
        fare_to_number
    )

    filtered_jobs = filtered_jobs[
        fare_num.isna()
        |
        fare_num.between(
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
        "Tiada job yang sepadan dengan filter anda."
    )
    st.stop()


# ============================================================
# JOB TABLE
# ============================================================
st.markdown(
    """
    <div class="section-title">Senarai Job</div>
    <div class="section-sub">Ringkasan semua job yang sepadan dengan filter.</div>
    """,
    unsafe_allow_html=True,
)


table_data = pd.DataFrame(index=filtered_jobs.index)


def add_table_col(display_name, key):
    source_col = cols.get(key)

    if source_col:
        table_data[display_name] = (
            filtered_jobs[source_col]
            .fillna("")
            .astype(str)
            .str.strip()
        )


add_table_col("Booking ID", "booking_id")
add_table_col("Pickup", "pickup")
add_table_col("Destinasi", "destination")
add_table_col("Tarikh", "date")
add_table_col("Masa", "time")
add_table_col("Penumpang", "pax")
add_table_col("Jenis Trip", "trip_type")
add_table_col("Tambang (RM)", "fare")


if "Booking ID" not in table_data.columns:
    table_data.insert(
        0,
        "Booking ID",
        [
            f"SG-{i+1:05d}"
            for i in range(len(table_data))
        ],
    )


st.dataframe(
    table_data.reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# DETAILED JOB CARDS
# ============================================================
st.markdown(
    """
    <div class="section-title" style="margin-top:24px;">Detail Job</div>
    <div class="section-sub">Tekan WhatsApp Admin pada job yang anda berminat.</div>
    """,
    unsafe_allow_html=True,
)


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
                <div class="route-value">📍 {safe_html(pickup)}</div>

                <div class="route-line"></div>

                <div class="route-label">DESTINASI</div>
                <div class="route-value">🏁 {safe_html(destination)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        i1, i2, i3 = st.columns(3)

        with i1:
            st.markdown(f"**📅 Tarikh**  \n{trip_date}")

        with i2:
            st.markdown(f"**🕐 Masa Pickup**  \n{pickup_time}")

        with i3:
            st.markdown(f"**👥 Penumpang**  \n{pax}")

        d1, d2 = st.columns(2)

        with d1:
            st.markdown(f"**🚗 Jenis Trip**  \n{trip_type}")

        with d2:
            st.markdown(f"**🧳 Bagasi**  \n{baggage}")

        if notes not in {
            "-",
            "Tiada",
            "Tidak dinyatakan",
        }:
            st.markdown(f"**📝 Nota:** {notes}")

        st.markdown(
            """
            <div class="privacy">
                🔒 Nama dan nombor telefon pelanggan tidak dipaparkan.
                Maklumat lanjut akan diberikan selepas admin mengesahkan
                driver untuk job tersebut.
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
        💡 <b>Nota:</b> Claim melalui WhatsApp belum bermaksud job telah
        diberikan kepada anda. Sila tunggu pengesahan daripada admin SheGO.
    </div>
    """,
    unsafe_allow_html=True,
)
