#!/usr/bin/env python3
"""
VIDIMPORT · Dashboard FCST
Herramienta de comparación de pronósticos semanales de fruta fresca.
─────────────────────────────────────────────────────────
Deploy: Streamlit Community Cloud (share.streamlit.io)
Uso local: streamlit run app.py
─────────────────────────────────────────────────────────
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re, io
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VIDIMPORT · FCST Dashboard",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: #0d1117 !important;
    color: #c9d1d9 !important;
    font-family: 'Segoe UI', system-ui, sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d !important;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: #21262d !important; border-color: #30363d !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #161b22; border-radius: 10px; padding: 4px; gap: 4px;
    border: 1px solid #30363d;
}
.stTabs [data-baseweb="tab"] {
    color: #8b949e !important; border-radius: 7px; padding: 8px 22px !important;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: #21262d !important; color: #58a6ff !important;
}
.kpi-row { display: flex; gap: 12px; margin-bottom: 16px; }
.kpi {
    flex: 1; background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 16px 14px; text-align: center;
}
.kpi-val { font-size: 1.9rem; font-weight: 700; color: #58a6ff; line-height: 1.1; }
.kpi-lbl { font-size: 0.78rem; color: #8b949e; margin-top: 5px; text-transform: uppercase; letter-spacing: .05em; }
.kpi-delta { font-size: 0.9rem; margin-top: 3px; font-weight: 600; }
.up   { color: #3fb950; }
.dn   { color: #f85149; }
.neu  { color: #8b949e; }
.sec-title {
    font-size: 1.05rem; font-weight: 600; color: #58a6ff;
    border-bottom: 1px solid #30363d; padding-bottom: 6px;
    margin: 20px 0 10px 0;
}
.alert-banner {
    background: linear-gradient(90deg,#3d0a0a,#1f1117);
    border-left: 4px solid #f85149; border-radius: 8px;
    padding: 10px 16px; margin-bottom: 14px;
}
.warn-banner {
    background: linear-gradient(90deg,#2d2000,#1a1a00);
    border-left: 4px solid #d29922; border-radius: 8px;
    padding: 10px 16px; margin-bottom: 14px;
}
[data-testid="stDataFrame"] iframe { border-radius: 8px !important; }
.chip-red  { background:#3d0a0a; color:#f85149; border:1px solid #f85149; border-radius:20px; padding:2px 10px; font-size:.8rem; font-weight:600; }
.chip-grn  { background:#0a2d0a; color:#3fb950; border:1px solid #3fb950; border-radius:20px; padding:2px 10px; font-size:.8rem; font-weight:600; }
.chip-neu  { background:#1c1c1c; color:#8b949e; border:1px solid #30363d; border-radius:20px; padding:2px 10px; font-size:.8rem; }
.stSelectbox > div > div, .stMultiSelect > div > div, .stTextInput > div > div {
    background: #161b22 !important; border-color: #30363d !important; color: #c9d1d9 !important;
}
div[data-testid="stMetricValue"] { color: #58a6ff !important; }
hr { border-color: #30363d !important; }

/* Upload zone styling */
[data-testid="stFileUploader"] {
    background: #161b22 !important;
    border: 1.5px dashed #30363d !important;
    border-radius: 10px !important;
    padding: 8px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #58a6ff !important;
}

/* Welcome screen */
.welcome-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 32px 40px;
    text-align: center;
    max-width: 600px;
    margin: 60px auto;
}
.step-row {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    background: #21262d;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 10px 0;
    text-align: left;
}
.step-num {
    background: #58a6ff;
    color: #0d1117;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.85rem;
    flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
CADENA_NORM = {
    "la comer":   "La Comer",
    "samss":      "Sam's",
    "sam's":      "Sam's",
    "sams":       "Sam's",
    "city market":"City Market",
    "walmart":    "Walmart",
    "chedraui":   "Chedraui",
    "costco":     "Costco",
    "futurama":   "Futurama",
    "casa ley":   "Casa Ley",
    "fresko":     "Fresko",
}
CADENA_COLORS = {
    "Walmart":     "#2196F3",
    "Sam's":       "#1565C0",
    "La Comer":    "#E53935",
    "City Market": "#9C27B0",
    "Fresko":      "#43A047",
    "Chedraui":    "#FB8C00",
    "Costco":      "#0288D1",
    "Casa Ley":    "#E53935",
    "Futurama":    "#FDD835",
}
BG    = "#0d1117"
SURF  = "#161b22"
SURF2 = "#21262d"
BORDER= "#30363d"

def ptpl(fig, height=None):
    upd = dict(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color="#c9d1d9", family="Segoe UI, system-ui, sans-serif", size=12),
        xaxis=dict(gridcolor=SURF2, linecolor=BORDER, zerolinecolor=SURF2),
        yaxis=dict(gridcolor=SURF2, linecolor=BORDER, zerolinecolor=SURF2),
        legend=dict(bgcolor=SURF, bordercolor=BORDER, borderwidth=1),
        margin=dict(l=40, r=20, t=40, b=50),
    )
    if height:
        upd["height"] = height
    fig.update_layout(**upd)
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def norm_cadena(v):
    if pd.isna(v): return None
    s = str(v).strip()
    return CADENA_NORM.get(s.lower(), s) if s else None

def extract_week_num(filename: str):
    m = re.search(r"W(\d+)", filename, re.IGNORECASE)
    return int(m.group(1)) if m else None

def week_pos(n: int) -> int:
    return (n - 36) if n >= 36 else (n + 16)

def fmt_pct(v, show_sign=True):
    if v == np.inf or v == float("inf"): return "NUEVO ∞"
    if pd.isna(v): return "—"
    prefix = "+" if (show_sign and v > 0) else ""
    return f"{prefix}{v:.1f}%"

def fmt_vol(v):
    if pd.isna(v): return "—"
    return f"{int(v):,}"

def color_cadena(name):
    return CADENA_COLORS.get(name, "#8b949e")

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING  ·  Acepta bytes (desde st.file_uploader)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="📂 Procesando archivo…")
def load_file(file_bytes: bytes, filename: str):
    """
    Carga un archivo FCST desde bytes (st.file_uploader).
    Retorna: (df, week_num, week_labels)
    """
    raw = pd.read_excel(io.BytesIO(file_bytes), header=4, engine="openpyxl")
    wk_num = extract_week_num(filename)

    # Deduplicar columnas
    seen = {}
    cols_clean = []
    for c in raw.columns:
        k = str(c)
        seen[k] = seen.get(k, 0) + 1
        cols_clean.append(f"{k}__d{seen[k]}" if seen[k] > 1 else k)
    raw.columns = cols_clean

    # Columnas clave (posicional)
    df = pd.DataFrame()
    df["Cadena"]   = raw.iloc[:, 3].apply(norm_cadena)
    df["Especie"]  = raw.iloc[:, 4].fillna("").astype(str).str.strip()
    df["Variedad"] = raw.iloc[:, 5].fillna("").astype(str).str.strip()
    df["Tipo"]     = raw.iloc[:, 6].fillna("").astype(str).str.strip()
    df["SKU"]      = raw.iloc[:, 13].fillna("").astype(str).str.strip()
    df["Key"]      = (df["Cadena"].fillna("") + " ║ " +
                      df["Especie"] + " ║ " +
                      df["Variedad"] + " ║ " + df["Tipo"])

    # Columnas de semana (primera ocurrencia por número)
    seen_wk = {}
    wk_labels = []
    for c in cols_clean:
        m = re.match(r"^W-(\d+)(__d\d+)?$", c)
        if m:
            n = int(m.group(1))
            if n in seen_wk:
                continue
            seen_wk[n] = c
            lbl = f"W{n:02d}"
            df[lbl] = pd.to_numeric(raw[c], errors="coerce").fillna(0)
            wk_labels.append(lbl)

    wk_labels.sort(key=lambda w: week_pos(int(w[1:])))

    valid = (df["Cadena"].notna() &
             ~df["Cadena"].isin(["nan", "None", ""]) &
             df["Cadena"].str.len().gt(0))
    df = df[valid].reset_index(drop=True)

    return df, wk_num, wk_labels


# ─────────────────────────────────────────────────────────────────────────────
# COMPARISON ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def compare(df_old, wk_old, wk_labels_old, df_new, wk_new, wk_labels_new):
    common = sorted(
        set(wk_labels_old) & set(wk_labels_new),
        key=lambda w: week_pos(int(w[1:])),
    )
    KEY_COLS = ["Key", "Cadena", "Especie", "Variedad", "Tipo", "SKU"]
    agg_o = df_old.groupby(KEY_COLS, dropna=False)[common].sum().reset_index()
    agg_n = df_new.groupby(KEY_COLS, dropna=False)[common].sum().reset_index()
    sfx_o = f"_W{wk_old:02d}"
    sfx_n = f"_W{wk_new:02d}"
    mg = pd.merge(agg_o, agg_n, on=["Key","Cadena","Especie","Variedad","Tipo"],
                  how="outer", suffixes=(sfx_o, sfx_n))
    for w in common:
        co = f"{w}{sfx_o}"; cn = f"{w}{sfx_n}"
        mg[co] = mg.get(co, pd.Series(0, index=mg.index)).fillna(0)
        mg[cn] = mg.get(cn, pd.Series(0, index=mg.index)).fillna(0)
        diff = mg[cn] - mg[co]
        pct  = np.where(mg[co]==0, np.where(mg[cn]>0, np.inf, 0.0), (diff/mg[co])*100)
        mg[f"{w}_VAR"] = diff
        mg[f"{w}_PCT"] = pct
    return mg, common, sfx_o, sfx_n

def build_alerts(mg, common, sfx_o, sfx_n, threshold, cadenas_sel, species_sel, focus_weeks):
    rows = []
    for _, r in mg.iterrows():
        if cadenas_sel and r.get("Cadena") not in cadenas_sel: continue
        if species_sel  and r.get("Especie")  not in species_sel:  continue
        for w in focus_weeks:
            pct = r.get(f"{w}_PCT", 0)
            var = r.get(f"{w}_VAR", 0)
            vo  = r.get(f"{w}{sfx_o}", 0)
            vn  = r.get(f"{w}{sfx_n}", 0)
            if (abs(pct) >= threshold or pct == np.inf) and (vo > 0 or vn > 0):
                rows.append({
                    "Cadena":    r.get("Cadena",""),
                    "Especie":   r.get("Especie",""),
                    "Variedad":  r.get("Variedad",""),
                    "Tipo":      r.get("Tipo",""),
                    "Semana":    w,
                    "Vol Base":  int(vo),
                    "Vol Nuevo": int(vn),
                    "Δ Cajas":   int(var),
                    "Δ %":       round(pct if pct != np.inf else 999, 1),
                    "Dir":       "▲" if var > 0 else ("▼" if var < 0 else "—"),
                })
    if not rows: return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("Δ %", key=abs, ascending=False).reset_index(drop=True)

def weekly_totals(mg, common, sfx_o, sfx_n):
    rows = []
    for w in common:
        vo = mg.get(f"{w}{sfx_o}", pd.Series([0])).sum()
        vn = mg.get(f"{w}{sfx_n}", pd.Series([0])).sum()
        rows.append({"Semana":w,"Base":vo,"Nuevo":vn,"Δ":vn-vo,
                     "Δ%":((vn-vo)/vo*100) if vo>0 else 0})
    return pd.DataFrame(rows)

def cadena_totals(mg, common, sfx_o, sfx_n, focus_week):
    co = f"{focus_week}{sfx_o}"; cn = f"{focus_week}{sfx_n}"
    agg = (mg.groupby("Cadena")[[co,cn]].sum()
             .rename(columns={co:"Base",cn:"Nuevo"}).reset_index())
    agg["Δ"]  = agg["Nuevo"] - agg["Base"]
    agg["Δ%"] = np.where(agg["Base"]>0,(agg["Δ"]/agg["Base"])*100,0)
    return agg.sort_values("Nuevo",ascending=False)


# ─────────────────────────────────────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def bar_cadena_comparison(df, wk_old, wk_new):
    fig = go.Figure()
    fig.add_bar(x=df["Cadena"],y=df["Base"],name=f"W{wk_old:02d} (base)",
                marker_color=[color_cadena(c) for c in df["Cadena"]],opacity=0.45)
    fig.add_bar(x=df["Cadena"],y=df["Nuevo"],name=f"W{wk_new:02d} (nuevo)",
                marker_color=[color_cadena(c) for c in df["Cadena"]],opacity=1.0)
    fig.update_layout(barmode="group",height=360)
    return ptpl(fig)

def waterfall_cadena(df, focus_week):
    df2 = df[df["Δ"]!=0].copy()
    colors = ["#3fb950" if d>0 else "#f85149" for d in df2["Δ"]]
    fig = go.Figure(go.Bar(
        x=df2["Cadena"],y=df2["Δ"],marker_color=colors,
        text=[f"{'+' if d>0 else ''}{int(d):,}" for d in df2["Δ"]],
        textposition="outside",name="Variación"))
    fig.update_layout(title=f"Variación neta {focus_week}",height=320,yaxis_title="Δ Cajas")
    return ptpl(fig)

def line_weekly(totals_df, wk_old, wk_new, title=""):
    fig = go.Figure()
    fig.add_scatter(x=totals_df["Semana"],y=totals_df["Base"],mode="lines+markers",
                    name=f"FCST W{wk_old:02d}",
                    line=dict(color="#8b949e",dash="dot",width=2),marker=dict(size=5))
    fig.add_scatter(x=totals_df["Semana"],y=totals_df["Nuevo"],mode="lines+markers",
                    name=f"FCST W{wk_new:02d}",
                    line=dict(color="#58a6ff",width=2.5),marker=dict(size=6))
    fig.update_layout(title=title,height=350,xaxis_title="Semana",yaxis_title="Cajas")
    return ptpl(fig)

def heatmap_cadena_weeks(mg, common, sfx_n, cadenas):
    data_rows = []
    for cad in cadenas:
        sub = mg[mg["Cadena"]==cad]
        row_vals = []
        for w in common:
            pct_vals = sub[f"{w}_PCT"].replace([np.inf,-np.inf],np.nan)
            row_vals.append(pct_vals.mean())
        data_rows.append(row_vals)
    z = np.clip(np.array(data_rows,dtype=float),-100,100)
    fig = go.Figure(go.Heatmap(
        z=z,x=[w[1:] for w in common],y=cadenas,
        colorscale=[[0,"#f85149"],[0.45,"#3d1f1f"],[0.5,"#21262d"],[0.55,"#1f3d1f"],[1,"#3fb950"]],
        zmid=0,zmin=-100,zmax=100,
        colorbar=dict(title="Δ %",ticksuffix="%",bgcolor=SURF,bordercolor=BORDER),
        text=[[f"{v:.0f}%" if not np.isnan(v) else "" for v in row] for row in z],
        texttemplate="%{text}",
        hovertemplate="Cadena: %{y}<br>Semana: W%{x}<br>Variación: %{z:.1f}%<extra></extra>"))
    fig.update_layout(title="Mapa de calor — Variación % por cadena × semana",height=300)
    return ptpl(fig)

def sku_trend(mg, key, common, sfx_o, sfx_n, wk_old, wk_new):
    sub = mg[mg["Key"]==key]
    if sub.empty: return None
    row = sub.iloc[0]
    vals_o = [row.get(f"{w}{sfx_o}",0) for w in common]
    vals_n = [row.get(f"{w}{sfx_n}",0) for w in common]
    fig = go.Figure()
    fig.add_scatter(x=common,y=vals_o,mode="lines+markers",name=f"FCST W{wk_old:02d}",
                    line=dict(color="#8b949e",dash="dot",width=2),marker=dict(size=5))
    fig.add_scatter(x=common,y=vals_n,mode="lines+markers",name=f"FCST W{wk_new:02d}",
                    line=dict(color="#58a6ff",width=2.5),marker=dict(size=7),
                    fill="tonexty",fillcolor="rgba(88,166,255,0.08)")
    title_sku = f"{row.get('Cadena','')} · {row.get('Variedad','')} · {row.get('Tipo','')}"
    fig.update_layout(title=f"Tendencia: {title_sku}",height=380,
                      xaxis_title="Semana",yaxis_title="Cajas")
    return ptpl(fig)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR  ·  Upload de archivos
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:12px 0 8px'>
      <span style='font-size:1.6rem'>🍎</span><br>
      <span style='font-size:.95rem;font-weight:700;color:#58a6ff;letter-spacing:.04em'>VIDIMPORT · FCST</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**📂 Cargar archivos FCST**")
    st.caption("Arrastra o selecciona los 2 archivos Excel semanales")

    file_old = st.file_uploader(
        "Semana BASE (anterior)",
        type=["xlsx"],
        key="upload_old",
        help="Ej: Fcst_PT_Comercial_W24Final.xlsx",
    )
    file_new = st.file_uploader(
        "Semana NUEVA (actual)",
        type=["xlsx"],
        key="upload_new",
        help="Ej: Fcst_PT_Comercial_W25.xlsx",
    )

    files_ready = file_old is not None and file_new is not None

    if files_ready:
        st.markdown("---")
        st.markdown("**⚙️ Parámetros**")
        threshold = st.slider("Umbral de alerta (%)", 5, 30, 10, step=5)
        st.markdown("---")
        st.markdown("**🔍 Filtros globales**")


# ─────────────────────────────────────────────────────────────────────────────
# PANTALLA DE BIENVENIDA  ·  Si no hay archivos cargados
# ─────────────────────────────────────────────────────────────────────────────
if not files_ready:
    st.markdown("""
    <div class="welcome-card">
      <div style="font-size:3rem;margin-bottom:12px">🍎</div>
      <h2 style="color:#58a6ff;font-size:1.4rem;margin-bottom:6px">Dashboard FCST · VIDIMPORT</h2>
      <p style="color:#8b949e;font-size:.9rem;margin-bottom:24px">
        Comparativo semanal de pronósticos de fruta fresca
      </p>

      <div class="step-row">
        <div class="step-num">1</div>
        <div>
          <b style="color:#c9d1d9">Sube el archivo BASE</b><br>
          <span style="color:#8b949e;font-size:.85rem">El FCST de la semana anterior
          — ej: <code>Fcst_PT_Comercial_W24Final.xlsx</code></span>
        </div>
      </div>

      <div class="step-row">
        <div class="step-num">2</div>
        <div>
          <b style="color:#c9d1d9">Sube el archivo NUEVO</b><br>
          <span style="color:#8b949e;font-size:.85rem">El FCST de esta semana
          — ej: <code>Fcst_PT_Comercial_W25.xlsx</code></span>
        </div>
      </div>

      <div class="step-row">
        <div class="step-num">3</div>
        <div>
          <b style="color:#c9d1d9">El análisis aparece automáticamente</b><br>
          <span style="color:#8b949e;font-size:.85rem">Variaciones, alertas, tendencias
          y top items por cadena</span>
        </div>
      </div>

      <p style="color:#30363d;font-size:.8rem;margin-top:20px">
        ← Usa los botones de carga en el panel izquierdo
      </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# CARGA Y COMPARACIÓN
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("Procesando archivos…"):
    bytes_old = file_old.read()
    bytes_new = file_new.read()

    df_old, wk_old, wk_lbls_old = load_file(bytes_old, file_old.name)
    df_new, wk_new, wk_lbls_new = load_file(bytes_new, file_new.name)

# Validar que los números de semana se detectaron
if wk_old is None or wk_new is None:
    st.error("⚠️ No se pudo detectar el número de semana en el nombre del archivo. "
             "Asegúrate de que el nombre incluya 'W24', 'W25', etc.")
    st.stop()

if wk_old == wk_new:
    st.error("⚠️ Los dos archivos tienen el mismo número de semana. "
             "Sube archivos de semanas diferentes.")
    st.stop()

# Si están invertidos, corrégelos automáticamente
if wk_old > wk_new:
    df_old, df_new = df_new, df_old
    wk_old, wk_new = wk_new, wk_old
    wk_lbls_old, wk_lbls_new = wk_lbls_new, wk_lbls_old

mg, common, sfx_o, sfx_n = compare(
    df_old, wk_old, wk_lbls_old,
    df_new, wk_new, wk_lbls_new,
)

# Filtros sidebar (después de cargar)
with st.sidebar:
    all_cadenas = sorted(mg["Cadena"].dropna().unique().tolist())
    cadenas_sel = st.multiselect("Cadena(s)", all_cadenas, default=[],
                                 help="Vacío = todas")
    all_species = sorted(mg["Especie"].dropna().unique().tolist())
    species_sel = st.multiselect("Especie(s)", all_species, default=[])
    st.markdown("---")
    st.caption(f"📊 {len(mg)} SKUs · {len(common)} semanas")
    st.caption(f"🗂 Base: **{file_old.name}**")
    st.caption(f"🗂 Nuevo: **{file_new.name}**")

# Semana actual y semanas futuras
current_lbl = f"W{wk_new:02d}"
fwd_weeks   = [w for w in common if week_pos(int(w[1:]))>=week_pos(wk_new)]
focus_weeks = fwd_weeks if fwd_weeks else common

# Filtro aplicado
mg_filt = mg.copy()
if cadenas_sel: mg_filt = mg_filt[mg_filt["Cadena"].isin(cadenas_sel)]
if species_sel:  mg_filt = mg_filt[mg_filt["Especie"].isin(species_sel)]


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style='color:#58a6ff;margin-bottom:0'>🍎 Dashboard FCST · Comparativo Semanal</h1>
<p style='color:#8b949e;margin-top:4px'>
  Comparando <b style='color:#c9d1d9'>{file_old.name}</b>
  vs <b style='color:#58a6ff'>{file_new.name}</b>
  — Umbral de alerta: <b style='color:#f85149'>{threshold}%</b>
</p>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# KPIs GLOBALES
# ─────────────────────────────────────────────────────────────────────────────
col_curr_o = f"{current_lbl}{sfx_o}"
col_curr_n = f"{current_lbl}{sfx_n}"

vol_base = mg_filt[col_curr_o].sum() if col_curr_o in mg_filt else 0
vol_new  = mg_filt[col_curr_n].sum() if col_curr_n in mg_filt else 0
vol_diff = vol_new - vol_base
vol_pct  = (vol_diff / vol_base * 100) if vol_base > 0 else 0

df_alerts_all = build_alerts(mg_filt, common, sfx_o, sfx_n, threshold,
                              cadenas_sel if cadenas_sel else None,
                              species_sel if species_sel else None,
                              focus_weeks)
n_alerts = len(df_alerts_all) if not df_alerts_all.empty else 0
n_up     = (df_alerts_all["Δ Cajas"]>0).sum() if not df_alerts_all.empty else 0
n_down   = (df_alerts_all["Δ Cajas"]<0).sum() if not df_alerts_all.empty else 0
cadenas_aff = df_alerts_all["Cadena"].nunique() if not df_alerts_all.empty else 0

delta_cls = "up" if vol_diff>=0 else "dn"
delta_sym = "▲" if vol_diff>=0 else "▼"

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi">
    <div class="kpi-val">{fmt_vol(vol_base)}</div>
    <div class="kpi-lbl">Cajas W{wk_old:02d} (base)</div>
  </div>
  <div class="kpi">
    <div class="kpi-val">{fmt_vol(vol_new)}</div>
    <div class="kpi-lbl">Cajas W{wk_new:02d} (nuevo)</div>
    <div class="kpi-delta {delta_cls}">{delta_sym} {fmt_vol(abs(vol_diff))} &nbsp;({fmt_pct(vol_pct)})</div>
  </div>
  <div class="kpi">
    <div class="kpi-val" style="color:#f85149">{n_alerts}</div>
    <div class="kpi-lbl">Alertas &gt;{threshold}%</div>
    <div class="kpi-delta">
      <span class="up">▲ {n_up} suben</span> &nbsp;
      <span class="dn">▼ {n_down} bajan</span>
    </div>
  </div>
  <div class="kpi">
    <div class="kpi-val">{cadenas_aff}</div>
    <div class="kpi-lbl">Cadenas con cambios</div>
  </div>
  <div class="kpi">
    <div class="kpi-val">{len(focus_weeks)}</div>
    <div class="kpi-lbl">Semanas analizadas</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Resumen", "⚠️ Alertas", "🏬 Por Cadena", "🍎 Por Item", "📈 Tendencia"
])

# ═══ TAB 1 — RESUMEN ════════════════════════════════════════════════════════
with tab1:
    totals = weekly_totals(mg_filt, common, sfx_o, sfx_n)
    st.plotly_chart(
        line_weekly(totals, wk_old, wk_new,
                    f"Volumen total de cajas — W{wk_old:02d} vs W{wk_new:02d}"),
        use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-title">📦 Volumen por Cadena — semana actual</div>',
                    unsafe_allow_html=True)
        cad_df = cadena_totals(mg_filt, common, sfx_o, sfx_n, current_lbl)
        cad_nz = cad_df[(cad_df["Base"]>0)|(cad_df["Nuevo"]>0)]
        if not cad_nz.empty:
            st.plotly_chart(bar_cadena_comparison(cad_nz, wk_old, wk_new),
                            use_container_width=True)
        else:
            st.info("Sin volumen en la semana actual.")

    with c2:
        st.markdown('<div class="sec-title">🔄 Variación neta por Cadena</div>',
                    unsafe_allow_html=True)
        cad_var = cad_nz[cad_nz["Δ"]!=0] if not cad_nz.empty else pd.DataFrame()
        if not cad_var.empty:
            st.plotly_chart(waterfall_cadena(cad_var, current_lbl),
                            use_container_width=True)
        else:
            st.success("✅ Sin variaciones en la semana actual.")

    st.markdown('<div class="sec-title">🌡️ Mapa de Calor — Variación % por Cadena × Semana</div>',
                unsafe_allow_html=True)
    cads_heat = cadenas_sel if cadenas_sel else all_cadenas
    wks_heat  = fwd_weeks[:20]
    if cads_heat and wks_heat:
        st.plotly_chart(heatmap_cadena_weeks(mg_filt, wks_heat, sfx_n, cads_heat),
                        use_container_width=True)

    st.markdown(f'<div class="sec-title">🏆 Top 15 items por volumen — {current_lbl}</div>',
                unsafe_allow_html=True)
    if col_curr_o in mg_filt.columns and col_curr_n in mg_filt.columns:
        top15 = (mg_filt
                 .assign(Vol_base=lambda x: x[col_curr_o],
                         Vol_nuevo=lambda x: x[col_curr_n])
                 .sort_values("Vol_nuevo", ascending=False)
                 .head(15))
        top15["Label"] = top15.apply(lambda r: f"{r['Cadena']} · {r['Variedad']}", axis=1)
        fig_top = px.bar(
            top15.iloc[::-1],
            x="Vol_nuevo", y="Label",
            orientation="h", color="Cadena",
            color_discrete_map=CADENA_COLORS,
            title=f"Top 15 por volumen — {current_lbl}", height=440)
        st.plotly_chart(ptpl(fig_top), use_container_width=True)


# ═══ TAB 2 — ALERTAS ════════════════════════════════════════════════════════
with tab2:
    st.markdown(f"""
    <div class="alert-banner">
      <b>⚠️ Alertas de variación &gt; {threshold}%</b> —
      Items con cambio significativo entre W{wk_old:02d} y W{wk_new:02d}
      en semanas futuras.
    </div>
    """, unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        dir_filter = st.radio("Dirección", ["Todos","Solo alzas ▲","Solo bajas ▼"],
                              horizontal=True)
    with col_f2:
        sem_filter = st.selectbox("Semana",
                                  ["Todas las semanas futuras"] + focus_weeks)
    with col_f3:
        cad_alert = st.multiselect("Cadena", all_cadenas, default=[], key="alert_cad")

    fw_alert  = [sem_filter] if sem_filter!="Todas las semanas futuras" else focus_weeks
    cad_alert2 = cad_alert or (cadenas_sel if cadenas_sel else None)
    sp_alert   = species_sel if species_sel else None

    df_a = build_alerts(mg, common, sfx_o, sfx_n, threshold,
                        cad_alert2, sp_alert, fw_alert)
    if dir_filter=="Solo alzas ▲" and not df_a.empty:
        df_a = df_a[df_a["Δ Cajas"]>0]
    elif dir_filter=="Solo bajas ▼" and not df_a.empty:
        df_a = df_a[df_a["Δ Cajas"]<0]

    if df_a.empty:
        st.success(f"✅ Ningún item supera el {threshold}% en las semanas seleccionadas.")
    else:
        n2=len(df_a); u2=(df_a["Δ Cajas"]>0).sum(); d2=(df_a["Δ Cajas"]<0).sum()
        st.markdown(f"""
        <p><b>{n2}</b> registros &nbsp;·&nbsp;
          <span class="chip-grn">▲ {u2} suben</span> &nbsp;
          <span class="chip-red">▼ {d2} bajan</span>
        </p>""", unsafe_allow_html=True)

        def color_pct(val):
            if isinstance(val,(int,float)):
                if val>=threshold:  return "background-color:#0a3d0a; color:#3fb950"
                elif val<=-threshold: return "background-color:#3d0a0a; color:#f85149"
            return ""

        styled = (df_a.style
                  .map(color_pct, subset=["Δ %"])
                  .format({"Vol Base":"{:,.0f}","Vol Nuevo":"{:,.0f}",
                           "Δ Cajas":"{:+,.0f}","Δ %":"{:+.1f}%"}))
        st.dataframe(styled, use_container_width=True, height=420)

        buf = io.BytesIO()
        df_a.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        st.download_button("📥 Exportar alertas a Excel", data=buf,
                           file_name=f"alertas_W{wk_old:02d}_vs_W{wk_new:02d}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.markdown('<div class="sec-title">📊 Items con mayor variación absoluta</div>',
                    unsafe_allow_html=True)
        top_al = df_a.head(15).copy()
        top_al["Label"] = top_al["Cadena"]+" · "+top_al["Variedad"]+" ("+top_al["Semana"]+")"
        fig_al = go.Figure(go.Bar(
            x=top_al["Δ Cajas"][::-1], y=top_al["Label"][::-1],
            orientation="h",
            marker_color=top_al["Δ Cajas"][::-1].apply(
                lambda v: "#3fb950" if v>0 else "#f85149").tolist(),
            text=[f"{v:+,.0f}" for v in top_al["Δ Cajas"][::-1]],
            textposition="outside"))
        fig_al.update_layout(title="Top 15 variaciones",height=440,xaxis_title="Δ Cajas")
        st.plotly_chart(ptpl(fig_al), use_container_width=True)


# ═══ TAB 3 — POR CADENA ═════════════════════════════════════════════════════
with tab3:
    cadena_sel3 = st.selectbox("Cadena", all_cadenas, key="tab3_cad")
    semana_sel3 = st.select_slider("Semana de enfoque", options=common,
                                    value=current_lbl if current_lbl in common else common[0])
    mg_c3 = mg[mg["Cadena"]==cadena_sel3]

    if mg_c3.empty:
        st.warning("Sin datos para esta cadena.")
    else:
        co3=f"{semana_sel3}{sfx_o}"; cn3=f"{semana_sel3}{sfx_n}"
        vo3=mg_c3[co3].sum() if co3 in mg_c3.columns else 0
        vn3=mg_c3[cn3].sum() if cn3 in mg_c3.columns else 0
        d3=vn3-vo3; p3=(d3/vo3*100) if vo3>0 else 0
        cl3="up" if d3>=0 else "dn"; sy3="▲" if d3>=0 else "▼"

        st.markdown(f"""
        <div class="kpi-row">
          <div class="kpi"><div class="kpi-val">{fmt_vol(vo3)}</div>
            <div class="kpi-lbl">{cadena_sel3} · Base W{wk_old:02d}</div></div>
          <div class="kpi"><div class="kpi-val">{fmt_vol(vn3)}</div>
            <div class="kpi-lbl">{cadena_sel3} · Nuevo W{wk_new:02d}</div>
            <div class="kpi-delta {cl3}">{sy3} {fmt_vol(abs(d3))} ({fmt_pct(p3)})</div>
          </div>
        </div>""", unsafe_allow_html=True)

        det = mg_c3.assign(
            Vol_base=mg_c3[co3] if co3 in mg_c3.columns else 0,
            Vol_nuevo=mg_c3[cn3] if cn3 in mg_c3.columns else 0)
        det = det[(det["Vol_base"]>0)|(det["Vol_nuevo"]>0)].copy()
        det = det.sort_values("Vol_nuevo",ascending=False).head(25)
        det["Label"] = det["Variedad"]+" · "+det["Tipo"]

        if not det.empty:
            fig_c3=go.Figure()
            fig_c3.add_bar(y=det["Label"],x=det["Vol_base"],orientation="h",
                           name=f"W{wk_old:02d}",marker_color=SURF2,opacity=0.7)
            fig_c3.add_bar(y=det["Label"],x=det["Vol_nuevo"],orientation="h",
                           name=f"W{wk_new:02d}",marker_color=color_cadena(cadena_sel3))
            fig_c3.update_layout(barmode="overlay",
                                 title=f"{cadena_sel3} — Items · {semana_sel3}",
                                 height=max(360,len(det)*25),xaxis_title="Cajas")
            st.plotly_chart(ptpl(fig_c3),use_container_width=True)

        cad_t3=[{"Semana":w,
                  "Base":mg_c3[f"{w}{sfx_o}"].sum() if f"{w}{sfx_o}" in mg_c3.columns else 0,
                  "Nuevo":mg_c3[f"{w}{sfx_n}"].sum() if f"{w}{sfx_n}" in mg_c3.columns else 0}
                for w in common]
        st.plotly_chart(line_weekly(pd.DataFrame(cad_t3),wk_old,wk_new,
                                    f"{cadena_sel3} · Tendencia semanal"),
                        use_container_width=True)

        with st.expander("📋 Tabla detallada"):
            show_wks = focus_weeks[:8]
            tbl_cols=(["Especie","Variedad","Tipo"]+
                      [f"{w}{sfx_o}" for w in show_wks if f"{w}{sfx_o}" in mg_c3.columns]+
                      [f"{w}{sfx_n}" for w in show_wks if f"{w}{sfx_n}" in mg_c3.columns])
            rmap={f"{w}{sfx_o}":f"{w} Base" for w in show_wks}
            rmap.update({f"{w}{sfx_n}":f"{w} Nuevo" for w in show_wks})
            st.dataframe(mg_c3[[c for c in tbl_cols if c in mg_c3.columns]]
                         .rename(columns=rmap), use_container_width=True)


# ═══ TAB 4 — POR ITEM ═══════════════════════════════════════════════════════
with tab4:
    c4a,c4b=st.columns(2)
    with c4a: cadena_sel4=st.selectbox("Cadena",all_cadenas,key="tab4_cad")
    with c4b:
        vars4=sorted(mg[mg["Cadena"]==cadena_sel4]["Variedad"].dropna().unique().tolist())
        variedad_sel4=st.selectbox("Variedad",vars4,key="tab4_var")

    tipos4=sorted(mg[(mg["Cadena"]==cadena_sel4)&
                     (mg["Variedad"]==variedad_sel4)]["Tipo"].dropna().unique().tolist())
    tipo_sel4=st.selectbox("Tipo",tipos4 if tipos4 else ["—"],key="tab4_tipo")

    match4=mg[(mg["Cadena"]==cadena_sel4)&
              (mg["Variedad"]==variedad_sel4)&
              (mg["Tipo"]==tipo_sel4)]

    if match4.empty:
        st.warning("Sin datos para esta combinación.")
    else:
        key4=match4.iloc[0]["Key"]
        row4=match4.iloc[0]
        co4=f"{current_lbl}{sfx_o}"; cn4=f"{current_lbl}{sfx_n}"
        vo4=row4.get(co4,0); vn4=row4.get(cn4,0); d4=vn4-vo4
        cl4="up" if d4>=0 else "dn"; sy4="▲" if d4>=0 else "▼"

        st.markdown(f"""
        <div class="kpi-row">
          <div class="kpi"><div class="kpi-val">{fmt_vol(vo4)}</div>
            <div class="kpi-lbl">W{wk_new:02d} · Base</div></div>
          <div class="kpi"><div class="kpi-val">{fmt_vol(vn4)}</div>
            <div class="kpi-lbl">W{wk_new:02d} · Nuevo</div>
            <div class="kpi-delta {cl4}">{sy4} {fmt_vol(abs(d4))}</div></div>
        </div>""", unsafe_allow_html=True)

        fig_sku=sku_trend(match4,key4,common,sfx_o,sfx_n,wk_old,wk_new)
        if fig_sku: st.plotly_chart(fig_sku,use_container_width=True)

        wk_rows=[]
        for w in common:
            vo_w=row4.get(f"{w}{sfx_o}",0); vn_w=row4.get(f"{w}{sfx_n}",0)
            dv=vn_w-vo_w; pw=(dv/vo_w*100) if vo_w>0 else (np.inf if vn_w>0 else 0)
            wk_rows.append({"Semana":w,
                            f"W{wk_old:02d}":int(vo_w),f"W{wk_new:02d}":int(vn_w),
                            "Δ Cajas":int(dv),
                            "Δ %":round(pw,1) if pw!=np.inf else "NUEVO",
                            "Estado":"🟢" if dv>0 else ("🔴" if dv<0 else "⚪")})
        df_wk4=pd.DataFrame(wk_rows)
        df_wk4_nz=df_wk4[(df_wk4[f"W{wk_old:02d}"]>0)|(df_wk4[f"W{wk_new:02d}"]>0)]
        if not df_wk4_nz.empty:
            st.markdown('<div class="sec-title">📋 Semana a semana</div>',unsafe_allow_html=True)
            st.dataframe(df_wk4_nz,use_container_width=True)


# ═══ TAB 5 — TENDENCIA ══════════════════════════════════════════════════════
with tab5:
    st.markdown(f"""
    <div class="warn-banner">
      <b>📈 Tendencia histórica y proyección</b> —
      Gris punteado = FCST W{wk_old:02d} (base). Azul = FCST W{wk_new:02d} (revisado).
      La línea vertical marca la semana actual.
    </div>""", unsafe_allow_html=True)

    view5=st.radio("Ver",["Global","Por cadena"],horizontal=True)

    if view5=="Global":
        t5=weekly_totals(mg_filt,common,sfx_o,sfx_n)
        fig5=line_weekly(t5,wk_old,wk_new,"Tendencia global: FCST Base vs Revisado")
        if current_lbl in common:
            fig5.add_vline(x=current_lbl,line_dash="dash",line_color="#d29922",
                           opacity=0.7,annotation_text=f"Hoy {current_lbl}",
                           annotation_position="top left")
        st.plotly_chart(ptpl(fig5),use_container_width=True)
    else:
        cads5=st.multiselect("Cadenas",all_cadenas,
                             default=all_cadenas[:3] if len(all_cadenas)>=3 else all_cadenas,
                             key="tab5_cad")
        fig5m=go.Figure()
        for cad in cads5:
            mc=mg[mg["Cadena"]==cad]
            vals=[mc[f"{w}{sfx_n}"].sum() if f"{w}{sfx_n}" in mc.columns else 0 for w in common]
            fig5m.add_scatter(x=common,y=vals,mode="lines+markers",name=cad,
                              line=dict(color=color_cadena(cad),width=2.5),marker=dict(size=5))
        if current_lbl in common:
            fig5m.add_vline(x=current_lbl,line_dash="dash",line_color="#d29922",opacity=0.7)
        fig5m.update_layout(title=f"Tendencia por cadena — W{wk_new:02d}",
                            height=380,xaxis_title="Semana",yaxis_title="Cajas")
        st.plotly_chart(ptpl(fig5m),use_container_width=True)

    st.markdown('<div class="sec-title">🍎 Tendencia por Especie</div>',unsafe_allow_html=True)
    especies_top=mg_filt["Especie"].value_counts().head(6).index.tolist()
    cols5=st.columns(min(3,len(especies_top))) if especies_top else []
    for i,esp in enumerate(especies_top):
        with cols5[i%len(cols5)]:
            me=mg_filt[mg_filt["Especie"]==esp]
            vo5=[me[f"{w}{sfx_o}"].sum() if f"{w}{sfx_o}" in me.columns else 0 for w in common]
            vn5=[me[f"{w}{sfx_n}"].sum() if f"{w}{sfx_n}" in me.columns else 0 for w in common]
            fe=go.Figure()
            fe.add_scatter(x=common,y=vo5,mode="lines",name="Base",
                           line=dict(color="#8b949e",dash="dot",width=1.5))
            fe.add_scatter(x=common,y=vn5,mode="lines+markers",name="Nuevo",
                           line=dict(color="#58a6ff",width=2),marker=dict(size=3))
            fe.update_layout(title=esp,height=220,showlegend=False,
                             margin=dict(l=30,r=10,t=35,b=30),
                             xaxis=dict(tickangle=45,tickfont=dict(size=8)))
            st.plotly_chart(ptpl(fe),use_container_width=True)

    st.markdown('<div class="sec-title">📊 Ranking variación Especie × Cadena</div>',
                unsafe_allow_html=True)
    rank_rows=[]
    for cad in all_cadenas:
        for esp in especies_top:
            sub_r=mg[(mg["Cadena"]==cad)&(mg["Especie"]==esp)]
            if sub_r.empty: continue
            vo_r=sum(sub_r[f"{w}{sfx_o}"].sum() for w in fwd_weeks if f"{w}{sfx_o}" in sub_r.columns)
            vn_r=sum(sub_r[f"{w}{sfx_n}"].sum() for w in fwd_weeks if f"{w}{sfx_n}" in sub_r.columns)
            if vo_r==0 and vn_r==0: continue
            dr=vn_r-vo_r; pr=(dr/vo_r*100) if vo_r>0 else 0
            rank_rows.append({"Cadena":cad,"Especie":esp,
                              f"Vol Base (W{wk_new}+)":int(vo_r),
                              f"Vol Nuevo (W{wk_new}+)":int(vn_r),
                              "Δ Cajas":int(dr),"Δ %":round(pr,1)})
    if rank_rows:
        df_rank=pd.DataFrame(rank_rows).sort_values("Δ %",ascending=False)
        def color_rank(val):
            if isinstance(val,(int,float)):
                if val>=threshold:  return "background-color:#0a3d0a; color:#3fb950"
                elif val<=-threshold: return "background-color:#3d0a0a; color:#f85149"
            return ""
        st.dataframe(df_rank.style.map(color_rank,subset=["Δ %"])
                     .format({"Δ %":"{:+.1f}%","Δ Cajas":"{:+,.0f}"}),
                     use_container_width=True,height=300)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='color:#8b949e;font-size:.8rem;text-align:center'>"
    f"VIDIMPORT · Dashboard FCST · "
    f"W{wk_old:02d} → W{wk_new:02d} · "
    f"Umbral {threshold}% · {len(mg)} SKUs · {len(common)} semanas"
    f"</p>", unsafe_allow_html=True)
