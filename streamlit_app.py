import streamlit as st
import pandas as pd
import os

st.title("🗂️ Master Interactive Door Schedule Explorer")

@st.cache_data
def load_data():
    file_path = "PLOT_MASTER.tsv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, sep="\t", encoding="latin-1")
        # Clean out any accidental header rows duplicated inside data
        if "Family" in df.columns:
            df = df[df["Family"] != "Family"]
        return df
    else:
        st.error(f"File not found: {file_path}. Please upload PLOT_MASTER.tsv to your GitHub repository.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Column mappings matching the master TSV export
    fam_col = "Family" if "Family" in df.columns else df.columns[0]
    type_col = "AMPLASARE/ TIP USA/ NR CANATURI" if "AMPLASARE/ TIP USA/ NR CANATURI" in df.columns else df.columns[1]
    mark_col = "INDICATIV USA" if "INDICATIV USA" in df.columns else df.columns[5]

    # 1. Level 1: Select Family (filtering out blank or header strings)
    families = sorted([str(x) for x in df[fam_col].dropna().unique() if str(x).strip() and str(x) != "Family"])
    selected_family = st.selectbox("Family:", families)

    # Filter dataframe strictly for the selected family
    df_fam = df[df[fam_col].astype(str) == selected_family]

    # 2. Level 2: Select Type belonging to that family
    types_in_fam = sorted([str(x) for x in df_fam[type_col].dropna().unique() if str(x).strip()])
    selected_type = st.selectbox("Type:", types_in_fam)

    # Filter further by the selected type
    df_type = df_fam[df_fam[type_col].astype(str) == selected_type]

    # 3. Level 3: Door Mark Selection
    door_marks = sorted([str(x) for x in df_type[mark_col].dropna().unique() if str(x).strip()])
    selected_door = st.selectbox("Door Mark:", door_marks)

    # Get exact row data for the selected configuration
    matching_rows = df_type[df_type[mark_col].astype(str) == selected_door]
    row_data = matching_rows.iloc[0] if not matching_rows.empty else df_type.iloc[0]

    st.divider()
    st.subheader(f"Parameters for Door Mark: {selected_door}")

    # Helper function to evaluate checkboxes safely
    def is_checked(val):
        if pd.isna(val):
            return False
        v_str = str(val).strip().lower()
        return v_str in ["✓", "yes", "da", "1", "true", "x"]

    # 4. Level 4: Interactive Tickboxes with unique keys per door to prevent duplicate ID crashes
    col1, col2, col3, col4, col5 = st.columns(5)

    ba_val = col1.checkbox("BA", value=is_checked(row_data.get("BA", "")), key=f"ba_{selected_door}")
    ca_val = col2.checkbox("CA", value=is_checked(row_data.get("CA", "")), key=f"ca_{selected_door}")
    ym_val = col3.checkbox("YM", value=is_checked(row_data.get("YM", "")), key=f"ym_{selected_door}")
    mda_val = col4.checkbox("MDA", value=is_checked(row_data.get("MDA", "")), key=f"mda_{selected_door}")
    er_val = col5.checkbox("ER", value=is_checked(row_data.get("ER", "")), key=f"er_{selected_door}")

    # Debug expander to inspect raw row values
    with st.expander("🔍 View Raw Row Data (Debug)"):
        st.write(row_data)
