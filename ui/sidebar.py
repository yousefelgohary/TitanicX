import streamlit as st
import pandas as pd
from processing.pipeline import apply_filters


def build_sidebar(df: pd.DataFrame) -> dict:
    """
    Render sidebar filter widgets.
    Returns {"pclass": [int, ...], "sex": [str, ...]}
    """
    with st.sidebar:

        # ── Brand Header ──────────────────────────────────────────────────────
        st.markdown(
            """
            <div style="text-align:center; padding:1.2rem 0 0.8rem;">
                <div style="font-size:2.8rem; line-height:1;">🚢</div>
                <h2 style="
                    color:#E2E8F0; font-weight:800; margin:0.4rem 0 0.1rem;
                    font-size:1.05rem; letter-spacing:0.02em;
                ">Titanic Analytics</h2>
                <p style="
                    color:rgba(255,255,255,0.35); font-size:0.72rem; margin:0;
                    letter-spacing:0.05em; text-transform:uppercase;
                ">RMS Titanic · April 1912</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

        # ── Passenger Class ───────────────────────────────────────────────────
        st.markdown('<span class="section-label">🎟 Passenger Class</span>', unsafe_allow_html=True)

        pclass_map = {1: "1st Class 💎", 2: "2nd Class 🥈", 3: "3rd Class 🥉"}
        pclass_all = sorted(df["Pclass"].unique().tolist())
        pclass_sel = []

        for p in pclass_all:
            if st.checkbox(pclass_map[p], value=True, key=f"pc_{p}"):
                pclass_sel.append(p)

        if not pclass_sel:          # guard: never allow empty selection
            pclass_sel = pclass_all

        st.markdown('<div class="fancy-divider" style="margin:0.8rem 0;"></div>', unsafe_allow_html=True)

        # ── Gender ────────────────────────────────────────────────────────────
        st.markdown('<span class="section-label">⚥ Gender</span>', unsafe_allow_html=True)

        sex_map = {"female": "👩 Female", "male": "👨 Male"}
        sex_all = sorted(df["Sex"].unique().tolist())
        sex_sel = []

        for s in sex_all:
            if st.checkbox(sex_map.get(s, s), value=True, key=f"sx_{s}"):
                sex_sel.append(s)

        if not sex_sel:
            sex_sel = sex_all

        st.markdown('<div class="fancy-divider" style="margin:0.8rem 0;"></div>', unsafe_allow_html=True)

        # ── Live Stats Panel ──────────────────────────────────────────────────
        fdf        = apply_filters(df, {"pclass": pclass_sel, "sex": sex_sel})
        n_total    = len(fdf)
        n_survived = int(fdf["Survived"].sum())
        surv_pct   = (n_survived / n_total * 100) if n_total > 0 else 0.0
        pct_of_all = (n_total / len(df) * 100)

        st.markdown(
            f"""
            <div style="
                background: rgba(124,58,237,0.1);
                border: 1px solid rgba(124,58,237,0.3);
                border-radius: 14px;
                padding: 1rem 1.1rem;
                text-align: center;
            ">
                <p style="
                    color:rgba(255,255,255,0.4); font-size:0.65rem;
                    margin:0 0 0.4rem; letter-spacing:0.1em; text-transform:uppercase;
                ">Filtered Selection</p>
                <p style="
                    color:#E2E8F0; font-size:1.55rem; font-weight:800;
                    margin:0; line-height:1;
                ">{n_total:,}</p>
                <p style="
                    color:rgba(255,255,255,0.4); font-size:0.72rem; margin:0.1rem 0 0.5rem;
                ">passengers ({pct_of_all:.0f}% of dataset)</p>
                <div style="
                    display:flex; justify-content:center; gap:1.2rem;
                    border-top:1px solid rgba(255,255,255,0.07); padding-top:0.55rem;
                ">
                    <div>
                        <p style="color:#34d399; font-size:1rem; font-weight:700; margin:0;">{n_survived:,}</p>
                        <p style="color:rgba(255,255,255,0.35); font-size:0.65rem; margin:0;">Survived</p>
                    </div>
                    <div>
                        <p style="color:#a78bfa; font-size:1rem; font-weight:700; margin:0;">{surv_pct:.1f}%</p>
                        <p style="color:rgba(255,255,255,0.35); font-size:0.65rem; margin:0;">Rate</p>
                    </div>
                    <div>
                        <p style="color:#f87171; font-size:1rem; font-weight:700; margin:0;">{n_total - n_survived:,}</p>
                        <p style="color:rgba(255,255,255,0.35); font-size:0.65rem; margin:0;">Lost</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <p style="
                color:rgba(255,255,255,0.18); font-size:0.62rem;
                text-align:center; margin-top:1.2rem;
            ">Built with Streamlit &amp; Pandas</p>
            """,
            unsafe_allow_html=True,
        )

    return {"pclass": pclass_sel, "sex": sex_sel}
