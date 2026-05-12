import os
import math
import string
import pandas as pd
import streamlit as st
from io import BytesIO
import zipfile
import base64

# =====================================================
# CONFIGURATION
# =====================================================
MAX_ITEMS = 450
MAX_COST  = 900_000
MAX_ROWS  = 45_000
SUFFIXES  = list(string.ascii_uppercase)

LOGO_B64 = "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"

# =====================================================
# THEME STATE
# =====================================================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

IS_DARK = st.session_state.theme == "dark"

# =====================================================
# THEME CSS VARIABLES
# =====================================================
LIGHT_VARS = """
    --white:   #ffffff;
    --bg:      #f1f3f6;
    --surface: rgba(255,255,255,0.92);
    --border:  #e2e5ea;
    --text:    #101828;
    --muted:   #667085;
    --input-bg:#ffffff;
    --log-bg:  #ffffff;
    --stat-bg: #ffffff;
    --expander-bg: #ffffff;
    --file-row-bg: #ffffff;
    --hint-bg: #ffffff;
    --shadow:  0 1px 3px rgba(0,0,0,.08), 0 4px 16px rgba(0,0,0,.04);
    --shadow2: 0 2px 8px rgba(0,0,0,.10), 0 8px 24px rgba(0,0,0,.06);
    --navbar-bg: #ffffff;
    --page-bg: linear-gradient(145deg, #e8eaed 0%, #f4f5f7 40%, #ecedf0 100%);
"""

DARK_VARS = """
    --white:   #1e2130;
    --bg:      #13151f;
    --surface: rgba(26,29,42,0.97);
    --border:  #2d3148;
    --text:    #e8eaf0;
    --muted:   #8b91a8;
    --input-bg:#252838;
    --log-bg:  #252838;
    --stat-bg: #1e2130;
    --expander-bg: #1e2130;
    --file-row-bg: #1e2130;
    --hint-bg: #252838;
    --shadow:  0 1px 3px rgba(0,0,0,.3), 0 4px 16px rgba(0,0,0,.2);
    --shadow2: 0 2px 8px rgba(0,0,0,.35), 0 8px 24px rgba(0,0,0,.25);
    --navbar-bg: #1a1d2e;
    --page-bg: linear-gradient(145deg, #0f111a 0%, #13151f 40%, #111320 100%);
"""

THEME_VARS = DARK_VARS if IS_DARK else LIGHT_VARS

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Instamart — MIM Uploader",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================
# PREMIUM CSS (theme-aware)
# =====================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

:root {{
    {THEME_VARS}
    --orange:  #f05a2a;
    --orange2: #ff7a45;
    --green:   #12b76a;
    --red:     #d92d20;
    --warn:    #dc6803;
    --blue:    #1570ef;
    --mono:    'DM Mono', monospace;
    --radius:  14px;
    --radius-sm: 8px;
}}

html, body {{
    background: var(--page-bg) !important;
    min-height: 100vh;
}}

[class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    color: var(--text) !important;
}}

/* ── Kill Streamlit chrome ── */
#MainMenu, footer, header,
div[data-testid="stToolbar"],
div[data-testid="stDecoration"] {{ visibility: hidden !important; height: 0 !important; }}
section[data-testid="stSidebar"] {{ display: none; }}

.block-container {{
    padding-top: 0.6rem !important;
    padding-bottom: 2rem !important;
    max-width: 1280px !important;
}}

/* ── NAVBAR ── */
.im-navbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--navbar-bg);
    border-bottom: 1px solid var(--border);
    padding: 0 28px;
    height: 70px;
    margin: -0.6rem -1rem 0;
    width: calc(100% + 2rem);
    box-shadow: 0 1px 0 var(--border), 0 2px 12px rgba(0,0,0,.12);
    position: sticky;
    top: 0;
    z-index: 100;
}}
.im-navbar-left  {{ display: flex; align-items: center; gap: 12px; }}
.im-navbar-logo  {{ height: 52px; width: auto; border-radius: 10px; }}
.im-navbar-title {{
    font-size: 14px;
    font-weight: 600;
    color: var(--text) !important;
    letter-spacing: -.01em;
    border-left: 1.5px solid var(--border);
    padding-left: 14px;
    margin-left: 2px;
}}
.im-navbar-sub {{
    font-size: 12px;
    color: var(--muted) !important;
    font-family: var(--mono);
    display: block;
    line-height: 1;
    margin-top: 2px;
}}
.im-navbar-badge {{
    font-size: 11px;
    font-weight: 600;
    background: linear-gradient(135deg, var(--orange), var(--orange2));
    color: #fff;
    padding: 6px 16px;
    border-radius: 50px;
    letter-spacing: .04em;
    box-shadow: 0 2px 8px rgba(240,90,42,.30);
}}

/* ── CARDS ── */
.im-card {{
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 20px 22px;
    margin-bottom: 16px;
}}
.im-card-orange {{
    border-color: rgba(240,90,42,.25);
    box-shadow: var(--shadow), inset 0 0 0 1px rgba(240,90,42,.06);
}}

.im-section-label {{
    font-size: 10.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    color: var(--muted) !important;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 7px;
}}
.im-section-label::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: var(--border);
    display: block;
}}

/* ── STATS ── */
.im-stats {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 18px; }}
.im-stat {{
    flex: 1;
    min-width: 120px;
    background: var(--stat-bg);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 14px 16px;
    box-shadow: var(--shadow);
}}
.im-stat-val {{
    font-size: 24px;
    font-weight: 700;
    color: var(--orange) !important;
    font-family: var(--mono);
    line-height: 1;
}}
.im-stat-lbl {{
    font-size: 11.5px;
    color: var(--muted) !important;
    margin-top: 5px;
    font-weight: 500;
}}

/* ── BANNERS ── */
.im-banner {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 10px 0;
    font-size: 13.5px;
    font-weight: 500;
    line-height: 1.5;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
}}
.im-banner-icon {{ font-size: 16px; flex-shrink: 0; margin-top: 1px; }}
.im-banner.success {{ background: {"#0d2b1a" if IS_DARK else "#f0fdf4"}; border: 1px solid {"#1a4731" if IS_DARK else "#bbf7d0"}; color: {"#6ee7b7" if IS_DARK else "#166534"} !important; }}
.im-banner.warning {{ background: {"#2b1f07" if IS_DARK else "#fffbeb"}; border: 1px solid {"#4d3510" if IS_DARK else "#fde68a"}; color: {"#fbbf24" if IS_DARK else "#92400e"} !important; }}
.im-banner.error   {{ background: {"#2a0f0f" if IS_DARK else "#fef2f2"}; border: 1px solid {"#4d1515" if IS_DARK else "#fecaca"}; color: {"#fca5a5" if IS_DARK else "#991b1b"} !important; }}
.im-banner.info    {{ background: {"#0d1b38" if IS_DARK else "#eff6ff"}; border: 1px solid {"#1e3a70" if IS_DARK else "#bfdbfe"}; color: {"#93c5fd" if IS_DARK else "#1e40af"} !important; }}

/* ── LOG BLOCKS ── */
.im-log {{
    background: var(--log-bg);
    border: 1px solid var(--border);
    border-left: 3.5px solid var(--orange);
    border-radius: 0 10px 10px 0;
    padding: 14px 16px;
    margin-bottom: 10px;
    font-family: var(--mono);
    font-size: 12.5px;
    line-height: 1.6;
    box-shadow: var(--shadow);
}}
.im-log-store {{ font-weight: 600; color: var(--blue) !important; font-size: 13px; }}
.im-log-meta  {{ color: var(--muted) !important; margin: 3px 0; }}
.im-log-badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: {"rgba(194,65,12,.2)" if IS_DARK else "#fff7ed"};
    color: {"#fb923c" if IS_DARK else "#c2410c"} !important;
    border: 1px solid {"rgba(194,65,12,.4)" if IS_DARK else "#fed7aa"};
    border-radius: 5px;
    padding: 2px 8px;
    font-size: 10.5px;
    font-weight: 600;
    margin: 2px 3px 2px 0;
    text-transform: uppercase;
    letter-spacing: .04em;
}}
.im-log-variant {{ color: var(--green) !important; font-size: 12px; margin-top: 6px; }}
.im-log-variant div::before {{ content: "↳ "; opacity: .5; }}

/* ── FILE ROWS ── */
.im-file-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--file-row-bg);
    border: 1.5px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-family: var(--mono);
    font-size: 12.5px;
    box-shadow: var(--shadow);
    transition: border-color .15s;
}}
.im-file-row:hover {{ border-color: rgba(240,90,42,.4); }}
.im-file-icon {{ font-size: 18px; }}
.im-file-name {{ flex: 1; color: var(--blue) !important; font-weight: 500; }}
.im-file-rows {{ color: var(--muted) !important; }}

/* ── INPUTS ── */
.stNumberInput label,
.stFileUploader label {{
    font-size: 12.5px !important;
    font-weight: 600 !important;
    color: {"#c9cde0" if IS_DARK else "#344054"} !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}}
.stNumberInput input {{
    background: var(--input-bg) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--mono) !important;
    font-size: 14px !important;
    padding: 8px 12px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,.1) !important;
}}
.stNumberInput input:focus {{
    border-color: var(--orange) !important;
    box-shadow: 0 0 0 3px rgba(240,90,42,.18) !important;
}}

/* ── Run button ── */
div[data-testid="stButton"] > button {{
    background: linear-gradient(135deg, var(--orange) 0%, var(--orange2) 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14.5px !important;
    padding: 10px 24px !important;
    box-shadow: 0 2px 8px rgba(240,90,42,.35) !important;
    transition: all .15s ease !important;
    width: 100% !important;
    letter-spacing: .01em !important;
}}
div[data-testid="stButton"] > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(240,90,42,.4) !important;
}}

/* ── Theme toggle button ── */
.theme-toggle-btn > div[data-testid="stButton"] > button {{
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 50px !important;
    font-weight: 600 !important;
    font-size: 12.5px !important;
    padding: 6px 14px !important;
    box-shadow: var(--shadow) !important;
    width: auto !important;
    letter-spacing: .01em !important;
}}
.theme-toggle-btn > div[data-testid="stButton"] > button:hover {{
    border-color: var(--orange) !important;
    transform: none !important;
}}

/* ── Download buttons ── */
div[data-testid="stDownloadButton"] > button {{
    background: {"#0d2b1a" if IS_DARK else "var(--white)"} !important;
    color: var(--green) !important;
    border: 1.5px solid {"#1a4731" if IS_DARK else "#a7f3d0"} !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    box-shadow: var(--shadow) !important;
    transition: all .15s ease !important;
}}
div[data-testid="stDownloadButton"] > button:hover {{
    background: {"#0f3520" if IS_DARK else "#f0fdf4"} !important;
    border-color: var(--green) !important;
    box-shadow: var(--shadow2) !important;
}}

/* ── File uploader ── */
div[data-testid="stFileUploader"] {{
    background: var(--input-bg) !important;
    border: 1.5px dashed {"#3d4260" if IS_DARK else "#d0d5dd"} !important;
    border-radius: 10px !important;
    transition: border-color .15s !important;
}}
div[data-testid="stFileUploader"]:hover {{
    border-color: var(--orange) !important;
}}

/* ── Expander ── */
div[data-testid="stExpander"] {{
    background: var(--expander-bg) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow) !important;
}}
div[data-testid="stExpander"] summary {{
    font-weight: 600 !important;
    color: var(--text) !important;
}}

hr {{ border-color: var(--border) !important; margin: 4px 0 !important; }}

.im-empty {{
    text-align: center;
    padding: 52px 20px;
    color: var(--muted);
}}
.im-empty-icon  {{ font-size: 44px; opacity: .45; margin-bottom: 14px; }}
.im-empty-title {{ font-size: 16px; font-weight: 600; color: {"#9ba3bf" if IS_DARK else "#344054"} !important; margin-bottom: 8px; }}
.im-empty-sub   {{ font-size: 13px; color: var(--muted) !important; font-family: var(--mono); }}
</style>
""", unsafe_allow_html=True)

# =====================================================
# NAVBAR  (with theme toggle)
# =====================================================
nav_left, nav_right = st.columns([6, 1])

with nav_left:
    st.markdown(f"""
    <div class="im-navbar">
      <div class="im-navbar-left">
        <img class="im-navbar-logo"
             src="data:image/webp;base64,{LOGO_B64}"
             alt="Instamart logo">
        <div class="im-navbar-title">
          MIM Uploader
          <span class="im-navbar-sub">Inventory Split Engine</span>
        </div>
      </div>
      <div class="im-navbar-badge">INTERNAL TOOL</div>
    </div>
    <div style="margin-bottom:20px;"></div>
    """, unsafe_allow_html=True)

# Theme toggle — floated right via a small column trick
with nav_right:
    st.markdown("""<div style="margin-top:14px; display:flex; justify-content:flex-end;">""",
                unsafe_allow_html=True)
    st.markdown('<div class="theme-toggle-btn">', unsafe_allow_html=True)
    toggle_label = "☀️ Light" if IS_DARK else "🌙 Dark"
    if st.button(toggle_label, key="theme_toggle", on_click=toggle_theme):
        pass
    st.markdown("</div></div>", unsafe_allow_html=True)

# =====================================================
# LAYOUT
# =====================================================
col_left, col_right = st.columns([1, 2.5], gap="large")

# ─────────── LEFT PANEL ─────────────────────────────
with col_left:

    st.markdown('''<div class="im-section-label">⚙ Configuration</div>''', unsafe_allow_html=True)
    max_items = st.number_input("Max Items per Group",  min_value=1, value=MAX_ITEMS, step=10,
                                help="Maximum SKUs allowed per remark group before splitting.")
    max_cost  = st.number_input("Max Cost per Group (₹)", min_value=1, value=MAX_COST,  step=10_000,
                                help="Maximum total liquidation cost allowed per remark group.")
    max_rows  = st.number_input("Max Rows per Output File", min_value=1, value=MAX_ROWS, step=1_000,
                                help="Row count after which the output is split into numbered part files.")

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    st.markdown('''<div class="im-section-label">📂 Input File</div>''', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["csv"], label_visibility="collapsed")

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    run_btn = st.button("▶  Run Splitter", use_container_width=True)

    hint_border = "#2d3148" if IS_DARK else "#e2e5ea"
    hint_color  = "#8b91a8" if IS_DARK else "#667085"
    hint_label  = "#c9cde0" if IS_DARK else "#344054"
    st.markdown(f"""
    <div style="margin-top:12px; padding:10px 13px; background:var(--hint-bg);
         border:1.5px solid {hint_border}; border-radius:8px; font-size:11.5px; color:{hint_color};
         font-family:'DM Mono',monospace; line-height:1.7;">
      <b style="color:{hint_label};">Required columns:</b><br>
      Store ID &nbsp;·&nbsp; Remarks<br>
      Quantity &nbsp;·&nbsp; Liquidation Price
    </div>
    """, unsafe_allow_html=True)

# ─────────── RIGHT PANEL ────────────────────────────
with col_right:

    if not uploaded_file and not run_btn:
        st.markdown("""
        <div class="im-empty">
          <div class="im-empty-icon">📊</div>
          <div class="im-empty-title">Upload a CSV to begin</div>
          <div class="im-empty-sub">Configure limits → upload file → click Run</div>
        </div>
        """, unsafe_allow_html=True)

    elif run_btn and not uploaded_file:
        st.markdown('''<div class="im-banner error">
          <span class="im-banner-icon">⛔</span>
          <span>Please upload a CSV file before running the splitter.</span>
        </div>''', unsafe_allow_html=True)

    elif run_btn and uploaded_file:

        # ─── LOAD CSV ─────────────────────────────
        try:
            output_df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.markdown(f'''<div class="im-banner error">
              <span class="im-banner-icon">⛔</span>
              <span>Failed to read CSV: {e}</span>
            </div>''', unsafe_allow_html=True)
            st.stop()

        # ─── SAFETY CHECKS ───────────────────────
        required_columns = {"Store ID", "Remarks", "Quantity", "Liquidation Price"}
        missing_cols = required_columns - set(output_df.columns)
        if missing_cols:
            st.markdown(f'''<div class="im-banner error">
              <span class="im-banner-icon">⛔</span>
              <span>Missing required columns: <b>{", ".join(missing_cols)}</b></span>
            </div>''', unsafe_allow_html=True)
            st.stop()

        # ─── NORMALIZATION ───────────────────────
        output_df["Quantity"] = pd.to_numeric(output_df["Quantity"], errors="coerce").fillna(0)
        output_df["Liquidation Price"] = pd.to_numeric(output_df["Liquidation Price"], errors="coerce").fillna(0)

        # ─── GROUPING & STRICT SPLITTING LOGIC ───
        final_rows    = []
        grouping_logs = []

        try:
            for (store_id, remark), group in output_df.groupby(["Store ID", "Remarks"], dropna=False):
                group = group.copy()
                group["TOTAL_COST"] = group["Quantity"] * group["Liquidation Price"]
                total_items = len(group)
                total_cost  = int(group["TOTAL_COST"].sum())
                needs_split = (total_items > max_items or total_cost > max_cost)

                if not needs_split:
                    final_rows.append(group)
                    continue

                # STRICT GREEDY SPLITTING
                suffix_index  = 0
                current_chunk = []
                current_items = 0
                current_cost  = 0
                created_variants = []

                for _, row in group.iterrows():
                    row_cost = row["TOTAL_COST"]
                    if (current_items + 1 > max_items or current_cost + row_cost > max_cost):
                        if suffix_index >= len(SUFFIXES):
                            raise ValueError(f"Suffix overflow for remark '{remark}'")
                        new_remark = f"{remark} {SUFFIXES[suffix_index]}"
                        chunk_df   = pd.DataFrame(current_chunk)
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

                if current_chunk:
                    if suffix_index >= len(SUFFIXES):
                        raise ValueError(f"Suffix overflow for remark '{remark}'")
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
                    "reasons":  [r for r in [
                        "ITEM LIMIT EXCEEDED" if total_items > max_items else None,
                        "COST LIMIT EXCEEDED" if total_cost  > max_cost  else None,
                    ] if r],
                    "variants": created_variants,
                })

        except ValueError as e:
            st.markdown(f'''<div class="im-banner error">
              <span class="im-banner-icon">⛔</span><span>{e}</span>
            </div>''', unsafe_allow_html=True)
            st.stop()

        # ─── FINAL DATAFRAME ──────────────────────
        output_df = pd.concat(final_rows, ignore_index=True)
        output_df.drop(columns=["TOTAL_COST"], errors="ignore", inplace=True)
        total_rows    = len(output_df)
        groups_split  = len(grouping_logs)
        parts_count   = math.ceil(total_rows / max_rows) if total_rows > max_rows else 1

        # ─── STATS PILLS ──────────────────────────
        st.markdown(f"""
        <div class="im-stats">
          <div class="im-stat">
            <div class="im-stat-val">{total_rows:,}</div>
            <div class="im-stat-lbl">Total Output Rows</div>
          </div>
          <div class="im-stat">
            <div class="im-stat-val">{groups_split}</div>
            <div class="im-stat-lbl">Groups Split</div>
          </div>
          <div class="im-stat">
            <div class="im-stat-val">{parts_count}</div>
            <div class="im-stat-lbl">Output File(s)</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ─── 🔔 GROUPING LOGS ────────────────────
        if grouping_logs:
            with st.expander(f"🔔  Splitting Details — {groups_split} group(s) affected", expanded=True):
                for g in grouping_logs:
                    badges = "".join(
                        f'<span class="im-log-badge">⚠ {r}</span>' for r in g["reasons"]
                    )
                    variants_html = "".join(f"<div>{v}</div>" for v in g["variants"])
                    st.markdown(f"""
                    <div class="im-log">
                      <div>
                        <span class="im-log-store">Store {g['store_id']}</span>
                        <span style="color:var(--muted)"> · </span>
                        <span style="color:var(--text)">{g['remark']}</span>
                      </div>
                      <div class="im-log-meta">
                        Items: <b>{g['items']}</b> &nbsp;|&nbsp; Cost: <b>₹{g['cost']:,}</b>
                      </div>
                      <div style="margin:4px 0">{badges}</div>
                      <div class="im-log-variant">{variants_html}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown('''<div class="im-banner success">
              <span class="im-banner-icon">✅</span>
              <span>All groups are within limits — no splitting required.</span>
            </div>''', unsafe_allow_html=True)

        # ─── OUTPUT FILES ─────────────────────────
        st.markdown('''<div class="im-section-label" style="margin-top:20px">📁 Output Files</div>''',
                    unsafe_allow_html=True)

        output_files = {}

        if total_rows <= max_rows:
            fname = "UPLOAD_FILE.csv"
            buf   = BytesIO()
            output_df.to_csv(buf, index=False)
            output_files[fname] = buf.getvalue()

            st.markdown(f"""
            <div class="im-file-row">
              <span class="im-file-icon">📄</span>
              <span class="im-file-name">{fname}</span>
              <span class="im-file-rows">{total_rows:,} rows</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('''<div class="im-banner success" style="margin-bottom:12px">
              <span class="im-banner-icon">✅</span>
              <span>Single output file ready for download.</span>
            </div>''', unsafe_allow_html=True)

        else:
            parts = math.ceil(total_rows / max_rows)
            st.markdown(f'''<div class="im-banner warning" style="margin-bottom:12px">
              <span class="im-banner-icon">⚠️</span>
              <span>Row limit exceeded ({max_rows:,} rows). Output split into <b>{parts} part(s)</b>.</span>
            </div>''', unsafe_allow_html=True)

            for i in range(parts):
                part_df = output_df.iloc[i * max_rows:(i + 1) * max_rows]
                fname   = f"MIM_UPLOADER_PART_{i + 1}.csv"
                buf     = BytesIO()
                part_df.to_csv(buf, index=False)
                output_files[fname] = buf.getvalue()

                st.markdown(f"""
                <div class="im-file-row">
                  <span class="im-file-icon">📄</span>
                  <span class="im-file-name">{fname}</span>
                  <span class="im-file-rows">{len(part_df):,} rows</span>
                </div>
                """, unsafe_allow_html=True)

        # ─── DOWNLOAD BUTTONS ─────────────────────
        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)

        if len(output_files) == 1:
            fname, data = next(iter(output_files.items()))
            st.download_button(
                label=f"⬇  Download {fname}",
                data=data,
                file_name=fname,
                mime="text/csv",
                use_container_width=True,
            )
        else:
            zip_buf = BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname, data in output_files.items():
                    zf.writestr(fname, data)
            zip_buf.seek(0)

            dl_c1, dl_c2 = st.columns(2)
            with dl_c1:
                st.download_button(
                    label="⬇  Download All as ZIP",
                    data=zip_buf.getvalue(),
                    file_name="MIM_UPLOADER_PARTS.zip",
                    mime="application/zip",
                    use_container_width=True,
                )
            with dl_c2:
                with st.expander("⬇  Download Individual Files"):
                    for fname, data in output_files.items():
                        st.download_button(
                            label=f"⬇  {fname}",
                            data=data,
                            file_name=fname,
                            mime="text/csv",
                            use_container_width=True,
                            key=fname,
                        )
