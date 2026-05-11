import os
import math
import string
import io
import base64
import zipfile
import pandas as pd
import streamlit as st

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="MIM Uploader — Instamart",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================
# CONFIGURATION DEFAULTS
# =====================================================
DEFAULT_MAX_ITEMS = 450
DEFAULT_MAX_COST  = 900_000
DEFAULT_MAX_ROWS  = 48_000

SUFFIXES = (
    list(string.ascii_uppercase) +
    [a + b for a in string.ascii_uppercase for b in string.ascii_uppercase]
)

# =====================================================
# LOGO
# =====================================================
LOGO_PATH = "/mnt/user-data/uploads/Icon.png"

def get_logo_b64():
    try:
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

logo_b64 = get_logo_b64()

# =====================================================
# CSS
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: linear-gradient(135deg, #0a0a0f 0%, #111118 40%, #0d0d14 70%, #090910 100%) !important;
    color: #E8EAF0 !important;
    font-family: 'Inter', sans-serif !important;
    min-height: 100vh;
}

[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section[data-testid="stMain"] > div {
    background: transparent !important;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Navbar ── */
.mim-nav {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 32px;
    background: rgba(255,255,255,0.03);
    border-bottom: 1px solid rgba(255,255,255,0.07);
    backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 100;
}
.mim-nav-logo {
    width: 42px; height: 42px;
    border-radius: 11px;
    object-fit: cover;
    box-shadow: 0 2px 12px rgba(0,0,0,0.5);
}
.mim-nav-logo-fallback {
    width: 42px; height: 42px;
    border-radius: 11px;
    background: linear-gradient(135deg, #1D4ED8, #3B82F6);
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 1rem; color: #fff;
}
.mim-nav-text { display: flex; flex-direction: column; gap: 1px; }
.mim-nav-title {
    font-size: 0.95rem; font-weight: 700;
    color: #F0F2F8; letter-spacing: -0.2px;
}
.mim-nav-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; color: #6B7280; letter-spacing: 0.5px;
}
.mim-nav-badge {
    margin-left: auto;
    background: rgba(239,68,68,0.15);
    border: 1px solid rgba(239,68,68,0.3);
    color: #EF4444;
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 1.5px; padding: 5px 14px;
    border-radius: 6px; text-transform: uppercase;
}

/* ── Section label ── */
.mim-section-label {
    display: flex; align-items: center; gap: 8px;
    font-size: 0.67rem; font-weight: 600;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: #4B5563; margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.mim-section-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #F97316; flex-shrink: 0;
}

/* ── Metric cards ── */
.mim-metrics {
    display: flex; gap: 14px; flex-wrap: wrap;
    margin-bottom: 18px;
}
.mim-metric-card {
    flex: 1; min-width: 130px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 18px 20px;
    transition: border-color 0.2s;
}
.mim-metric-card:hover { border-color: rgba(255,255,255,0.15); }
.mim-metric-val {
    font-size: 1.8rem; font-weight: 700;
    color: #F97316; line-height: 1.1; letter-spacing: -1px;
}
.mim-metric-val.blue  { color: #60A5FA; }
.mim-metric-val.green { color: #34D399; }
.mim-metric-lbl { font-size: 0.72rem; color: #4B5563; margin-top: 5px; font-weight: 500; }

/* ── Alert boxes ── */
.mim-alert {
    border-radius: 10px; padding: 13px 16px;
    font-size: 0.82rem; line-height: 1.55;
    display: flex; align-items: flex-start;
    gap: 12px; border: 1px solid; margin-bottom: 10px;
}
.mim-alert-icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }
.mim-alert-success { background: rgba(16,185,129,0.08);  border-color: rgba(16,185,129,0.2);  color: #6EE7B7; }
.mim-alert-error   { background: rgba(239,68,68,0.08);   border-color: rgba(239,68,68,0.2);   color: #FCA5A5; }
.mim-alert-warning { background: rgba(245,158,11,0.08);  border-color: rgba(245,158,11,0.2);  color: #FCD34D; }
.mim-alert-info    { background: rgba(96,165,250,0.08);  border-color: rgba(96,165,250,0.2);  color: #93C5FD; }

/* ── File row ── */
.mim-file-row {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 14px 18px;
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 8px;
    transition: border-color 0.2s, background 0.2s;
}
.mim-file-row:hover { border-color: rgba(255,255,255,0.14); background: rgba(255,255,255,0.035); }
.mim-file-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem; color: #60A5FA; font-weight: 500;
}
.mim-file-rows-badge {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; color: #4B5563;
}

/* ── Required columns card ── */
.mim-req-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px; padding: 14px 16px;
    margin-top: 10px;
}
.mim-req-title { font-size: 0.72rem; font-weight: 600; color: #6B7280; margin-bottom: 8px; }
.mim-req-cols { display: flex; flex-wrap: wrap; gap: 6px; }
.mim-req-col {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px; padding: 4px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; color: #9CA3AF;
}

/* ── Empty state ── */
.mim-empty {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 14px; text-align: center;
    padding: 80px 20px;
}
.mim-empty-icon { font-size: 3.2rem; opacity: 0.2; filter: grayscale(1); }
.mim-empty-title { font-size: 1rem; font-weight: 600; color: #374151; }
.mim-empty-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; color: #2D3748; letter-spacing: 0.3px;
}

/* ── Run button ── */
.mim-run-btn-wrap .stButton > button {
    background: linear-gradient(135deg, #EA580C, #F97316) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; padding: 0.75rem 1.5rem !important;
    font-size: 0.88rem !important; font-weight: 700 !important;
    width: 100% !important;
    box-shadow: 0 4px 20px rgba(249,115,22,0.25) !important;
    transition: all 0.2s !important;
}
.mim-run-btn-wrap .stButton > button:hover {
    background: linear-gradient(135deg, #C2410C, #EA580C) !important;
    box-shadow: 0 6px 24px rgba(249,115,22,0.35) !important;
}

/* ── Download buttons ── */
.mim-dl-zip .stDownloadButton > button {
    background: rgba(16,185,129,0.1) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    color: #34D399 !important; border-radius: 10px !important;
    font-size: 0.83rem !important; font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important; width: 100% !important;
    transition: all 0.18s !important;
}
.mim-dl-zip .stDownloadButton > button:hover {
    background: rgba(16,185,129,0.18) !important;
    border-color: rgba(16,185,129,0.5) !important;
}
.mim-dl-ind .stDownloadButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #9CA3AF !important; border-radius: 10px !important;
    font-size: 0.83rem !important; font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important; width: 100% !important;
}
.mim-dl-ind .stDownloadButton > button:hover {
    background: rgba(255,255,255,0.08) !important; color: #E5E7EB !important;
}

/* ── Number inputs ── */
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important; color: #E8EAF0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important; font-weight: 500 !important;
}
[data-testid="stNumberInput"] button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #9CA3AF !important; border-radius: 6px !important;
}
[data-testid="stNumberInput"] button:hover {
    background: rgba(255,255,255,0.1) !important; color: #E8EAF0 !important;
}
[data-testid="stNumberInput"] label,
[data-testid="stFileUploader"] label,
.stSelectSlider label { color: #9CA3AF !important; font-size: 0.8rem !important; }

/* ── Text input ── */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important; color: #E8EAF0 !important;
    font-size: 0.83rem !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1.5px dashed rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"]:hover { border-color: rgba(249,115,22,0.35) !important; }
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzoneInstructions"] span { color: #6B7280 !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important; margin-bottom: 10px !important;
}
[data-testid="stExpander"] summary { color: #9CA3AF !important; font-size: 0.82rem !important; font-weight: 500 !important; }
[data-testid="stExpander"] > div > div { background: transparent !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important; overflow: hidden;
}

/* ── Column separator ── */
[data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 0 !important; align-items: stretch !important; }

/* ── Left panel border ── */
div[data-testid="stHorizontalBlock"] > div:first-child {
    border-right: 1px solid rgba(255,255,255,0.07) !important;
    padding-right: 28px !important;
    padding-top: 28px !important;
    padding-bottom: 28px !important;
    padding-left: 28px !important;
    background: rgba(255,255,255,0.015) !important;
}
div[data-testid="stHorizontalBlock"] > div:last-child {
    padding: 32px 36px !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 1rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.18); }
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE
# =====================================================
for key, val in {
    "result_df": None,
    "grouping_logs": [],
    "output_files": [],
    "processing_done": False,
    "input_stats": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =====================================================
# PROCESSING FUNCTIONS (logic preserved exactly)
# =====================================================
def run_processing(input_df, max_items, max_cost):
    output_df = input_df.copy()
    required_columns = {"Store ID", "Remarks", "Quantity", "Liquidation Price"}
    missing_cols = required_columns - set(output_df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    output_df["Quantity"] = pd.to_numeric(output_df["Quantity"], errors="coerce").fillna(0)
    output_df["Liquidation Price"] = pd.to_numeric(output_df["Liquidation Price"], errors="coerce").fillna(0)

    final_rows = []
    grouping_logs = []

    for (store_id, remark), group in output_df.groupby(["Store ID", "Remarks"], dropna=False):
        group = group.copy()
        group["TOTAL_COST"] = group["Quantity"] * group["Liquidation Price"]
        total_items = len(group)
        total_cost  = int(group["TOTAL_COST"].sum())
        needs_split = (total_items > max_items or total_cost > max_cost)

        if not needs_split:
            final_rows.append(group)
            continue

        suffix_index = 0
        current_chunk, current_items, current_cost = [], 0, 0
        created_variants = []

        for _, row in group.iterrows():
            row_cost = row["TOTAL_COST"]
            if current_items + 1 > max_items or current_cost + row_cost > max_cost:
                if suffix_index >= len(SUFFIXES):
                    raise ValueError(f"Suffix overflow for remark '{remark}'")
                new_remark = f"{remark} {SUFFIXES[suffix_index]}"
                chunk_df = pd.DataFrame(current_chunk)
                chunk_df["Remarks"] = new_remark
                final_rows.append(chunk_df)
                created_variants.append(new_remark)
                suffix_index += 1
                current_chunk, current_items, current_cost = [], 0, 0
            current_chunk.append(row)
            current_items += 1
            current_cost  += row_cost

        if current_chunk:
            if suffix_index >= len(SUFFIXES):
                raise ValueError(f"Suffix overflow for remark '{remark}'")
            new_remark = f"{remark} {SUFFIXES[suffix_index]}"
            chunk_df = pd.DataFrame(current_chunk)
            chunk_df["Remarks"] = new_remark
            final_rows.append(chunk_df)
            created_variants.append(new_remark)

        grouping_logs.append({
            "store_id": store_id, "remark": remark,
            "items": total_items, "cost": total_cost,
            "reasons": [r for r in [
                "ITEM LIMIT EXCEEDED" if total_items > max_items else None,
                "COST LIMIT EXCEEDED" if total_cost  > max_cost  else None,
            ] if r],
            "variants": created_variants,
        })

    output_df = pd.concat(final_rows, ignore_index=True)
    output_df.drop(columns=["TOTAL_COST"], errors="ignore", inplace=True)
    return output_df, grouping_logs

def split_into_files(df, max_rows):
    total = len(df)
    if total <= max_rows:
        buf = io.BytesIO(); df.to_csv(buf, index=False)
        return [("UPLOAD_FILE.csv", buf.getvalue(), total)]
    parts = math.ceil(total / max_rows)
    files = []
    for i in range(parts):
        part = df.iloc[i * max_rows:(i + 1) * max_rows]
        buf  = io.BytesIO(); part.to_csv(buf, index=False)
        files.append((f"MIM_UPLOADER_PART_{i+1}.csv", buf.getvalue(), len(part)))
    return files

def build_zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for fname, fdata, _ in files:
            z.writestr(fname, fdata)
    return buf.getvalue()

# =====================================================
# NAVBAR
# =====================================================
if logo_b64:
    logo_html = f'<img class="mim-nav-logo" src="data:image/png;base64,{logo_b64}" alt="logo"/>'
else:
    logo_html = '<div class="mim-nav-logo-fallback">IM</div>'

st.markdown(f"""
<div class="mim-nav">
    {logo_html}
    <div class="mim-nav-text">
        <span class="mim-nav-title">MIM Uploader</span>
        <span class="mim-nav-sub">Inventory Split Engine</span>
    </div>
    <div class="mim-nav-badge">Internal Tool</div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# BODY — TWO-COLUMN LAYOUT
# =====================================================
col_left, col_right = st.columns([1, 2.2], gap="small")

# ─────────────────────────────────────────────────────
# LEFT PANEL — Configuration + Upload
# ─────────────────────────────────────────────────────
with col_left:

    st.markdown("""
    <div class="mim-section-label">
        <span class="mim-section-dot"></span> Configuration
    </div>
    """, unsafe_allow_html=True)

    max_items = st.number_input(
        "Max Items per Group",
        min_value=1, max_value=10_000,
        value=DEFAULT_MAX_ITEMS, step=10,
        help="Maximum number of SKU rows per Store ID + Remark group",
    )
    max_cost = st.number_input(
        "Max Cost per Group (₹)",
        min_value=1, max_value=100_000_000,
        value=DEFAULT_MAX_COST, step=10_000,
        help="Maximum total cost (Qty × Price) per group",
    )
    max_rows = st.number_input(
        "Max Rows per Output File",
        min_value=1000, max_value=500_000,
        value=DEFAULT_MAX_ROWS, step=1000,
        help="Output CSV is split if row count exceeds this",
    )

    st.markdown("""
    <div class="mim-section-label" style="margin-top:10px;">
        <span class="mim-section-dot"></span> Input File
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="mim-run-btn-wrap">', unsafe_allow_html=True)
    run_btn = st.button("▶  Run Splitter", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="mim-req-card">
        <div class="mim-req-title">Required columns</div>
        <div class="mim-req-cols">
            <span class="mim-req-col">Store ID</span>
            <span class="mim-req-col">Remarks</span>
            <span class="mim-req-col">Quantity</span>
            <span class="mim-req-col">Liquidation Price</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# RIGHT PANEL — Results / Empty
# ─────────────────────────────────────────────────────
with col_right:

    # ── Process when file uploaded + button clicked ──
    if uploaded_file:
        try:
            raw_df = pd.read_csv(uploaded_file)
            required_cols = {"Store ID", "Remarks", "Quantity", "Liquidation Price"}
            missing = required_cols - set(raw_df.columns)

            if missing:
                st.markdown(f"""
                <div class="mim-alert mim-alert-error">
                    <span class="mim-alert-icon">❌</span>
                    <div><strong>Missing columns:</strong> {', '.join(missing)}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Compute input stats
                tmp = raw_df.copy()
                tmp["Quantity"] = pd.to_numeric(tmp["Quantity"], errors="coerce").fillna(0)
                tmp["Liquidation Price"] = pd.to_numeric(tmp["Liquidation Price"], errors="coerce").fillna(0)
                st.session_state.input_stats = {
                    "rows": len(raw_df),
                    "total_cost": int((tmp["Quantity"] * tmp["Liquidation Price"]).sum()),
                    "stores": raw_df["Store ID"].nunique(),
                    "remarks": raw_df["Remarks"].nunique(),
                    "filename": uploaded_file.name,
                    "size_mb": round(uploaded_file.size / 1_048_576, 2),
                }

                if run_btn:
                    with st.spinner("Processing… please wait"):
                        try:
                            result_df, grouping_logs = run_processing(
                                raw_df, int(max_items), int(max_cost)
                            )
                            output_files = split_into_files(result_df, int(max_rows))
                            st.session_state.result_df       = result_df
                            st.session_state.grouping_logs   = grouping_logs
                            st.session_state.output_files    = output_files
                            st.session_state.processing_done = True
                        except Exception as e:
                            st.markdown(f"""
                            <div class="mim-alert mim-alert-error">
                                <span class="mim-alert-icon">❌</span>
                                <div><strong>Error:</strong> {e}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.session_state.processing_done = False

        except Exception as e:
            st.markdown(f"""
            <div class="mim-alert mim-alert-error">
                <span class="mim-alert-icon">❌</span>
                <div><strong>Failed to read file:</strong> {e}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── RESULTS ──
    if st.session_state.processing_done and st.session_state.result_df is not None:
        result_df     = st.session_state.result_df
        grouping_logs = st.session_state.grouping_logs
        output_files  = st.session_state.output_files

        # Metric row
        st.markdown(f"""
        <div class="mim-metrics">
            <div class="mim-metric-card">
                <div class="mim-metric-val">{len(result_df):,}</div>
                <div class="mim-metric-lbl">Total Output Rows</div>
            </div>
            <div class="mim-metric-card">
                <div class="mim-metric-val blue">{len(grouping_logs)}</div>
                <div class="mim-metric-lbl">Groups Split</div>
            </div>
            <div class="mim-metric-card">
                <div class="mim-metric-val green">{len(output_files)}</div>
                <div class="mim-metric-lbl">Output File(s)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Splitting details expander
        if grouping_logs:
            with st.expander(f"🔔  Splitting Details — {len(grouping_logs)} group(s) affected", expanded=False):
                for g in grouping_logs:
                    variants_html = "".join([
                        f'<span style="background:rgba(96,165,250,0.1);border:1px solid rgba(96,165,250,0.2);'
                        f'border-radius:5px;padding:3px 9px;font-family:monospace;'
                        f'font-size:0.68rem;color:#60A5FA;">{v}</span>'
                        for v in g["variants"]
                    ])
                    st.markdown(f"""
                    <div style="border-left:2px solid rgba(249,115,22,0.4);padding:10px 14px;
                                margin-bottom:12px;background:rgba(249,115,22,0.04);
                                border-radius:0 8px 8px 0;">
                        <div style="font-size:0.78rem;font-weight:600;color:#D1D5DB;margin-bottom:5px;">
                            📌 Store <span style="color:#F97316;">{g['store_id']}</span>
                            &nbsp;·&nbsp; {g['remark']}
                        </div>
                        <div style="font-size:0.72rem;color:#6B7280;margin-bottom:6px;">
                            Items: <span style="color:#9CA3AF">{g['items']:,}</span>
                            &nbsp;·&nbsp; Cost: <span style="color:#9CA3AF">₹{g['cost']:,}</span>
                            &nbsp;·&nbsp; Reason:
                            <span style="color:#FCD34D">{' · '.join(g['reasons'])}</span>
                        </div>
                        <div style="display:flex;flex-wrap:wrap;gap:6px;">{variants_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # Output files section
        st.markdown("""
        <div class="mim-section-label">
            <span class="mim-section-dot"></span> Output Files
        </div>
        """, unsafe_allow_html=True)

        if len(output_files) > 1:
            st.markdown(f"""
            <div class="mim-alert mim-alert-warning">
                <span class="mim-alert-icon">⚠️</span>
                <div>Row limit exceeded ({int(max_rows):,} rows).
                Output split into <strong>{len(output_files)} part(s)</strong>.</div>
            </div>
            """, unsafe_allow_html=True)

        for fname, fdata, row_count in output_files:
            st.markdown(f"""
            <div class="mim-file-row">
                <span style="font-size:1.1rem;">📄</span>
                <span class="mim-file-name">{fname}</span>
                <span class="mim-file-rows-badge">{row_count:,} rows</span>
            </div>
            """, unsafe_allow_html=True)

        # Download buttons
        zip_data = build_zip(output_files)
        dl_c1, dl_c2 = st.columns(2)

        with dl_c1:
            st.markdown('<div class="mim-dl-zip">', unsafe_allow_html=True)
            st.download_button(
                label="⬇  Download All as ZIP",
                data=zip_data,
                file_name="MIM_OUTPUT.zip",
                mime="application/zip",
                use_container_width=True,
                key="dl_zip",
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with dl_c2:
            if len(output_files) == 1:
                fname, fdata, _ = output_files[0]
                st.markdown('<div class="mim-dl-ind">', unsafe_allow_html=True)
                st.download_button(
                    label=f"⬇  Download {fname}",
                    data=fdata, file_name=fname, mime="text/csv",
                    use_container_width=True, key="dl_single",
                )
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                with st.expander("⬇  Download Individual Files", expanded=False):
                    for i, (fname, fdata, row_count) in enumerate(output_files):
                        st.markdown('<div class="mim-dl-ind">', unsafe_allow_html=True)
                        st.download_button(
                            label=f"Part {i+1} — {fname}  ({row_count:,} rows)",
                            data=fdata, file_name=fname, mime="text/csv",
                            use_container_width=True, key=f"dl_{i}",
                        )
                        st.markdown("</div>", unsafe_allow_html=True)

        # Preview
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        with st.expander("🔍  Preview Output Data", expanded=False):
            search = st.text_input(
                "Filter", placeholder="Search Remarks or Store ID…",
                label_visibility="collapsed", key="search"
            )
            preview = result_df.copy()
            if search:
                mask = (
                    preview["Remarks"].astype(str).str.contains(search, case=False, na=False) |
                    preview["Store ID"].astype(str).str.contains(search, case=False, na=False)
                )
                preview = preview[mask]
                st.markdown(f"""
                <div class="mim-alert mim-alert-info">
                    <span class="mim-alert-icon">🔍</span>
                    <div><strong>{len(preview):,}</strong> rows for "<strong>{search}</strong>"</div>
                </div>
                """, unsafe_allow_html=True)
            n_rows = st.select_slider(
                "Rows", options=[50, 100, 250, 500, 1000], value=100,
                label_visibility="collapsed", key="nrows"
            )
            st.dataframe(preview.head(n_rows), use_container_width=True, height=340)

        # Success
        st.markdown(f"""
        <div class="mim-alert mim-alert-success" style="margin-top:8px;">
            <span class="mim-alert-icon">✅</span>
            <div>Processing complete —
                <strong>{len(result_df):,}</strong> rows across
                <strong>{len(output_files)}</strong> file(s).
                {len(grouping_logs)} group(s) split.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── FILE LOADED, NOT YET RUN ──
    elif uploaded_file and not st.session_state.processing_done:
        istats = st.session_state.input_stats
        if istats:
            st.markdown(f"""
            <div class="mim-alert mim-alert-info">
                <span class="mim-alert-icon">📂</span>
                <div>
                    <strong>{istats.get('filename','')}</strong>
                    &nbsp;·&nbsp; {istats.get('size_mb',0)} MB
                    &nbsp;·&nbsp; {istats.get('rows',0):,} rows
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="mim-metrics">
                <div class="mim-metric-card">
                    <div class="mim-metric-val">{istats.get('rows',0):,}</div>
                    <div class="mim-metric-lbl">Input Rows</div>
                </div>
                <div class="mim-metric-card">
                    <div class="mim-metric-val blue">{istats.get('stores',0)}</div>
                    <div class="mim-metric-lbl">Unique Stores</div>
                </div>
                <div class="mim-metric-card">
                    <div class="mim-metric-val green">{istats.get('remarks',0)}</div>
                    <div class="mim-metric-lbl">Unique Remarks</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("""
        <div class="mim-alert mim-alert-info">
            <span class="mim-alert-icon">ℹ️</span>
            <div>File loaded — click <strong>▶ Run Splitter</strong> to process.</div>
        </div>
        """, unsafe_allow_html=True)

    # ── EMPTY STATE ──
    else:
        st.markdown("""
        <div class="mim-empty">
            <div class="mim-empty-icon">📊</div>
            <div class="mim-empty-title">Upload a CSV to begin</div>
            <div class="mim-empty-sub">Configure limits → upload file → click Run</div>
        </div>
        """, unsafe_allow_html=True)
