import streamlit as st
import pandas as pd


def render_kpi_row(filtered_df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    """
    Render a 4-column KPI metrics row.
    All deltas are computed against the full (unfiltered) dataset.
    """
    n_total     = len(filtered_df)
    n_full      = len(full_df)
    n_survivors = int(filtered_df["Survived"].sum()) if n_total > 0 else 0
    surv_rate   = filtered_df["Survived"].mean() * 100 if n_total > 0 else 0.0
    global_rate = full_df["Survived"].mean() * 100

    survivors_f = filtered_df[filtered_df["Survived"] == 1]
    avg_fare_sv = survivors_f["Fare"].mean() if len(survivors_f) > 0 else 0.0
    avg_fare_gl = full_df[full_df["Survived"] == 1]["Fare"].mean()

    delta_rate = surv_rate - global_rate
    delta_fare = avg_fare_sv - avg_fare_gl

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🧑‍✈️ Passengers (Filtered)",
            value=f"{n_total:,}",
            delta=f"{n_total - n_full:+,} vs full" if n_total != n_full else "Full dataset",
        )

    with col2:
        st.metric(
            label="✅ Survivors",
            value=f"{n_survivors:,}",
            delta=f"{surv_rate:.1f}% survival" if n_total > 0 else "—",
            delta_color="normal",
        )

    with col3:
        st.metric(
            label="📈 Survival Rate",
            value=f"{surv_rate:.1f}%",
            delta=f"{delta_rate:+.1f}% vs global {global_rate:.1f}%",
            delta_color="normal" if delta_rate >= 0 else "inverse",
        )

    with col4:
        st.metric(
            label="💰 Avg Fare (Survivors)",
            value=f"£{avg_fare_sv:.2f}",
            delta=f"{delta_fare:+.1f} vs global avg",
            delta_color="normal" if delta_fare >= 0 else "inverse",
        )
