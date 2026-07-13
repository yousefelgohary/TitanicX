import streamlit as st
import pandas as pd


def render_explorer_tab(df: pd.DataFrame) -> None:
    """
    Data Explorer tab: full filtered DataFrame with column selector + CSV download.
    """
    # ── Header ─────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <h3 style="color:#E2E8F0; font-weight:800; margin-bottom:0.3rem; font-size:1.3rem;">
            📥 Cleaned Data Explorer
        </h3>
        <p style="color:rgba(255,255,255,0.42); font-size:0.88rem; margin-bottom:1.2rem;">
            The table reflects all pipeline steps (cleaning + feature engineering)
            filtered by your sidebar selections. Download the cleaned CSV below.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # ── Quick Stats ────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Rows", f"{len(df):,}")
    with c2:
        st.metric("Columns", len(df.columns))
    with c3:
        st.metric("Missing Values", f"{df.isnull().sum().sum():,}")
    with c4:
        dtypes = df.dtypes.value_counts()
        numeric_count = int(dtypes.get("float64", 0)) + int(dtypes.get("int64", 0))
        st.metric("Numeric Columns", numeric_count)

    st.markdown('<div class="fancy-divider" style="margin:1rem 0;"></div>', unsafe_allow_html=True)

    # ── Column Selector ────────────────────────────────────────────────────────
    all_cols = df.columns.tolist()
    selected = st.multiselect(
        "🔍 Select columns to display",
        options=all_cols,
        default=all_cols,
        key="explorer_multiselect",
    )
    display_df = df[selected] if selected else df

    # ── DataFrame ──────────────────────────────────────────────────────────────
    st.dataframe(
        display_df,
        use_container_width=True,
        height=430,
    )

    # ── Describe Panel ─────────────────────────────────────────────────────────
    with st.expander("📊 Descriptive Statistics of Displayed Columns"):
        numeric_cols = display_df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            st.dataframe(
                display_df[numeric_cols].describe().round(3),
                use_container_width=True,
            )
        else:
            st.info("No numeric columns in the current selection.")

    # ── Download ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    csv_bytes = df.to_csv(index=False).encode("utf-8")

    col_dl, col_info = st.columns([2, 5])
    with col_dl:
        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=csv_bytes,
            file_name="titanic_cleaned.csv",
            mime="text/csv",
        )
    with col_info:
        st.markdown(
            f"<p style='color:rgba(255,255,255,0.35); font-size:0.8rem; margin-top:0.6rem;'>"
            f"Full cleaned dataset · {len(df):,} rows · {len(df.columns)} columns · "
            f"Features: has_cabin, AgeGroup, Title included</p>",
            unsafe_allow_html=True,
        )
