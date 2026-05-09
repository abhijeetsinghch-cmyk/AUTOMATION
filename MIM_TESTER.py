import os
import math
import string
import pandas as pd
import streamlit as st
from io import BytesIO
import zipfile

# =====================================================
# CONFIGURATION
# =====================================================
MAX_ITEMS = 450
MAX_COST = 900_000
MAX_ROWS = 45_000
SUFFIXES = list(string.ascii_uppercase)

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="MIM Uploader",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;600;800&display=swap');

:root {
    --bg: #0d0f14;
    --surface: #151820;
    --surface2: #1c2030;
    --border: #252a3a;
    --accent: #4f8ef7;
    --accent2: #f7934f;
    --green: #3ecf8e;
    --red: #f75f5f;
    --yellow: #f7d74f;
    --text: #e8ecf5;
    --muted: #6b7594;
    --font-mono: 'IBM Plex Mono', monospace;
    --font-sans: 'Syne', sans-serif;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-sans) !important;
}

/* ── Header ── */
.mim-header {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 32px 0 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 32px;
}
.mim-logo {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, var(--accent), #7b5cf7);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
}
.mim-title { font-size: 28px; font-weight: 800; letter-spacing: -0.5px; margin: 0; }
.mim-sub   { font-size: 13px; color: var(--muted); margin: 2px 0 0; font-family: var(--font-mono); }

/* ── Cards ── */
.config-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px 24px;
    margin-bottom: 20px;
}
.card-label {
    font-size: 11px;
    font-family: var(--font-mono);
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 14px;
}

/* ── Stat pills ── */
.stat-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }
.stat-pill {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 18px;
    flex: 1; min-width: 130px;
}
.stat-pill .val { font-size: 22px; font-weight: 800; color: var(--accent); font-family: var(--font-mono); }
.stat-pill .lbl { font-size: 11px; color: var(--muted); margin-top: 2px; }

/* ── Log entries ── */
.log-block {
    background: var(--surface2);
    border-left: 3px solid var(--accent2);
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin-bottom: 12px;
    font-family: var(--font-mono);
    font-size: 13px;
}
.log-block .store { color: var(--accent); font-weight: 600; }
.log-block .badge {
    display: inline-block;
    background: rgba(247,147,79,.15);
    color: var(--accent2);
    border: 1px solid rgba(247,147,79,.3);
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 11px;
    margin: 2px 3px 2px 0;
}
.log-block .variant {
    color: var(--green);
    font-size: 12px;
    margin-top: 6px;
}

/* ── Success / warning banners ── */
.banner {
    border-radius: 12px;
    padding: 16px 20px;
    margin: 10px 0;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.banner.success { background: rgba(62,207,142,.1); border: 1px solid rgba(62,207,142,.3); color: var(--green); }
.banner.warning { background: rgba(247,215,79,.1); border: 1px solid rgba(247,215,79,.3); color: var(--yellow); }
.banner.error   { background: rgba(247,95,95,.1);  border: 1px solid rgba(247,95,95,.3);  color: var(--red);  }

/* ── File output rows ── */
.file-row {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-family: var(--font-mono);
    font-size: 13px;
}
.file-row .fname { color: var(--accent); flex: 1; }
.file-row .frows { color: var(--muted); }

/* ── Streamlit overrides ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #7b5cf7) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: var(--font-sans) !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 10px 28px !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .85 !important; }

.stDownloadButton > button {
    background: var(--surface2) !important;
    color: var(--green) !important;
    border: 1px solid rgba(62,207,142,.35) !important;
    border-radius: 10px !important;
    font-family: var(--font-mono) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
.stDownloadButton > button:hover {
    background: rgba(62,207,142,.1) !important;
}

div[data-testid="stFileUploader"] {
    border: 1.5px dashed var(--border) !important;
    border-radius: 12px !important;
    background: var(--surface) !important;
    padding: 10px !important;
}
div[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

.stNumberInput input, .stTextInput input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: var(--font-mono) !important;
}

[data-testid="stMetricValue"] { color: var(--accent) !important; font-family: var(--font-mono) !important; }
[data-testid="stExpander"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; }

/* hide default streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<div class="mim-header">
    <div class="mim-logo">📦</div>
    <div>
        <div class="mim-title">MIM Uploader Splitter</div>
        <div class="mim-sub">inventory · liquidation · auto-split engine</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# LAYOUT: CONFIG SIDEBAR PANEL + MAIN
# =====================================================
col_cfg, col_main = st.columns([1, 2.6], gap="large")

# ── LEFT: Configuration ──────────────────────────────
with col_cfg:
    st.markdown('<div class="card-label">⚙ Limits Configuration</div>', unsafe_allow_html=True)

    max_items = st.number_input("Max Items per Group", min_value=1, value=MAX_ITEMS, step=10,
                                help="Maximum SKUs allowed per remark group before splitting.")
    max_cost  = st.number_input("Max Cost per Group (₹)", min_value=1, value=MAX_COST, step=10000,
                                help="Maximum total liquidation cost per remark group.")
    max_rows  = st.number_input("Max Rows per Output File", min_value=1, value=MAX_ROWS, step=1000,
                                help="Row threshold after which output is split into numbered parts.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card-label">📂 Upload Input CSV</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["csv"], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("▶ Run Splitter", use_container_width=True)

# ── RIGHT: Output ────────────────────────────────────
with col_main:

    if not uploaded_file and not run_btn:
        st.markdown("""
        <div style="text-align:center; padding: 60px 20px; color: #6b7594;">
            <div style="font-size:48px; margin-bottom:16px;">⬆</div>
            <div style="font-size:16px; font-weight:600; color:#e8ecf5;">Upload a CSV to get started</div>
            <div style="font-size:13px; margin-top:8px; font-family:'IBM Plex Mono',monospace;">
                Required columns: Store ID · Remarks · Quantity · Liquidation Price
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif run_btn and not uploaded_file:
        st.markdown('<div class="banner error">⚠ Please upload a CSV file before running.</div>',
                    unsafe_allow_html=True)

    elif run_btn and uploaded_file:
        # =====================================================
        # LOAD INPUT CSV
        # =====================================================
        try:
            output_df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.markdown(f'<div class="banner error">❌ Failed to read CSV: {e}</div>',
                        unsafe_allow_html=True)
            st.stop()

        # =====================================================
        # SAFETY CHECKS
        # =====================================================
        required_columns = {"Store ID", "Remarks", "Quantity", "Liquidation Price"}
        missing_cols = required_columns - set(output_df.columns)
        if missing_cols:
            st.markdown(
                f'<div class="banner error">❌ Missing required columns: <b>{", ".join(missing_cols)}</b></div>',
                unsafe_allow_html=True)
            st.stop()

        # =====================================================
        # NORMALIZATION
        # =====================================================
        output_df["Quantity"] = pd.to_numeric(output_df["Quantity"], errors="coerce").fillna(0)
        output_df["Liquidation Price"] = pd.to_numeric(output_df["Liquidation Price"], errors="coerce").fillna(0)

        # =====================================================
        # GROUPING & STRICT SPLITTING LOGIC
        # =====================================================
        final_rows = []
        grouping_logs = []

        try:
            for (store_id, remark), group in output_df.groupby(["Store ID", "Remarks"], dropna=False):
                group = group.copy()
                group["TOTAL_COST"] = group["Quantity"] * group["Liquidation Price"]
                total_items = len(group)
                total_cost = int(group["TOTAL_COST"].sum())
                needs_split = (total_items > max_items or total_cost > max_cost)

                if not needs_split:
                    final_rows.append(group)
                    continue

                # STRICT GREEDY SPLITTING
                suffix_index = 0
                current_chunk = []
                current_items = 0
                current_cost = 0
                created_variants = []

                for _, row in group.iterrows():
                    row_cost = row["TOTAL_COST"]
                    if (current_items + 1 > max_items or current_cost + row_cost > max_cost):
                        if suffix_index >= len(SUFFIXES):
                            raise ValueError(f"Suffix overflow for remark '{remark}'")
                        new_remark = f"{remark} {SUFFIXES[suffix_index]}"
                        chunk_df = pd.DataFrame(current_chunk)
                        chunk_df["Remarks"] = new_remark
                        final_rows.append(chunk_df)
                        created_variants.append(new_remark)
                        suffix_index += 1
                        current_chunk = []
                        current_items = 0
                        current_cost = 0
                    current_chunk.append(row)
                    current_items += 1
                    current_cost += row_cost

                if current_chunk:
                    if suffix_index >= len(SUFFIXES):
                        raise ValueError(f"Suffix overflow for remark '{remark}'")
                    new_remark = f"{remark} {SUFFIXES[suffix_index]}"
                    chunk_df = pd.DataFrame(current_chunk)
                    chunk_df["Remarks"] = new_remark
                    final_rows.append(chunk_df)
                    created_variants.append(new_remark)

                grouping_logs.append({
                    "store_id": store_id,
                    "remark": remark,
                    "items": total_items,
                    "cost": total_cost,
                    "reasons": [
                        r for r in [
                            "ITEM LIMIT EXCEEDED" if total_items > max_items else None,
                            "COST LIMIT EXCEEDED" if total_cost > max_cost else None,
                        ] if r
                    ],
                    "variants": created_variants,
                })

        except ValueError as e:
            st.markdown(f'<div class="banner error">❌ {e}</div>', unsafe_allow_html=True)
            st.stop()

        # =====================================================
        # FINAL DATAFRAME
        # =====================================================
        output_df = pd.concat(final_rows, ignore_index=True)
        output_df.drop(columns=["TOTAL_COST"], errors="ignore", inplace=True)
        total_rows = len(output_df)

        # =====================================================
        # STATS ROW
        # =====================================================
        groups_split = len(grouping_logs)
        parts_count  = math.ceil(total_rows / max_rows) if total_rows > max_rows else 1

        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-pill">
                <div class="val">{total_rows:,}</div>
                <div class="lbl">Total Output Rows</div>
            </div>
            <div class="stat-pill">
                <div class="val">{groups_split}</div>
                <div class="lbl">Groups Split</div>
            </div>
            <div class="stat-pill">
                <div class="val">{parts_count}</div>
                <div class="lbl">Output File(s)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # =====================================================
        # 🔔 GROUPING LOGS
        # =====================================================
        if grouping_logs:
            with st.expander(f"🔔 Grouping & Splitting Details  ({groups_split} groups affected)", expanded=True):
                for g in grouping_logs:
                    badges = "".join(f'<span class="badge">{r}</span>' for r in g["reasons"])
                    variants_html = "".join(f"<div>↳ {v}</div>" for v in g["variants"])
                    st.markdown(f"""
                    <div class="log-block">
                        <div><span class="store">Store {g['store_id']}</span> &nbsp;·&nbsp; {g['remark']}</div>
                        <div style="margin:6px 0 4px">
                            Items: <b>{g['items']}</b> &nbsp;|&nbsp; Cost: <b>₹{g['cost']:,}</b>
                        </div>
                        <div>{badges}</div>
                        <div class="variant">{variants_html}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="banner success">✓ No groups required splitting — all within limits.</div>',
                        unsafe_allow_html=True)

        # =====================================================
        # OUTPUT FILES
        # =====================================================
        st.markdown('<div class="card-label" style="margin-top:24px">📁 Output Files</div>',
                    unsafe_allow_html=True)

        output_files = {}   # filename → bytes

        if total_rows <= max_rows:
            fname = "UPLOAD_FILE.csv"
            buf = BytesIO()
            output_df.to_csv(buf, index=False)
            output_files[fname] = buf.getvalue()

            st.markdown(f"""
            <div class="file-row">
                <span>📄</span>
                <span class="fname">{fname}</span>
                <span class="frows">{total_rows:,} rows</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="banner success">✅ Single output file ready for download.</div>',
                        unsafe_allow_html=True)
        else:
            parts = math.ceil(total_rows / max_rows)
            st.markdown(
                f'<div class="banner warning">⚠ Row limit exceeded ({max_rows:,}). Split into {parts} part(s).</div>',
                unsafe_allow_html=True)

            for i in range(parts):
                part_df = output_df.iloc[i * max_rows:(i + 1) * max_rows]
                fname = f"MIM_UPLOADER_PART_{i + 1}.csv"
                buf = BytesIO()
                part_df.to_csv(buf, index=False)
                output_files[fname] = buf.getvalue()

                st.markdown(f"""
                <div class="file-row">
                    <span>📄</span>
                    <span class="fname">{fname}</span>
                    <span class="frows">{len(part_df):,} rows</span>
                </div>
                """, unsafe_allow_html=True)

        # =====================================================
        # DOWNLOAD BUTTONS
        # =====================================================
        st.markdown("<br>", unsafe_allow_html=True)

        if len(output_files) == 1:
            fname, data = next(iter(output_files.items()))
            st.download_button(
                label=f"⬇ Download {fname}",
                data=data,
                file_name=fname,
                mime="text/csv",
                use_container_width=True,
            )
        else:
            # ZIP all parts
            zip_buf = BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname, data in output_files.items():
                    zf.writestr(fname, data)
            zip_buf.seek(0)

            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                st.download_button(
                    label="⬇ Download All as ZIP",
                    data=zip_buf.getvalue(),
                    file_name="MIM_UPLOADER_PARTS.zip",
                    mime="application/zip",
                    use_container_width=True,
                )
            with dl_col2:
                # individual downloads in expander
                with st.expander("⬇ Download Individual Files"):
                    for fname, data in output_files.items():
                        st.download_button(
                            label=f"⬇ {fname}",
                            data=data,
                            file_name=fname,
                            mime="text/csv",
                            use_container_width=True,
                            key=fname,
                        )