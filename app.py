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

/* Keep the page clean without fighting Streamlit too much */
.block-container {
    max-width: 1220px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
}

#MainMenu, footer { visibility: hidden; }

.shego-brand {
    display:flex;
    align-items:center;
    gap:12px;
    margin:4px 0 18px 0;
}
.shego-logo {
    width:44px;
    height:44px;
    border-radius:14px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#e85c8a;
    color:white;
    font-weight:900;
    font-size:20px;
}
.shego-name {
    font-size:1.45rem;
    font-weight:900;
    line-height:1.05;
    color:#171717;
}
.shego-name span { color:#e85c8a; }
.shego-sub {
    color:#777;
    font-size:.82rem;
    margin-top:4px;
}

.shego-hero {
    border:1px solid #ececec;
    border-radius:20px;
    padding:24px;
    margin-bottom:18px;
    background:linear-gradient(135deg,#ffffff 65%,#fff3f7 100%);
}
.shego-hero h1 {
    margin:0 0 8px 0;
    color:#171717;
    font-size:clamp(1.8rem,4vw,2.7rem);
    line-height:1.08;
    letter-spacing:-.035em;
}
.shego-hero p {
    margin:0;
    color:#666;
    line-height:1.65;
    max-width:850px;
}

.result-bar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin:12px 0 12px;
    flex-wrap:wrap;
}
.result-count {
    display:inline-flex;
    align-items:center;
    padding:7px 11px;
    border-radius:999px;
    background:#fff3f7;
    color:#c84672;
    border:1px solid #f2d6df;
    font-size:.82rem;
    font-weight:800;
}
.result-note {
    color:#858585;
    font-size:.78rem;
}

/* ---------------- Desktop table ---------------- */
.desktop-view { display:block; }
.mobile-view { display:none; }

.table-shell {
    width:100%;
    overflow-x:auto;
    border:1px solid #e7e7e7;
    border-radius:16px;
    background:#fff;
}
.job-table {
    width:100%;
    min-width:980px;
    border-collapse:collapse;
    background:#fff;
}
.job-table th {
    padding:12px 13px;
    text-align:left;
    background:#fafafa;
    border-bottom:1px solid #e7e7e7;
    color:#666;
    font-size:.74rem;
    white-space:nowrap;
}
.job-table td {
    padding:13px;
    border-bottom:1px solid #eeeeee;
    color:#242424;
    font-size:.84rem;
    vertical-align:middle;
}
.job-table tr:last-child td { border-bottom:none; }
.job-table tbody tr:hover { background:#fffafb; }
.booking-cell { font-weight:900; white-space:nowrap; }
.route-cell { min-width:180px; font-weight:650; }
.route-arrow-inline { color:#d46a91; margin:0 5px; }
.fare-cell { font-weight:900; white-space:nowrap; }
.status-pill {
    display:inline-flex;
    align-items:center;
    gap:5px;
    padding:5px 8px;
    border-radius:999px;
    background:#edf9f3;
    color:#147b58;
    border:1px solid #d5eee0;
    font-size:.68rem;
    font-weight:850;
    white-space:nowrap;
}
.claim-link {
    display:inline-flex;
    align-items:center;
    justify-content:center;
    padding:8px 11px;
    border-radius:9px;
    background:#e85c8a;
    color:white !important;
    text-decoration:none !important;
    font-size:.75rem;
    font-weight:800;
    white-space:nowrap;
}
.claim-link:hover { background:#cf4c77; }

/* ---------------- Tablet / phone cards ---------------- */
.mobile-cards {
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:13px;
}
.job-card {
    border:1px solid #e8e8e8;
    border-radius:17px;
    background:#fff;
    padding:16px;
    box-shadow:0 4px 15px rgba(0,0,0,.025);
}
.card-head {
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:10px;
    margin-bottom:12px;
}
.card-booking {
    color:#171717;
    font-size:1rem;
    font-weight:900;
}
.card-fare {
    color:#171717;
    font-size:1.05rem;
    font-weight:900;
    text-align:right;
}
.card-route {
    padding:12px;
    background:#fafafa;
    border:1px solid #eeeeee;
    border-radius:13px;
    margin-bottom:12px;
}
.card-label {
    color:#929292;
    font-size:.65rem;
    font-weight:850;
    letter-spacing:.05em;
    text-transform:uppercase;
}
.card-place {
    color:#1f1f1f;
    font-size:.91rem;
    font-weight:750;
    line-height:1.4;
    margin-top:2px;
}
.card-route-arrow {
    color:#d46a91;
    font-weight:900;
    margin:5px 0;
}
.card-meta {
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:8px;
    margin-bottom:10px;
}
.meta-item {
    border:1px solid #eeeeee;
    border-radius:11px;
    padding:9px 10px;
}
.meta-name {
    color:#8c8c8c;
    font-size:.64rem;
    font-weight:800;
    text-transform:uppercase;
}
.meta-value {
    margin-top:2px;
    color:#282828;
    font-size:.81rem;
    font-weight:650;
    overflow-wrap:anywhere;
}
.card-extra {
    color:#666;
    font-size:.78rem;
    line-height:1.55;
    margin:8px 0 12px;
}
.card-claim {
    display:flex;
    width:100%;
    box-sizing:border-box;
    align-items:center;
    justify-content:center;
    padding:10px 12px;
    border-radius:11px;
    background:#e85c8a;
    color:white !important;
    text-decoration:none !important;
    font-size:.8rem;
    font-weight:850;
}

@media (max-width:1024px) {
    .block-container {
        padding-left:1rem;
        padding-right:1rem;
        padding-top:.8rem;
    }
    .desktop-view { display:none !important; }
    .mobile-view { display:block !important; }
    .shego-hero { padding:20px; }
}

@media (max-width:640px) {
    .mobile-cards { grid-template-columns:1fr; }
    .shego-hero { padding:18px; border-radius:17px; }
    .shego-hero h1 { font-size:1.85rem; }
    .card-meta { grid-template-columns:repeat(2,minmax(0,1fr)); }
}

@media (max-width:390px) {
    .card-meta { grid-template-columns:1fr; }
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
    '<div class="shego-brand">'
    '<div class="shego-logo">S</div>'
    '<div><div class="shego-name"><span>She</span>GO</div>'
    '<div class="shego-sub">Driver Job Board • Johor</div></div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<section class="shego-hero">'
    '<h1>Cari trip yang sesuai dengan anda.</h1>'
    '<p>Hanya tempahan berstatus <b>Open</b> dipaparkan. '
    'Pemandu boleh pilih job dan hantar permohonan claim melalui WhatsApp. '
    'Job hanya dianggap assigned selepas admin mengesahkan.</p>'
    '</section>',
    unsafe_allow_html=True,
)


# ============================================================
# LIVE DATA BOARD
# Auto refresh every 2 minutes. Filters remain in session_state.
# ============================================================
@st.fragment(run_every=AUTO_REFRESH_INTERVAL)
def live_board():
    st.caption("🟢 Auto refresh setiap 2 minit • Tekan Refresh Data untuk kemas kini segera")

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
    # FILTERS
    # ============================================================
    st.subheader("Cari Job")
    st.caption("Cari lokasi atau Booking ID, kemudian tapis ikut tarikh, jenis trip atau penumpang.")

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
    st.divider()
    st.subheader("Senarai Job Open")

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
            f'<div><div class="card-booking">{bid}</div><div style="margin-top:6px"><span class="status-pill">● OPEN</span></div></div>'
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
    st.divider()
    st.caption(
        "🔒 Nama dan nombor telefon pelanggan tidak dipaparkan pada Driver Board. "
        "Maklumat pelanggan hanya diberi selepas admin mengesahkan pemandu."
    )
    st.caption(
        "Flow: Open → Assigned → Completed. Cancelled digunakan jika tempahan dibatalkan."
    )



live_board()
