import os
import math
import string
import io
import zipfile
import base64
import streamlit as st
import pandas as pd

# =====================================================
# PAGE CONFIG — must be first Streamlit call
# =====================================================
st.set_page_config(
    page_title="MIM Uploader · Inventory Split Engine",
    page_icon="🧡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================
# LOGO HELPER
# =====================================================
def get_logo_b64():
    logo_path = os.path.join(os.path.dirname(__file__), "Icon.webp")
    if os.path.isfile(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

LOGO_B64 = get_logo_b64()
LOGO_HTML = (
    f'<img src="data:image/webp;base64,{LOGO_B64}" class="nav-logo" alt="Instamart"/>'
    if LOGO_B64
    else '<span class="nav-logo-text">instamart</span>'
)

# =====================================================
# PREMIUM CSS
# =====================================================
st.markdown(
    """
<style>
/* ── Google Fonts ─────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Reset & Root ─────────────────────────────── */
:root {
    --bg-base:        #F0F2F5;
    --bg-card:        #FFFFFF;
    --border-orange:  #F15A22;
    --border-subtle:  #E8E8EA;
    --accent-orange:  #F15A22;
    --accent-blue:    #1849D6;
    --green:          #16A34A;
    --green-bg:       #F0FDF4;
    --green-border:   #BBF7D0;
    --red:            #DC2626;
    --red-bg:         #FEF2F2;
    --red-border:     #FECACA;
    --orange-bg:      #FFF7ED;
    --orange-border:  #FED7AA;
    --text-primary:   #0A0A0B;
    --text-secondary: #6B7280;
    --text-muted:     #9CA3AF;
    --shadow-sm:      0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04);
    --shadow-md:      0 4px 12px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.04);
    --shadow-lg:      0 8px 32px rgba(0,0,0,.10), 0 4px 8px rgba(0,0,0,.06);
    --radius-sm:      8px;
    --radius-md:      12px;
    --radius-lg:      16px;
    --font-main:      'DM Sans', sans-serif;
    --font-mono:      'DM Mono', monospace;
}

/* ── Global Overrides ─────────────────────────── */
html, body, [class*="css"] {
    font-family: var(--font-main) !important;
    color: var(--text-primary) !important;
}

/* Remove Streamlit top padding */
.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}

/* App background */
.stApp {
    background: linear-gradient(145deg, #ECEEF2 0%, #F4F5F8 50%, #EAECF0 100%) !important;
    min-height: 100vh;
}

/* Hide default header & menu */
#MainMenu, header[data-testid="stHeader"], footer { display: none !important; }

/* ── Navbar ───────────────────────────────────── */
.nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    height: 62px;
    background: #FFFFFF;
    border-bottom: 1px solid var(--border-subtle);
    box-shadow: 0 1px 0 rgba(0,0,0,.06);
    position: sticky;
    top: 0;
    z-index: 999;
    margin-left: -1rem;
    margin-right: -1rem;
}

.nav-left { display: flex; align-items: center; gap: 14px; }

.nav-logo {
    height: 38px;
    width: 38px;
    border-radius: 10px;
    object-fit: cover;
    box-shadow: var(--shadow-sm);
}

.nav-logo-text {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--accent-blue);
    letter-spacing: -0.5px;
}

.nav-title-block { display: flex; flex-direction: column; gap: 1px; }

.nav-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.2px;
    line-height: 1.2;
}

.nav-subtitle {
    font-size: 0.7rem;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
}

.nav-badge {
    display: inline-flex;
    align-items: center;
    padding: 5px 14px;
    background: var(--accent-orange);
    color: #fff !important;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    border-radius: 6px;
}

/* ── Content Layout ───────────────────────────── */
.page-body {
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 1.5rem;
    padding: 1.5rem 1rem 2rem;
    align-items: start;
}

/* ── Card ─────────────────────────────────────── */
.card {
    background: linear-gradient(160deg, #FFFFFF 0%, #FAFAFA 100%);
    border: 1.5px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.card-accent {
    border-left: 3px solid var(--accent-orange);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 1.25rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border-subtle);
}

.card-header-icon {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent-orange);
    flex-shrink: 0;
}

.card-header-text {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: var(--text-secondary) !important;
}

/* ── Stat Cards ───────────────────────────────── */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
}

.stat-card {
    background: linear-gradient(145deg, #FFFFFF, #F9FAFB);
    border: 1.5px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent-orange);
    border-radius: var(--radius-md) var(--radius-md) 0 0;
}

.stat-label {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted) !important;
    margin-bottom: 0.4rem;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent-orange) !important;
    line-height: 1;
    letter-spacing: -1px;
}

/* ── Notification Boxes ───────────────────────── */
.notif {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 0.9rem 1.1rem;
    border-radius: var(--radius-md);
    margin-bottom: 0.75rem;
    font-size: 0.82rem;
    line-height: 1.5;
    font-weight: 500;
}

.notif-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }

.notif-success {
    background: var(--green-bg);
    border: 1.5px solid var(--green-border);
    color: var(--green) !important;
}

.notif-error {
    background: var(--red-bg);
    border: 1.5px solid var(--red-border);
    color: var(--red) !important;
}

.notif-warn {
    background: var(--orange-bg);
    border: 1.5px solid var(--orange-border);
    color: #C2410C !important;
}

.notif-info {
    background: #EFF6FF;
    border: 1.5px solid #BFDBFE;
    color: #1D4ED8 !important;
}

/* ── Split Log ────────────────────────────────── */
.split-row {
    background: #FAFAFA;
    border: 1.5px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    font-size: 0.82rem;
}

.split-row-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.split-store {
    font-weight: 700;
    font-size: 0.85rem;
    color: var(--text-primary) !important;
}

.split-meta {
    font-size: 0.75rem;
    color: var(--text-muted) !important;
    font-family: var(--font-mono);
}

.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-right: 4px;
}

.tag-red { background: var(--red-bg); color: var(--red) !important; border: 1px solid var(--red-border); }
.tag-orange { background: var(--orange-bg); color: #C2410C !important; border: 1px solid var(--orange-border); }

.variant-pill {
    display: inline-block;
    padding: 2px 10px;
    background: #F3F4F6;
    border: 1px solid #E5E7EB;
    border-radius: 20px;
    font-size: 0.72rem;
    font-family: var(--font-mono);
    color: var(--text-secondary) !important;
    margin: 2px 3px 2px 0;
}

/* ── File Row ─────────────────────────────────── */
.file-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(90deg, #FAFAFA, #FFFFFF);
    border: 1.5px solid var(--border-subtle);
    border-left: 3px solid var(--accent-orange);
    border-radius: var(--radius-sm);
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.5rem;
    font-size: 0.82rem;
}

.file-name {
    font-weight: 600;
    color: var(--text-primary) !important;
    font-family: var(--font-mono);
    font-size: 0.8rem;
}

.file-rows-badge {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-secondary) !important;
    background: #F3F4F6;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid #E5E7EB;
}

/* ── Streamlit widget overrides ───────────────── */
div[data-testid="stNumberInput"] label,
div[data-testid="stFileUploader"] label,
div[data-testid="stExpander"] summary p {
    font-family: var(--font-main) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    color: var(--text-secondary) !important;
    text-transform: uppercase;
}

div[data-testid="stNumberInput"] input {
    font-family: var(--font-mono) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    border: 1.5px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    background: #FAFAFA !important;
}

div[data-testid="stNumberInput"] input:focus {
    border-color: var(--accent-orange) !important;
    box-shadow: 0 0 0 3px rgba(241,90,34,0.08) !important;
}

/* Upload zone */
div[data-testid="stFileUploader"] > div:first-child {
    border: 2px dashed #D1D5DB !important;
    border-radius: var(--radius-md) !important;
    background: #FAFAFA !important;
    transition: all .2s ease;
}

div[data-testid="stFileUploader"] > div:first-child:hover {
    border-color: var(--accent-orange) !important;
    background: var(--orange-bg) !important;
}

/* Buttons */
div[data-testid="stButton"] button {
    font-family: var(--font-main) !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.3px;
    border-radius: var(--radius-sm) !important;
    transition: all .15s ease;
}

div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #F15A22 0%, #E04A15 100%) !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(241,90,34,0.35) !important;
    color: #fff !important;
}

div[data-testid="stButton"] button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(241,90,34,0.45) !important;
}

div[data-testid="stDownloadButton"] button {
    font-family: var(--font-main) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid var(--border-subtle) !important;
    background: #FFFFFF !important;
    color: var(--text-primary) !important;
    width: 100%;
    transition: all .15s ease;
}

div[data-testid="stDownloadButton"] button:hover {
    border-color: var(--accent-orange) !important;
    color: var(--accent-orange) !important;
    background: var(--orange-bg) !important;
}

/* Expander */
div[data-testid="stExpander"] {
    border: 1.5px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    background: #FAFAFA !important;
    box-shadow: none !important;
}

/* Divider */
hr { border-color: var(--border-subtle) !important; margin: 1rem 0 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #9CA3AF; }

/* Required cols hint */
.req-col-box {
    background: #F9FAFB;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    font-size: 0.75rem;
    color: var(--text-secondary) !important;
    margin-top: 1rem;
}

.req-col-title {
    font-weight: 700;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted) !important;
    margin-bottom: 0.4rem;
}

.req-col-pills { display: flex; flex-wrap: wrap; gap: 6px; }

.req-pill {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 4px;
    padding: 2px 10px;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--text-primary) !important;
}

/* Empty state */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem 2rem;
    text-align: center;
    color: var(--text-muted);
}

.empty-icon { font-size: 3rem; margin-bottom: 1rem; opacity: .5; }
.empty-title { font-size: 1rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary) !important; }
.empty-sub { font-size: 0.8rem; font-family: var(--font-mono); color: var(--text-muted) !important; }
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================
# CONFIGURATION CONSTANTS
# =====================================================
DEFAULT_MAX_ITEMS = 450
DEFAULT_MAX_COST  = 900_000
DEFAULT_MAX_ROWS  = 48_000

SUFFIXES = (
    list(string.ascii_uppercase) +
    [a + b for a in string.ascii_uppercase for b in string.ascii_uppercase]
)

# =====================================================
# NAVBAR
# =====================================================
st.markdown(
    f"""
<div class="nav-bar">
  <div class="nav-left">
    {LOGO_HTML}
    <div class="nav-title-block">
      <span class="nav-title">MIM Uploader</span>
      <span class="nav-subtitle">Inventory Split Engine</span>
    </div>
  </div>
  <span class="nav-badge">Internal Tool</span>
</div>
""",
    unsafe_allow_html=True,
)

# =====================================================
# LAYOUT — Left panel | Right panel
# =====================================================
left, right = st.columns([1.1, 2], gap="large")

# ─────────────────────────────────────────────────
# LEFT PANEL
# ─────────────────────────────────────────────────
with left:
    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)

    # ── Configuration card ──────────────────────
    st.markdown(
        '<div class="card card-accent">'
        '<div class="card-header"><div class="card-header-icon"></div>'
        '<span class="card-header-text">Configuration</span></div></div>',
        unsafe_allow_html=True,
    )

    max_items = st.number_input(
        "Max Items per Group",
        min_value=1,
        value=DEFAULT_MAX_ITEMS,
        step=50,
        help="Maximum number of line items allowed in a single Remarks group.",
    )

    max_cost = st.number_input(
        "Max Cost per Group (₹)",
        min_value=1,
        value=DEFAULT_MAX_COST,
        step=10_000,
        format="%d",
        help="Maximum total cost (Qty × Price) allowed in a single Remarks group.",
    )

    max_rows = st.number_input(
        "Max Rows per Output File",
        min_value=1,
        value=DEFAULT_MAX_ROWS,
        step=1_000,
        format="%d",
        help="If the output exceeds this row count it will be split across multiple files.",
    )

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

    # ── Upload card ─────────────────────────────
    st.markdown(
        '<div class="card card-accent">'
        '<div class="card-header"><div class="card-header-icon"></div>'
        '<span class="card-header-text">Input File</span></div></div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Drag and drop or browse",
        type=["csv"],
        help="Upload a CSV with: Store ID · Remarks · Quantity · Liquidation Price",
        label_visibility="collapsed",
    )

    # Required columns hint
    st.markdown(
        """
<div class="req-col-box">
  <div class="req-col-title">Required Columns</div>
  <div class="req-col-pills">
    <span class="req-pill">Store ID</span>
    <span class="req-pill">Remarks</span>
    <span class="req-pill">Quantity</span>
    <span class="req-pill">Liquidation Price</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div style="height:1.25rem"></div>', unsafe_allow_html=True)
    run_btn = st.button("▶  Run Splitter", type="primary", use_container_width=True)


# ─────────────────────────────────────────────────
# RIGHT PANEL
# ─────────────────────────────────────────────────
with right:
    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)

    # ── Empty state ─────────────────────────────
    if not run_btn and uploaded_file is None:
        st.markdown(
            """
<div class="card" style="margin-top:0">
  <div class="empty-state">
    <div class="empty-icon">📊</div>
    <div class="empty-title">Upload a CSV to begin</div>
    <div class="empty-sub">Configure limits → upload file → click Run</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    elif run_btn and uploaded_file is None:
        st.markdown(
            '<div class="notif notif-error">'
            '<span class="notif-icon">✕</span>'
            '<span>No file uploaded. Please select a CSV file before running.</span>'
            "</div>",
            unsafe_allow_html=True,
        )

    elif run_btn and uploaded_file is not None:

        # ── CORE LOGIC (unchanged) ───────────────
        try:
            df = pd.read_csv(uploaded_file)

            # Safety check
            required_columns = {"Store ID", "Remarks", "Quantity", "Liquidation Price"}
            missing_cols = required_columns - set(df.columns)
            if missing_cols:
                st.markdown(
                    f'<div class="notif notif-error">'
                    f'<span class="notif-icon">✕</span>'
                    f'<span>Missing required columns: <strong>{", ".join(missing_cols)}</strong></span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                # Normalise
                df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)
                df["Liquidation Price"] = pd.to_numeric(df["Liquidation Price"], errors="coerce").fillna(0)

                final_rows     = []
                grouping_logs  = []

                for (store_id, remark), group in df.groupby(
                    ["Store ID", "Remarks"], dropna=False
                ):
                    group = group.copy()
                    group["TOTAL_COST"] = group["Quantity"] * group["Liquidation Price"]

                    total_items = len(group)
                    total_cost  = int(group["TOTAL_COST"].sum())

                    needs_split = (
                        total_items > max_items or
                        total_cost  > max_cost
                    )

                    if not needs_split:
                        final_rows.append(group)
                        continue

                    # Greedy splitting
                    suffix_index  = 0
                    current_chunk = []
                    current_items = 0
                    current_cost  = 0
                    created_variants = []

                    for _, row in group.iterrows():
                        row_cost = row["TOTAL_COST"]

                        if (
                            current_items + 1 > max_items or
                            current_cost + row_cost > max_cost
                        ):
                            if suffix_index >= len(SUFFIXES):
                                raise ValueError(
                                    f"Suffix overflow for remark '{remark}'"
                                )
                            new_remark   = f"{remark} {SUFFIXES[suffix_index]}"
                            chunk_df     = pd.DataFrame(current_chunk)
                            chunk_df["Remarks"] = new_remark
                            final_rows.append(chunk_df)
                            created_variants.append(new_remark)

                            suffix_index  += 1
                            current_chunk  = []
                            current_items  = 0
                            current_cost   = 0

                        current_chunk.append(row)
                        current_items += 1
                        current_cost  += row_cost

                    # last chunk
                    if current_chunk:
                        if suffix_index >= len(SUFFIXES):
                            raise ValueError(
                                f"Suffix overflow for remark '{remark}'"
                            )
                        new_remark = f"{remark} {SUFFIXES[suffix_index]}"
                        chunk_df   = pd.DataFrame(current_chunk)
                        chunk_df["Remarks"] = new_remark
                        final_rows.append(chunk_df)
                        created_variants.append(new_remark)

                    grouping_logs.append({
                        "store_id": store_id,
                        "remark":   remark,
                        "items":    total_items,
                        "cost":     total_cost,
                        "reasons":  [
                            r for r in [
                                "ITEM LIMIT EXCEEDED" if total_items > max_items else None,
                                "COST LIMIT EXCEEDED" if total_cost  > max_cost  else None,
                            ] if r
                        ],
                        "variants": created_variants,
                    })

                output_df = pd.concat(final_rows, ignore_index=True)
                output_df.drop(columns=["TOTAL_COST"], errors="ignore", inplace=True)

                total_output_rows = len(output_df)

                # ── STAT CARDS ──────────────────
                st.markdown(
                    f"""
<div class="stat-grid">
  <div class="stat-card">
    <div class="stat-label">Total Output Rows</div>
    <div class="stat-value">{total_output_rows:,}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Groups Split</div>
    <div class="stat-value">{len(grouping_logs)}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Output File(s)</div>
    <div class="stat-value">{math.ceil(total_output_rows / max_rows) if total_output_rows > max_rows else 1}</div>
  </div>
</div>
""",
                    unsafe_allow_html=True,
                )

                # ── SPLITTING DETAILS ────────────
                if grouping_logs:
                    with st.expander(
                        f"🔔  Splitting Details — {len(grouping_logs)} group(s) affected",
                        expanded=False,
                    ):
                        for g in grouping_logs:
                            reasons_html = "".join(
                                f'<span class="tag tag-red">{r}</span>'
                                if "COST" in r
                                else f'<span class="tag tag-orange">{r}</span>'
                                for r in g["reasons"]
                            )
                            variants_html = "".join(
                                f'<span class="variant-pill">{v}</span>'
                                for v in g["variants"]
                            )
                            st.markdown(
                                f"""
<div class="split-row">
  <div class="split-row-header">
    <span class="split-store">Store ID: {g['store_id']}</span>
    <span class="split-meta">{g['items']} items · ₹{g['cost']:,}</span>
  </div>
  <div style="margin-bottom:0.4rem">{reasons_html}</div>
  <div><strong style="font-size:0.72rem;color:var(--text-muted)">VARIANTS:</strong><br/>{variants_html}</div>
</div>
""",
                                unsafe_allow_html=True,
                            )

                # ── OUTPUT FILES SECTION ─────────
                st.markdown(
                    '<div class="card card-accent" style="margin-top:0.75rem">'
                    '<div class="card-header"><div class="card-header-icon"></div>'
                    '<span class="card-header-text">Output Files</span></div></div>',
                    unsafe_allow_html=True,
                )

                if total_output_rows <= max_rows:
                    # Single file
                    csv_bytes = output_df.to_csv(index=False).encode("utf-8")

                    st.markdown(
                        '<div class="notif notif-success">'
                        '<span class="notif-icon">✓</span>'
                        '<span>Processing complete. Single output file ready to download.</span>'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div class="file-row">'
                        f'<span class="file-name">📄 UPLOAD_FILE.csv</span>'
                        f'<span class="file-rows-badge">{total_output_rows:,} rows</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    st.download_button(
                        "⬇  Download UPLOAD_FILE.csv",
                        data=csv_bytes,
                        file_name="UPLOAD_FILE.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

                else:
                    parts = math.ceil(total_output_rows / max_rows)

                    st.markdown(
                        f'<div class="notif notif-warn">'
                        f'<span class="notif-icon">⚠</span>'
                        f'<span>Row limit exceeded ({max_rows:,} rows). Output split into <strong>{parts} part(s)</strong>.</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    file_data = {}
                    for i in range(parts):
                        part_df   = output_df.iloc[i * max_rows : (i + 1) * max_rows]
                        fname     = f"MIM_UPLOADER_PART_{i + 1}.csv"
                        file_data[fname] = part_df.to_csv(index=False).encode("utf-8")

                        st.markdown(
                            f'<div class="file-row">'
                            f'<span class="file-name">📄 {fname}</span>'
                            f'<span class="file-rows-badge">{len(part_df):,} rows</span>'
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

                    # Individual download buttons
                    dl_cols = st.columns(len(file_data))
                    for col, (fname, data) in zip(dl_cols, file_data.items()):
                        with col:
                            st.download_button(
                                f"⬇ {fname}",
                                data=data,
                                file_name=fname,
                                mime="text/csv",
                                use_container_width=True,
                            )

                    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

                    # ZIP download
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                        for fname, data in file_data.items():
                            zf.writestr(fname, data)
                    zip_buffer.seek(0)

                    st.download_button(
                        "⬇  Download All as ZIP",
                        data=zip_buffer.getvalue(),
                        file_name="MIM_UPLOADER_OUTPUT.zip",
                        mime="application/zip",
                        use_container_width=True,
                    )

        except Exception as exc:
            st.markdown(
                f'<div class="notif notif-error">'
                f'<span class="notif-icon">✕</span>'
                f"<span><strong>Error:</strong> {exc}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    elif uploaded_file is not None and not run_btn:
        # File staged but not run yet
        st.markdown(
            '<div class="card" style="margin-top:0">',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="notif notif-info">'
            f'<span class="notif-icon">ℹ</span>'
            f'<span>File <strong>{uploaded_file.name}</strong> loaded. Click <strong>Run Splitter</strong> to process.</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
