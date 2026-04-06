"""
csv_analyzer.py
Full Streamlit UI component for the AECIP CSV Analysis page.
"""

import io
import sys
import os
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from dashboard.utils.csv_processor import process, validate

# ── constants ──────────────────────────────────────────────────────────────────

AECIP_FIELDS = [
    "— (not mapped)",
    "customer_id",
    "recency_days",
    "purchase_frequency",
    "monetary_value",
    "age",
]

ANALYSES = ["Customer Loss Prediction", "CLV Prediction", "Customer Segmentation"]

# ── CSS injection ─────────────────────────────────────────────────────────────

def _inject_css():
    st.markdown("""
    <style>
    /* ── Upload drop zone ─────────────────────── */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 2px dashed #334155;
        border-radius: 16px;
        padding: 8px 16px;
        transition: border-color 0.3s;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #6366F1;
    }

    /* ── Result KPI cards ─────────────────────── */
    .result-kpi-card {
        background: linear-gradient(135deg, #1E293B 0%, #162032 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 24px rgba(0,0,0,0.25);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .result-kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(99,102,241,0.18);
    }
    .result-kpi-label {
        color: #94A3B8;
        font-size: 12px;
        font-weight: 500;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .result-kpi-value {
        color: #F1F5F9;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* ── Section headers ──────────────────────── */
    .section-badge {
        display: inline-block;
        background: linear-gradient(90deg, #6366F1, #8B5CF6);
        color: white;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 30px;
        margin-bottom: 10px;
    }

    /* ── Algorithm chips ──────────────────────── */
    .algo-chip {
        display: inline-block;
        background: #1E293B;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 6px 14px;
        margin: 4px;
        font-size: 13px;
        color: #CBD5E1;
    }

    /* ── Warning / info banners ───────────────── */
    .warn-banner {
        background: #422006;
        border-left: 4px solid #F59E0B;
        border-radius: 6px;
        padding: 12px 16px;
        color: #FDE68A;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .info-banner {
        background: #0C1A3A;
        border-left: 4px solid #6366F1;
        border-radius: 6px;
        padding: 12px 16px;
        color: #BAC8FF;
        font-size: 14px;
        margin-bottom: 8px;
    }

    /* ── Run button ───────────────────────────── */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.55rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        letter-spacing: 0.3px !important;
        box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
        transition: all 0.25s !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        box-shadow: 0 6px 28px rgba(99,102,241,0.6) !important;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)


# ── helpers ───────────────────────────────────────────────────────────────────

def _section(label: str):
    st.markdown(f'<div class="section-badge">{label}</div>', unsafe_allow_html=True)


def _kpi_card(label: str, value: str):
    st.markdown(f"""
    <div class="result-kpi-card">
        <div class="result-kpi-label">{label}</div>
        <div class="result-kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def _plotly_defaults(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1", family="Inter"),
        margin=dict(t=30, b=10, l=10, r=10),
    )
    fig.update_xaxes(showgrid=False, color="#64748B")
    fig.update_yaxes(showgrid=True, gridcolor="#1E293B", color="#64748B")
    return fig


# ── step 1: upload ────────────────────────────────────────────────────────────

def _step_upload() -> pd.DataFrame | None:
    _section("Step 1 · Upload Dataset")
    st.markdown("Upload any customer `.csv` file.")

    file = st.file_uploader(
        "Drag & drop or browse",
        type=["csv"],
        key="csv_upload",
        help="Accepts any UTF-8 encoded CSV file. Max 200 MB.",
    )

    if file is None:
        return None

    try:
        df = pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        file.seek(0)
        df = pd.read_csv(file, encoding="latin-1")

    if df.empty:
        st.error("The uploaded CSV is empty. Please upload a file with at least one data row.")
        return None

    # Dataset summary strip
    n_rows, n_cols = df.shape
    n_null = int(df.isnull().sum().sum())
    num_cols = df.select_dtypes(include="number").shape[1]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{n_rows:,}")
    c2.metric("Columns", n_cols)
    c3.metric("Numeric cols", num_cols)
    c4.metric("Missing values", n_null)

    with st.expander("📋 Preview first 8 rows", expanded=True):
        st.dataframe(df.head(8), use_container_width=True)

    return df


# ── step 2: column mapping ────────────────────────────────────────────────────

def _step_map_columns(df: pd.DataFrame) -> dict:
    _section("Step 2 · Map Your Columns")

    user_cols = ["— (not mapped)"] + list(df.columns)

    # Try to auto-detect obvious column names
    col_lower = {c.lower().replace(" ", "_"): c for c in df.columns}

    def _guess(candidates: list[str]) -> str:
        for c in candidates:
            if c in col_lower:
                return col_lower[c]
        return "— (not mapped)"

    auto = {
        "customer_id":        _guess(["customer_id", "customerid", "id", "cust_id", "customer"]),
        "recency_days":       _guess(["recency_days", "recency", "days_since_purchase", "days_inactive", "last_seen"]),
        "purchase_frequency": _guess(["purchase_frequency", "frequency", "num_purchases", "order_count", "purchases"]),
        "monetary_value":     _guess(["monetary_value", "monetary", "total_spend", "revenue", "amount"]),
        "age":                _guess(["age", "customer_age"]),
    }

    cols = st.columns(3)
    mapping = {}
    field_defs = [
        ("customer_id",        "Customer ID",        "Unique identifier per customer"),
        ("recency_days",       "Recency (days)",     "Days since last purchase / activity"),
        ("purchase_frequency", "Purchase Frequency", "Number of purchases in period"),
        ("monetary_value",     "Monetary Value",     "Total spend / revenue per customer"),
        ("age",                "Age",                "Customer age (optional)"),
    ]

    for i, (field, label, help_txt) in enumerate(field_defs):
        default_idx = user_cols.index(auto[field]) if auto[field] in user_cols else 0
        selected = cols[i % 3].selectbox(
            label,
            options=user_cols,
            index=default_idx,
            key=f"map_{field}",
            help=help_txt,
        )
        mapping[field] = None if selected == "— (not mapped)" else selected

    return mapping


# ── step 3: run button ────────────────────────────────────────────────────────

def _step_run(df: pd.DataFrame, column_map: dict, analyses: list) -> dict | None:
    _section("Step 3 · Run Analysis")

    run = st.button("🚀  Run Analysis", type="primary", disabled=not analyses)

    if not run:
        return None

    return _run_pipeline_with_progress(df, column_map, analyses)


# ── animated pipeline processing screen ───────────────────────────────────────

def _run_pipeline_with_progress(df: pd.DataFrame, column_map: dict, analyses: list) -> dict:
    from dashboard.utils.csv_processor import (
        _extract_mapped, _run_churn, _run_clv, _run_segmentation,
        REQUIRED_FOR_CHURN, REQUIRED_FOR_CLV, REQUIRED_FOR_SEG
    )

    # ── CSS for the processing screen ─────────────────────────────────────────
    st.markdown("""
    <style>
    .pipeline-outer {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 48px 24px 32px;
    }
    .pipeline-title {
        font-size: 26px;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 6px;
        text-align: center;
        letter-spacing: -0.3px;
    }
    .pipeline-sub {
        font-size: 13px;
        color: #64748B;
        margin-bottom: 40px;
        text-align: center;
    }
    .stage-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
        gap: 14px;
        width: 100%;
        max-width: 960px;
        margin-bottom: 28px;
    }
    .stage-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px 16px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        transition: all 0.35s ease;
    }
    .stage-card.s-active {
        background: linear-gradient(135deg, #1e1b4b 0%, #1E293B 100%);
        border-color: #6366F1;
        box-shadow: 0 0 24px rgba(99,102,241,0.30);
    }
    .stage-card.s-done {
        background: linear-gradient(135deg, #052e16 0%, #1E293B 100%);
        border-color: #22C55E;
        box-shadow: 0 0 12px rgba(34,197,94,0.15);
    }
    .stage-icon { font-size: 22px; min-width: 30px; line-height: 1; }
    .stage-name {
        font-size: 13px;
        font-weight: 600;
        color: #F1F5F9;
        margin-bottom: 3px;
    }
    .stage-desc { font-size: 11px; color: #64748B; line-height: 1.4; }
    .stage-badge {
        display: inline-block;
        font-size: 10px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 20px;
        margin-top: 7px;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }
    .badge-pending { background:#1E293B; color:#475569; border:1px solid #475569; }
    .badge-active  { background:#312e81; color:#A5B4FC; border:1px solid #6366F1; }
    .badge-done    { background:#052e16; color:#4ADE80; border:1px solid #22C55E; }
    </style>
    """, unsafe_allow_html=True)

    # ── define dynamic stages ─────────────────────────────────────────────────
    stages = [
        ("📥", "Ingesting Data",         "Reading & parsing your CSV file"),
        ("🔍", "Validating Columns",     "Mapping to AECIP standard fields"),
        ("🤖", "Initialising ML Engine", "Loading models & feature pipeline"),
    ]
    if "Customer Loss Prediction" in analyses:
        stages.append(("🔴", "Customer Loss Prediction", "Scoring customer loss probability per customer"))
    if "CLV Prediction" in analyses:
        stages.append(("💰", "CLV Prediction",      "Computing lifetime value per customer"))
    if "Customer Segmentation" in analyses:
        stages.append(("🎯", "Segmenting Customers", "K-Means behavioural clustering"))
    stages.append(("⚙️", "Building Report",    "Aggregating insights & KPIs"))
    stages.append(("✅", "Analysis Complete",   "Dashboard is ready"))
    n = len(stages)

    # ── HTML renderer ─────────────────────────────────────────────────────────
    def _render(active_idx: int) -> str:
        cards = ""
        for i, (icon, name, desc) in enumerate(stages):
            if i < active_idx:
                cls, badge_cls, badge_label = "s-done",    "badge-done",    "✓ Done"
            elif i == active_idx:
                cls, badge_cls, badge_label = "s-active",  "badge-active",  "⏳ Processing"
            else:
                cls, badge_cls, badge_label = "",           "badge-pending", "Pending"
            cards += f"""
            <div class="stage-card {cls}">
                <div class="stage-icon">{icon}</div>
                <div>
                    <div class="stage-name">{name}</div>
                    <div class="stage-desc">{desc}</div>
                    <span class="stage-badge {badge_cls}">{badge_label}</span>
                </div>
            </div>"""
        return f"""
        <div class="pipeline-outer">
            <div class="pipeline-title">⚡ AECIP Intelligence Engine</div>
            <div class="pipeline-sub">Processing {len(df):,} customers through the full ML pipeline&hellip;</div>
            <div class="stage-grid">{cards}</div>
        </div>"""

    # ── placeholders ─────────────────────────────────────────────────────────
    ui_ph   = st.empty()
    prog_ph = st.progress(0)
    msg_ph  = st.empty()

    def _update(idx: int, msg: str, color: str = "#818CF8"):
        ui_ph.markdown(_render(idx), unsafe_allow_html=True)
        prog_ph.progress(min(int(idx / (n - 1) * 100), 100))
        msg_ph.markdown(
            f'<p style="text-align:center;color:{color};font-size:13px;margin-top:4px;">{msg}</p>',
            unsafe_allow_html=True
        )

    # ── initialise results container ──────────────────────────────────────────
    results = {
        "warnings": [],
        "summary":  {},
        "churn":    None,
        "clv":      None,
        "segments": None,
        "combined": None,
    }

    # ══ STAGE 0 — Ingest ═════════════════════════════════════════════════════
    _update(0, "📥 Reading and parsing your file...")
    time.sleep(0.7)

    # ══ STAGE 1 — Validate & Map ══════════════════════════════════════════════
    _update(1, "🔍 Validating and mapping columns...")
    results["warnings"] = validate(df, column_map, analyses)
    mapped = _extract_mapped(df.copy(), column_map)
    if "customer_id" not in mapped.columns:
        mapped["customer_id"] = range(1, len(mapped) + 1)
    results["combined"] = mapped.copy()
    time.sleep(0.5)

    # ══ STAGE 2 — Init ML Engine ══════════════════════════════════════════════
    _update(2, "🤖 Initialising ML models and feature pipeline...")
    time.sleep(0.9)

    current = 3  # dynamic stage pointer

    # ══ STAGE — Churn Prediction ═══════════════════════════════════════════════
    if "Customer Loss Prediction" in analyses:
        _update(current, "🔴 Running customer loss prediction model...")
        if all(c in mapped.columns for c in REQUIRED_FOR_CHURN):
            churn_df = _run_churn(mapped)
            results["churn"] = churn_df
            results["combined"] = results["combined"].merge(
                churn_df.drop(columns=["_model_used"], errors="ignore"),
                on="customer_id", how="left"
            )
            pct_high = (churn_df["churn_risk"] == "High 🔴").mean() * 100
            results["summary"]["At-Risk Customers"] = f"{pct_high:.1f}%"
        current += 1
        time.sleep(0.5)

    # ══ STAGE — CLV Prediction ════════════════════════════════════════════════
    if "CLV Prediction" in analyses:
        _update(current, "💰 Computing customer lifetime value...")
        if all(c in mapped.columns for c in REQUIRED_FOR_CLV):
            clv_df = _run_clv(mapped)
            results["clv"] = clv_df
            results["combined"] = results["combined"].merge(
                clv_df.drop(columns=["_model_used"], errors="ignore"),
                on="customer_id", how="left"
            )
            avg_clv = clv_df["predicted_clv"].mean()
            results["summary"]["Avg Predicted CLV"] = f"₹{avg_clv:,.0f}"
        current += 1
        time.sleep(0.5)

    # ══ STAGE — Customer Segmentation ════════════════════════════════════════
    if "Customer Segmentation" in analyses:
        _update(current, "🎯 Running K-Means customer segmentation...")
        if all(c in mapped.columns for c in REQUIRED_FOR_SEG):
            seg_df = _run_segmentation(mapped)
            results["segments"] = seg_df
            results["combined"] = results["combined"].merge(
                seg_df[["customer_id", "segment_name"]],
                on="customer_id", how="left"
            )
            top_seg = seg_df["segment_name"].value_counts().idxmax() if len(seg_df) else "—"
            results["summary"]["Dominant Segment"] = top_seg
        current += 1
        time.sleep(0.6)

    # ══ STAGE — Build Report ══════════════════════════════════════════════════
    _update(current, "⚙️ Aggregating intelligence report and KPIs...")
    results["summary"]["Total Customers Processed"] = f"{len(df):,}"
    time.sleep(0.7)
    current += 1

    # ══ STAGE — Complete ══════════════════════════════════════════════════════
    ui_ph.markdown(_render(n), unsafe_allow_html=True)  # all cards green
    prog_ph.progress(100)
    msg_ph.markdown(
        '<p style="text-align:center;color:#22C55E;font-size:14px;font-weight:600;margin-top:4px;">'
        '✅ Analysis complete! Loading your dashboard...</p>',
        unsafe_allow_html=True
    )
    time.sleep(1.2)

    # Clear the processing UI
    ui_ph.empty()
    prog_ph.empty()
    msg_ph.empty()

    return results


# ── step 5: results ───────────────────────────────────────────────────────────

def _step_results(results: dict):
    _section("Results")

    # Runtime warnings
    for w in results.get("warnings", []):
        st.markdown(f'<div class="warn-banner">{w}</div>', unsafe_allow_html=True)

    # ── KPI summary strip ──────────────────────────────────────────────────
    summary = results.get("summary", {})
    if summary:
        kpi_cols = st.columns(len(summary))
        for col, (k, v) in zip(kpi_cols, summary.items()):
            with col:
                _kpi_card(k, str(v))
        st.markdown("<br>", unsafe_allow_html=True)

    tabs = []
    if results.get("churn") is not None:
        tabs.append("🔴 Customer Loss Prediction")
    if results.get("clv") is not None:
        tabs.append("💰 CLV Prediction")
    if results.get("segments") is not None:
        tabs.append("🎯 Segmentation")

    if not tabs:
        st.warning("No results to display. Make sure required columns are mapped.")
        return

    rendered_tabs = st.tabs(tabs)
    tab_idx = 0

    # ── CHURN TAB ──────────────────────────────────────────────────────────
    if results.get("churn") is not None:
        with rendered_tabs[tab_idx]:
            churn = results["churn"]

            # Risk breakdown donut
            if "churn_risk" in churn.columns:
                risk_counts = churn["churn_risk"].value_counts().reset_index()
                risk_counts.columns = ["Loss Probability Level", "Count"]
                fig_donut = px.pie(
                    risk_counts, names="Loss Probability Level", values="Count",
                    hole=0.55,
                    color="Loss Probability Level",
                    color_discrete_map={
                        "Low 🟢":    "#22C55E",
                        "Medium 🟡": "#F59E0B",
                        "High 🔴":   "#EF4444",
                    },
                    title="Customer Loss Probability Distribution",
                )
                fig_donut = _plotly_defaults(fig_donut)
                st.plotly_chart(fig_donut, use_container_width=True)

            # Probability histogram
            if "churn_probability" in churn.columns:
                fig_hist = px.histogram(
                    churn, x="churn_probability",
                    nbins=20,
                    color_discrete_sequence=["#6366F1"],
                    title="Customer Loss Probability Distribution",
                    labels={"churn_probability": "Customer Loss Probability (%)"},
                )
                fig_hist = _plotly_defaults(fig_hist)
                st.plotly_chart(fig_hist, use_container_width=True)

            st.dataframe(churn.drop(columns=["_model_used"], errors="ignore"), use_container_width=True)

            if "_model_used" in churn.columns:
                st.caption(f"ℹ️ Engine: {churn['_model_used'].iloc[0]}")
        tab_idx += 1

    # ── CLV TAB ────────────────────────────────────────────────────────────
    if results.get("clv") is not None:
        with rendered_tabs[tab_idx]:
            clv = results["clv"]

            if "predicted_clv" in clv.columns:
                fig_clv = px.histogram(
                    clv, x="predicted_clv",
                    nbins=25,
                    color_discrete_sequence=["#10B981"],
                    title="Predicted CLV Distribution",
                    labels={"predicted_clv": "Predicted CLV (₹)"},
                )
                fig_clv = _plotly_defaults(fig_clv)
                st.plotly_chart(fig_clv, use_container_width=True)

                # Top 10 high-value customers
                top10 = clv.sort_values("predicted_clv", ascending=False).head(10)
                fig_bar = px.bar(
                    top10,
                    x="customer_id" if "customer_id" in top10.columns else top10.index,
                    y="predicted_clv",
                    color_discrete_sequence=["#6366F1"],
                    title="Top 10 Highest CLV Customers",
                    labels={"predicted_clv": "CLV (₹)", "customer_id": "Customer ID"},
                )
                fig_bar = _plotly_defaults(fig_bar)
                st.plotly_chart(fig_bar, use_container_width=True)

            st.dataframe(clv.drop(columns=["_model_used"], errors="ignore"), use_container_width=True)

            if "_model_used" in clv.columns:
                st.caption(f"ℹ️ Engine: {clv['_model_used'].iloc[0]}")
        tab_idx += 1

    # ── SEGMENTATION TAB ───────────────────────────────────────────────────
    if results.get("segments") is not None:
        with rendered_tabs[tab_idx]:
            seg = results["segments"]

            if "segment_name" in seg.columns:
                seg_counts = seg["segment_name"].value_counts().reset_index()
                seg_counts.columns = ["Segment", "Count"]

                color_map = {
                    "High Value ⭐": "#6366F1",
                    "Regular 🔁":    "#22C55E",
                    "Inactive 😴":   "#94A3B8",
                    "At Risk ⚠️":    "#F59E0B",
                }
                fig_seg = px.bar(
                    seg_counts, x="Segment", y="Count",
                    color="Segment",
                    color_discrete_map=color_map,
                    title="Customer Segment Breakdown",
                )
                fig_seg = _plotly_defaults(fig_seg)
                st.plotly_chart(fig_seg, use_container_width=True)

                # Silhouette badge
                if "silhouette" in seg.columns:
                    sil = seg["silhouette"].iloc[0]
                    st.metric("Silhouette Score (quality)", f"{sil:.4f}",
                              help="Closer to 1.0 = better-defined clusters. Above 0.4 is good.")

            st.dataframe(seg[["customer_id", "segment_name"] if "customer_id" in seg.columns
                             else ["segment_name"]], use_container_width=True)


# ── step 6: download ──────────────────────────────────────────────────────────

def _step_download(results: dict):
    combined = results.get("combined")
    if combined is None or combined.empty:
        return

    _section("Download Results")
    csv_bytes = combined.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download Results as CSV",
        data=csv_bytes,
        file_name="aecip_analysis_results.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ── main entry point ──────────────────────────────────────────────────────────

def render_csv_analyzer():
    _inject_css()

    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h2 style="color: #F1F5F9; font-weight: 700; font-size: 26px; margin:0;">
            📊 Initialize Intelligence Engine
        </h2>
        <p style="color: #64748B; font-size: 14px; margin-top: 6px;">
            Upload your customer dataset.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── step 1: upload
    df = _step_upload()
    if df is None:
        return

    st.markdown("---")

    # ── step 2: column mapping
    column_map = _step_map_columns(df)
    st.markdown("---")

    # ── step 3: run
    analyses = ANALYSES
    results = _step_run(df, column_map, analyses)
    if results is None:
        return

    # Transition to Output Dashboard
    st.session_state.results = results
    st.session_state.data_processed = True
    st.session_state.page = "overview"
    st.rerun()
