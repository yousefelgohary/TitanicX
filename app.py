"""
app.py — Titanic Survival Analytics Dashboard
=============================================
Entry point. Orchestrates the full pipeline:
  load → clean → engineer → filter → render

Run with:
    streamlit run app.py
"""

import streamlit as st

from data.loader import load_raw_data
from processing.pipeline import clean, engineer_features, apply_filters
from ui.sidebar import build_sidebar
from ui.kpi_cards import render_kpi_row
from ui.charts import render_overview_tab, render_deep_analysis_tab
from ui.insights import render_insights_tab
from ui.explorer import render_explorer_tab


def _load_css(path: str = "assets/style.css") -> None:
    try:
        with open(path, encoding="utf-8") as fh:
            st.markdown(f"<style>{fh.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # app still works without custom CSS


def main() -> None:
    # ── Page Config ─────────────────────────────────────────────────────────────
    st.set_page_config(
        page_title="Titanic Survival Analytics",
        page_icon="🚢",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "About": "**Titanic Survival Analytics Dashboard** — Built with Streamlit & Pandas",
        },
    )

    _load_css()

    # ── Data Pipeline (runs once, cached) ────────────────────────────────────────
    raw_df   = load_raw_data("titanic.csv")
    clean_df = clean(raw_df)
    full_df  = engineer_features(clean_df)

    # ── Sidebar → returns active filter state ─────────────────────────────────
    filters     = build_sidebar(full_df)
    filtered_df = apply_filters(full_df, filters)

    # ── Page Header ────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="page-header">
            <h1>🚢 Titanic Survival Analytics</h1>
            <p>Interactive EDA &amp; Feature Engineering — RMS Titanic · April 15, 1912</p>
        </div>
        <div class="fancy-divider"></div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI Row ─────────────────────────────────────────────────────────────────
    render_kpi_row(filtered_df, full_df)

    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

    # ── Tabs ────────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "🔬 Deep Analysis",
        "🤖 AI Insights",
        "📥 Data Explorer",
    ])

    with tab1:
        render_overview_tab(filtered_df)

    with tab2:
        render_deep_analysis_tab(filtered_df)

    with tab3:
        render_insights_tab(filtered_df)

    with tab4:
        render_explorer_tab(filtered_df)


if __name__ == "__main__":
    main()
