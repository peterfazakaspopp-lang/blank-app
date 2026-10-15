import streamlit as st
import pandas as pd
import os

st.title("🗂️ Interactive Door Schedule Explorer")

@st.cache_data
def load_data():
    file_path = "PLOT_1.xls"
    if os.path.exists(file_path):
        return pd.read_csv(file_path, sep="\t", encoding="latin-1")
    else:
        st.error(f"File not found: {file_path}. Please upload it to your repository.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Column names based on your table headers
    fam_col = "AMPLASARE/ TIP USA/ NR CANATURI - REPEZENTARE CONFORM DESEN"
    type_col = "INDICATIV USA" # Adjust if your type name/mark has a distinct column
    
    # 1. Level 1: Select Door Family
    families = sorted(df[fam_col].dropna().astype(str).unique())
    selected_family = st.selectbox("Select Door Family", families)

    # Filter dataframe strictly for the selected family
    df_fam = df[df[fam_col].astype(str) == selected_family]

    # 2. Level 2: Select Types / Type Marks belonging ONLY to that Family
    types_in_fam = sorted(df_fam[type_col].dropna().astype(str).unique())
    selected_type = st.selectbox("Select Type / Type Mark", types_in_fam)

    # Filter dataframe strictly for the selected family + type
    df_type = df_fam[df_fam[type_col].astype(str) == selected_type]

    # 3. Level 3: Select Specific Door Mark (Instance)
    door_marks = sorted(df_type[type_col].dropna().astype(str).unique())
    selected_door = st.selectbox("Select Door Mark", door_marks)

    # Retrieve the exact row data for the selected configuration
    row_data = df_type[df_type[type_col].astype(str) == selected_door].iloc[0]

    st.divider()
    st.subheader(f"Parameters & Features for: {selected_door}")

    # Helper function to evaluate checkboxes safely
    def is_checked(val):
        if pd.isna(val):
            return False
        v_str = str(val).strip().lower()
        return v_str in ["✓", "yes", "da", "1", "true"] or (v_str not in ["-", "x", "✗", "n/a", ""])

    # 4. Level 4: Interactive Tickboxes for Features (BA, CA, YM, MDA, ER)
    col1, col2, col3, col4, col5 = st.columns(5)

    ba_val = col1.checkbox("BA", value=is_checked(row_data.get("BA", "")))
    ca_val = col2.checkbox("CA", value=is_checked(row_data.get("CA", "")))
    ym_val = col3.checkbox("YM", value=is_checked(row_data.get("YM", "")))
    mda_val = col4.checkbox("MDA", value=is_checked(row_data.get("MDA", "")))
    er_val = col5.checkbox("ER", value=is_checked(row_data.get("ER", "")))
