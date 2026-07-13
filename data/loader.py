import pandas as pd
import streamlit as st


@st.cache_data
def load_raw_data(path: str = "titanic.csv") -> pd.DataFrame:
    """
    Load the raw Titanic CSV from disk.
    Cached by Streamlit so it only reads from disk once per session.
    """
    return pd.read_csv(path)
