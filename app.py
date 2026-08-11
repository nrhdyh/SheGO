import hmac
from pathlib import Path
from urllib.parse import quote
from datetime import datetime

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
# CONFIG
# ============================================================
STATUS_OPTIONS = [
    "Baru",
    "Open",
    "Sedang Diproses",
    "Assigned",
    "Completed",
    "Cancelled",
]

INTERNAL_COLUMNS = [
    "Booking ID",
    "Status",
    "Tambang (RM)",
    "Pemandu Ditugaskan",
    "Nota Admin",
    "Updated At",
]

CUSTOMER_COLUMNS = {
    "name": "Nama Penuh",
    "phone": "Nombor WhatsApp",
    "for_whom": "Tempahan ini untuk siapa?",
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

# ============================================================
# STYLE
# ============================================================
st.markdown(
    """
    <style>
        .stApp { background: #fffafc; }
        .block-container { max-width: 1180px; padding-top: 1.4rem; padding-bottom: 4rem; }
        [data-testid="stSidebar"] { background: #fff7fa; }

        .shego-brand {
            display:flex; align-items:center; gap:12px; margin-bottom:6px;
        }
        .shego-wordmark {
            font-weight:800; font-size:1.65rem; letter-spacing:-0.04em; color:#172033;
        }
        .shego-wordmark span { color:#d84f7d; }
        .subtle { color:#667085; font-size:.95rem; }

        .hero-box {
            background: radial-gradient(circle at 85% 20%, #ffd9e6 0, transparent 32%),
                        linear-gradient(135deg, #fff 0%, #fff3f7 100%);
            border:1px solid #f1dce4; border-radius:28px; padding:28px;
            margin: 8px 0 24px 0; box-shadow:0 12px 35px rgba(52,31,43,.06);
        }
        .hero-eyebrow { color:#b83c67; font-size:.82rem; font-weight:800; letter-spacing:.04em; }
        .hero-title { color:#172033; font-size:clamp(2rem,4vw,3.4rem); line-height:1.05; font-weight:800; letter-spacing:-.045em; margin:.35rem 0 .7rem; }
        .hero-copy { color:#667085; max-width:720px; font-size:1.02rem; }

        .job-count {
            display:inline-block; background:#fff0f5; color:#b83c67; border:1px solid #f2d1dd;
            border-radius:999px; padding:6px 11px; font-weight:800; font-size:.82rem;
        }
        .status-open {
            display:inline-block; background:#eaf8f1; color:#157f5b; border-radius:999px;
            padding:5px 10px; font-weight:800; font-size:.78rem;
        }
        .route-text { font-size:1.1rem; font-weight:800; color:#172033; }
        .muted-small { color:#667085; font-size:.88rem; }
        .privacy-note {
            background:#f8f9fb; border:1px solid #e9eaee; border-radius:16px;
            padding:12px 14px; color:#667085; font-size:.88rem;
        }
        .admin-note {
            background:#fff4e8; border:1px solid #f3d9bb; border-radius:14px;
            padding:12px 14px; color:#80532d; font-size:.9rem;
        }
        div[data-testid="stMetric"] {
            background:white; border:1px solid #eee3e8; padding:12px 16px;
            border-radius:18px;
        }
        .stButton > button, .stLinkButton > a {
            border-radius:14px !important; font-weight:800 !important;
        }
        @media (max-width: 640px) {
            .block-container { padding-left:1rem; padding-right:1rem; padding-top:.9rem; }
            .hero-box { padding:21px 18px; border-radius:22px; }
            .hero-title { font-size:2.15rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GOOGLE SHEETS
# ============================================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
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
    if "google_sheet" not in st.secrets or "spreadsheet_id" not in st.secrets["google_sheet"]:
        raise RuntimeError("Secret google_sheet.spreadsheet_id belum diset.")

    gc = get_google_client()
    return gc.open_by_key(st.secrets["google_sheet"]["spreadsheet_id"])


def find_booking_worksheet():
    ss = get_spreadsheet()
    for ws in ss.worksheets():
        headers = ws.row_values(1)
        if CUSTOMER_COLUMNS["pickup"] in headers and CUSTOMER_COLUMNS["destination"] in headers:
            return ws
    raise RuntimeError(
        "Tak jumpa sheet response booking. Pastikan spreadsheet ID ialah Google Sheet response SheGO Customer Booking Form."
    )


def load_raw_sheet(ws):
    values = ws.get_all_values()
    if not values:
        return [], []
    headers = values[0]
    rows = values[1:]
    return headers, rows


def rows_to_dataframe(headers, rows):
    normalized = []
    for i, row in enumerate(rows, start=2):
        padded = row + [""] * max(0, len(headers) - len(row))
        item = dict(zip(headers, padded[: len(headers)]))
        item["__row_number"] = i
        normalized.append(item)
    return pd.DataFrame(normalized)


def load_bookings():
    ws = find_booking_worksheet()
    headers, rows = load_raw_sheet(ws)
    return ws, headers, rows_to_dataframe(headers, rows)


def ensure_admin_columns(ws):
    headers = ws.row_values(1)
    changed = False
    for col in INTERNAL_COLUMNS:
        if col not in headers:
            ws.update_cell(1, len(headers) + 1, col)
            headers.append(col)
            changed = True
    return headers, changed


def initialize_booking_defaults(ws, headers, df):
    if df.empty:
        return

    col_index = {name: i + 1 for i, name in enumerate(headers)}

    for _, row in df.iterrows():
        row_num = int(row["__row_number"])
        booking_id = str(row.get("Booking ID", "")).strip()
        status = str(row.get("Status", "")).strip()

        if not booking_id:
            ws.update_cell(row_num, col_index["Booking ID"], f"SG-{row_num:05d}")

        if not status:
            ws.update_cell(row_num, col_index["Status"], "Baru")


def safe_value(row, column, fallback="-"):
    value = row.get(column, "")
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def booking_id_for_row(row):
    existing = safe_value(row, "Booking ID", "")
    if existing:
        return existing
    return f"SG-{int(row['__row_number']):05d}"


# ============================================================
# AUTH HELPERS
# ============================================================
def secret_value(name, default=""):
    try:
        return str(st.secrets[name])
    except Exception:
        return default


def login_gate(secret_name, session_key, title, help_text):
    if st.session_state.get(session_key, False):
        return True

    st.subheader(title)
    st.caption(help_text)
    password = st.text_input("Kod akses", type="password", key=f"{session_key}_input")

    if st.button("Masuk", type="primary", use_container_width=True, key=f"{session_key}_button"):
        expected = secret_value(secret_name)
        if expected and hmac.compare_digest(password, expected):
            st.session_state[session_key] = True
            st.rerun()
        else:
            st.error("Kod akses tidak betul.")
    return False


# ============================================================
# BRAND HEADER
# ============================================================
def render_brand():
    col1, col2 = st.columns([1, 5])
    with col1:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=96)
    with col2:
        st.markdown(
            '<div class="shego-brand"><div class="shego-wordmark"><span>She</span>GO Driver Board</div></div>'
            '<div class="subtle">Job board untuk rangkaian pemandu wanita SheGO.</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# DRIVER VIEW
# ============================================================
def render_driver_view():
    if not login_gate(
        "DRIVER_PIN",
        "driver_authenticated",
        "Akses Pemandu",
        "Masukkan kod akses yang diberikan oleh admin SheGO.",
    ):
        return

    st.markdown(
        """
        <div class="hero-box">
          <div class="hero-eyebrow">SHEGO • JOB TERSEDIA</div>
          <div class="hero-title">Pilih trip yang sesuai dengan anda.</div>
          <div class="hero-copy">Semak pickup, destinasi dan masa perjalanan. Jika berminat, tekan butang WhatsApp. Admin SheGO akan sahkan siapa yang menerima job tersebut.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        _, _, df = load_bookings()
    except Exception as exc:
        st.error(f"Tak dapat baca Google Sheet: {exc}")
        return

    if df.empty or "Status" not in df.columns:
        st.info("Belum ada job yang dibuka oleh admin.")
        return

    open_jobs = df[df["Status"].astype(str).str.strip().str.lower() == "open"].copy()

    # Search/filter
    top1, top2 = st.columns([3, 1])
    with top1:
        search = st.text_input(
            "Cari kawasan",
            placeholder="Contoh: Ulu Tiram, JB, Senai...",
        ).strip().lower()
    with top2:
        if st.button("↻ Refresh", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

    if search and not open_jobs.empty:
        pickup = open_jobs.get(CUSTOMER_COLUMNS["pickup"], pd.Series(dtype=str)).astype(str).str.lower()
        destination = open_jobs.get(CUSTOMER_COLUMNS["destination"], pd.Series(dtype=str)).astype(str).str.lower()
        open_jobs = open_jobs[pickup.str.contains(search, na=False) | destination.str.contains(search, na=False)]

    st.markdown(f'<span class="job-count">{len(open_jobs)} job tersedia</span>', unsafe_allow_html=True)
    st.write("")

    if open_jobs.empty:
        st.info("Tiada job yang available untuk carian ini sekarang.")
        return

    admin_whatsapp = secret_value("ADMIN_WHATSAPP")

    for _, row in open_jobs.iterrows():
        job_id = booking_id_for_row(row)
        pickup = safe_value(row, CUSTOMER_COLUMNS["pickup"])
        destination = safe_value(row, CUSTOMER_COLUMNS["destination"])
        date = safe_value(row, CUSTOMER_COLUMNS["date"])
        time = safe_value(row, CUSTOMER_COLUMNS["time"])
        pax = safe_value(row, CUSTOMER_COLUMNS["pax"])
        trip_type = safe_value(row, CUSTOMER_COLUMNS["trip_type"])
        baggage = safe_value(row, CUSTOMER_COLUMNS["baggage"])
        notes = safe_value(row, CUSTOMER_COLUMNS["notes"], "Tiada")
        return_time = safe_value(row, CUSTOMER_COLUMNS["return_time"], "-")
        fare = safe_value(row, "Tambang (RM)", "Belum dinyatakan")

        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"### {job_id}")
                st.markdown('<span class="status-open">● OPEN</span>', unsafe_allow_html=True)
            with c2:
                st.metric("Tambang", f"RM {fare}" if fare not in ["-", "Belum dinyatakan"] else fare)

            st.markdown(
                f'<div class="route-text">📍 {pickup}<br>↓<br>🏁 {destination}</div>',
                unsafe_allow_html=True,
            )
            st.write("")

            a, b, c = st.columns(3)
            a.markdown(f"**📅 Tarikh**  \n{date}")
            b.markdown(f"**🕐 Pickup**  \n{time}")
            c.markdown(f"**👥 Penumpang**  \n{pax}")

            d, e = st.columns(2)
            d.markdown(f"**🚗 Jenis trip**  \n{trip_type}")
            e.markdown(f"**🧳 Bagasi**  \n{baggage}")

            if return_time != "-":
                st.markdown(f"**↩️ Anggaran masa balik:** {return_time}")
            if notes != "Tiada":
                st.markdown(f"**📝 Nota pelanggan:** {notes}")

            st.markdown(
                '<div class="privacy-note">🔒 Nombor telefon pelanggan tidak dipaparkan di job board. Admin akan beri maklumat hubungan selepas job disahkan kepada pemandu.</div>',
                unsafe_allow_html=True,
            )

            msg = (
                f"Hi Admin SheGO, saya berminat nak ambil job {job_id}.\n\n"
                f"Pickup: {pickup}\n"
                f"Destinasi: {destination}\n"
                f"Tarikh: {date}\n"
                f"Masa: {time}\n\n"
                "Boleh semak sama ada job ini masih available?"
            )

            if admin_whatsapp:
                wa_url = f"https://wa.me/{admin_whatsapp}?text={quote(msg)}"
                st.link_button(
                    "💬 WhatsApp Admin untuk Claim Job",
                    wa_url,
                    type="primary",
                    use_container_width=True,
                )
            else:
                st.warning("ADMIN_WHATSAPP belum diset dalam Streamlit Secrets.")


# ============================================================
# ADMIN VIEW
# ============================================================
def render_admin_view():
    if not login_gate(
        "ADMIN_PASSWORD",
        "admin_authenticated",
        "Admin SheGO",
        "Hanya admin boleh buka, assign dan menukar status tempahan.",
    ):
        return

    try:
        ws = find_booking_worksheet()
        headers, _ = ensure_admin_columns(ws)
        _, raw_rows = load_raw_sheet(ws)
        df = rows_to_dataframe(headers, raw_rows)
        initialize_booking_defaults(ws, headers, df)

        # reload after initialization
        headers, raw_rows = load_raw_sheet(ws)
        df = rows_to_dataframe(headers, raw_rows)
    except Exception as exc:
        st.error(f"Tak dapat setup Google Sheet: {exc}")
        return

    st.markdown(
        """
        <div class="hero-box">
          <div class="hero-eyebrow">SHEGO • ADMIN</div>
          <div class="hero-title">Urus tempahan dari satu tempat.</div>
          <div class="hero-copy">Customer masih submit melalui Google Form. Admin hanya gunakan halaman ini untuk buka job kepada pemandu dan kemas kini status.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("Belum ada response customer.")
        return

    s1, s2, s3, s4 = st.columns(4)
    statuses = df["Status"].fillna("").astype(str)
    s1.metric("Jumlah", len(df))
    s2.metric("Baru", int((statuses == "Baru").sum()))
    s3.metric("Open", int((statuses == "Open").sum()))
    s4.metric("Assigned", int((statuses == "Assigned").sum()))

    st.subheader("Senarai Tempahan")

    view_cols = [
        "Booking ID",
        "Status",
        CUSTOMER_COLUMNS["name"],
        CUSTOMER_COLUMNS["pickup"],
        CUSTOMER_COLUMNS["destination"],
        CUSTOMER_COLUMNS["date"],
        CUSTOMER_COLUMNS["time"],
        "Tambang (RM)",
        "Pemandu Ditugaskan",
    ]
    existing_view_cols = [c for c in view_cols if c in df.columns]
    st.dataframe(df[existing_view_cols], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Edit Tempahan")

    booking_options = df["Booking ID"].astype(str).tolist()
    selected_id = st.selectbox("Pilih Booking ID", booking_options)
    selected = df[df["Booking ID"].astype(str) == selected_id].iloc[0]

    left, right = st.columns([1.15, 0.85])

    with left:
        st.markdown(f"### {selected_id}")
        st.markdown(f"**Customer:** {safe_value(selected, CUSTOMER_COLUMNS['name'])}")
        st.markdown(f"**WhatsApp:** {safe_value(selected, CUSTOMER_COLUMNS['phone'])}")
        st.markdown(f"**Pickup:** {safe_value(selected, CUSTOMER_COLUMNS['pickup'])}")
        st.markdown(f"**Destinasi:** {safe_value(selected, CUSTOMER_COLUMNS['destination'])}")
        st.markdown(
            f"**Tarikh / Masa:** {safe_value(selected, CUSTOMER_COLUMNS['date'])} • {safe_value(selected, CUSTOMER_COLUMNS['time'])}"
        )
        st.markdown(f"**Pax:** {safe_value(selected, CUSTOMER_COLUMNS['pax'])}")
        st.markdown(f"**Jenis Trip:** {safe_value(selected, CUSTOMER_COLUMNS['trip_type'])}")
        st.markdown(f"**Bagasi:** {safe_value(selected, CUSTOMER_COLUMNS['baggage'])}")
        st.markdown(f"**Nota Customer:** {safe_value(selected, CUSTOMER_COLUMNS['notes'], 'Tiada')}")

        phone = safe_value(selected, CUSTOMER_COLUMNS["phone"], "")
        if phone:
            clean_phone = "".join(ch for ch in phone if ch.isdigit())
            if clean_phone.startswith("0"):
                clean_phone = "60" + clean_phone[1:]
            customer_message = (
                f"Hi, ini SheGO. Kami sedang mengurus tempahan anda ({selected_id}). "
                "Kami akan maklumkan pemandu dan pengesahan tempahan sebaik sahaja tersedia."
            )
            st.link_button(
                "💬 WhatsApp Customer",
                f"https://wa.me/{clean_phone}?text={quote(customer_message)}",
                use_container_width=True,
            )

    with right:
        current_status = safe_value(selected, "Status", "Baru")
        current_index = STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 0

        with st.form("admin_update_form"):
            new_status = st.selectbox("Status", STATUS_OPTIONS, index=current_index)
            fare = st.text_input("Tambang (RM)", value=safe_value(selected, "Tambang (RM)", ""))
            assigned_driver = st.text_input(
                "Pemandu Ditugaskan",
                value=safe_value(selected, "Pemandu Ditugaskan", ""),
                placeholder="Contoh: Aina / SG-D001",
            )
            admin_note = st.text_area(
                "Nota Admin",
                value=safe_value(selected, "Nota Admin", ""),
                placeholder="Nota dalaman sahaja",
            )

            submitted = st.form_submit_button("Simpan Perubahan", type="primary", use_container_width=True)

        if submitted:
            headers = ws.row_values(1)
            col_index = {name: i + 1 for i, name in enumerate(headers)}
            row_num = int(selected["__row_number"])

            ws.update_cell(row_num, col_index["Status"], new_status)
            ws.update_cell(row_num, col_index["Tambang (RM)"], fare.strip())
            ws.update_cell(row_num, col_index["Pemandu Ditugaskan"], assigned_driver.strip())
            ws.update_cell(row_num, col_index["Nota Admin"], admin_note.strip())
            ws.update_cell(
                row_num,
                col_index["Updated At"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )

            st.success("Tempahan berjaya dikemas kini.")
            st.rerun()

    st.markdown(
        """
        <div class="admin-note">
        <b>Flow cadangan:</b> Baru → admin semak → Open → driver WhatsApp → Sedang Diproses → Assigned → Completed. 
        Hanya job berstatus <b>Open</b> akan muncul pada Driver Board.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# APP NAVIGATION
# ============================================================
render_brand()
st.write("")

page = st.sidebar.radio(
    "Menu",
    ["🚗 Job Pemandu", "🔐 Admin"],
    index=0,
)

if page == "🚗 Job Pemandu":
    render_driver_view()
else:
    render_admin_view()
