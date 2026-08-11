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

    # Row asal Google Sheet digunakan sebagai fallback Booking ID yang stabil.
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
st.title("🚗 SheGO Driver Board")
st.caption("Job pemandu wanita • Johor")

st.info(
    "Hanya job berstatus **Open** dipaparkan. "
    "Permintaan claim melalui WhatsApp masih tertakluk kepada pengesahan admin."
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
stat1, stat2, stat3 = st.columns(3)
with stat1:
    st.metric("Job Open", len(open_jobs))
with stat2:
    st.metric(
        "Tarikh Aktif",
        len(unique_values(open_jobs, cols["date"])) if cols["date"] else 0,
    )
with stat3:
    st.metric(
        "Jenis Trip",
        len(unique_values(open_jobs, cols["trip_type"])) if cols["trip_type"] else 0,
    )

st.divider()


# ============================================================
# FILTERS - NATIVE STREAMLIT ONLY
# ============================================================
st.subheader("Cari Job")
st.caption("Cari lokasi atau Booking ID, kemudian tapis jika perlu.")

location_search = st.text_input(
    "Pickup / Destinasi / Booking ID",
    placeholder="Contoh: Ulu Tiram, Senai, SG-001...",
    key="search_location",
).strip().casefold()

date_options = unique_values(open_jobs, cols["date"])
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

trip_options = unique_values(open_jobs, cols["trip_type"])
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

pax_options = unique_values(open_jobs, cols["pax"])
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

sort_option = st.selectbox(
    "Susun Job",
    options=[
        "Asal dari Google Sheet",
        "Tambang tertinggi",
        "Tambang terendah",
    ],
    key="sort_option",
)

if st.button("↻ Refresh Data", use_container_width=True):
    load_jobs.clear()
    st.rerun()

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
        filtered[cols["trip_type"]]
        .astype(str)
        .str.strip()
        .isin(selected_trip_types)
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
    filtered = filtered.sort_values(
        "_source_row",
        ascending=True,
        kind="stable",
    )


# ============================================================
# JOB TABLE - NATIVE STREAMLIT ONLY
# ============================================================
st.divider()
st.subheader("Senarai Job Open")
st.caption(
    f"{len(filtered)} job sepadan • Pada telefon, swipe table ke kiri/kanan untuk lihat semua maklumat."
)

if filtered.empty:
    st.warning("Tiada job yang sepadan dengan filter anda.")
    st.stop()

rows = []

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

    rows.append(
        {
            "Booking ID": booking_id,
            "Status": "OPEN",
            "Pickup": pickup,
            "Destinasi": destination,
            "Tarikh": trip_date,
            "Masa": pickup_time,
            "Pax": pax,
            "Jenis Trip": trip_type,
            "Bagasi": baggage,
            "Nota": notes,
            "Tambang": fare_display,
            "Claim": whatsapp_url,
        }
    )

job_table = pd.DataFrame(rows)

st.dataframe(
    job_table,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Booking ID": st.column_config.TextColumn(
            "Booking ID",
            width="small",
        ),
        "Status": st.column_config.TextColumn(
            "Status",
            width="small",
        ),
        "Pickup": st.column_config.TextColumn(
            "Pickup",
            width="medium",
        ),
        "Destinasi": st.column_config.TextColumn(
            "Destinasi",
            width="medium",
        ),
        "Tarikh": st.column_config.TextColumn(
            "Tarikh",
            width="small",
        ),
        "Masa": st.column_config.TextColumn(
            "Masa",
            width="small",
        ),
        "Pax": st.column_config.TextColumn(
            "Pax",
            width="small",
        ),
        "Jenis Trip": st.column_config.TextColumn(
            "Jenis Trip",
            width="small",
        ),
        "Bagasi": st.column_config.TextColumn(
            "Bagasi",
            width="small",
        ),
        "Nota": st.column_config.TextColumn(
            "Nota",
            width="medium",
        ),
        "Tambang": st.column_config.TextColumn(
            "Tambang",
            width="small",
        ),
        "Claim": st.column_config.LinkColumn(
            "Tindakan",
            display_text="Claim WhatsApp",
            width="medium",
        ),
    },
)

st.caption(
    "Tip telefon: swipe table secara mendatar untuk lihat kolum Tambang dan Claim WhatsApp."
)


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    "🔒 Nama dan nombor telefon pelanggan tidak dipaparkan pada Driver Board. "
    "Maklumat pelanggan hanya diberi selepas admin mengesahkan pemandu."
)

st.caption(
    "Flow: Open → Assigned → Completed. "
    "Cancelled digunakan jika tempahan dibatalkan."
)
