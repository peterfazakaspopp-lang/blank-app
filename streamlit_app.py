import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(layout="wide")
st.title("ASX_UM_XX_ALL")

@st.cache_data
def load_data():
    file_path = "PLOT_MASTER.tsv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, sep="\t", encoding="utf-8-sig")
        if "Family" in df.columns:
            df = df[~df["Family"].astype(str).str.contains("Grand total|Total|Family|Linked Revit Model", case=False, na=False)]
        return df
    else:
        st.error(f"File not found: {file_path}. Please upload PLOT_MASTER.tsv to your GitHub repository.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    fam_col = "Family" if "Family" in df.columns else df.columns[0]
    type_col = "TIP" if "TIP" in df.columns else df.columns[1]
    mark_col = "INDICATIV USA" if "INDICATIV USA" in df.columns else df.columns[3]
    nivel_col = "NIVEL" if "NIVEL" in df.columns else None
    plot_col = "FT RAL" if "FT RAL" in df.columns else None

    df["Clean_Family"] = df[fam_col].astype(str).str.upper()
    df["Clean_Type"] = df[type_col].astype(str).str.upper()

    if "TOTAL" in df.columns:
        df["Numeric_Total"] = pd.to_numeric(df["TOTAL"], errors="coerce").fillna(1)
    else:
        df["Numeric_Total"] = 1

    main_col, side_col = st.columns
