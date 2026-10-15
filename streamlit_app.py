import streamlit as st
import pandas as pd
import os

st.title("🗂️ Master Interactive Door Schedule Explorer")
@st.cache_data
def load_data():
    file_path = "PLOT_MASTER.tsv"  # Updated extension
    if os.path.exists(file_path):
        return pd.read_csv(file_path, sep="\t", encoding="latin-1")
    else:
        st.error(f"File not found: {file_path}. Please upload PLOT_MASTER.tsv to your GitHub repository.")
        return pd.DataFrame()
df = load_data()

if not df.empty:
    # Show columns for debugging if anything goes wrong
    # st.write("Columns found in file:", list(df.columns))

    # Safe dynamic column mapping (falls back to column positions if header text differs)
    fam_col = df.columns[0]  # First column: Family
    type_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]  # Second column: Type
    mark_col = "INDICATIV USA" if "INDICATIV USA" in df.columns else df.columns[2]

    # 1. Level 1: Select Family
    families = sorted(df[fam_col].dropna().astype(str).unique())
    selected_family = st.selectbox("Family:", families)

    # Filter dataframe strictly for the selected family
    df_fam = df[df[fam_col].astype(str) == selected_family]

    # 2. Level 2: Pull down to select all existing Types belonging to that family
    types_in_fam = sorted(df_fam[type_col].dropna().astype(str).unique())
    selected_type = st.selectbox("Type:", types_in_fam)

    # Filter further by the selected type
    df_type = df_fam[df_fam[type_col].astype(str) == selected_type]

    # 3. Level 3: Door Mark Selection
    door_marks = sorted(df_type[mark_col].dropna().astype(str).unique())
    selected_door = st.selectbox("Door Mark:", door_marks)
# Get exact row data for the selected configuration
    row_data = df_type[df_type[mark_col].astype(str) == selected_door].iloc[0]

    st.divider()
    st.subheader(f"Parameters for Door Mark: {selected_door}")

    # Helper function that catches checkmarks and any non-negative indicators
    def is_checked(val):
        if pd.isna(val):
            return False
        v_str = str(val).strip()
        # Returns True if it's a checkmark, '1', 'True', 'yes', 'da', or anything other than cross/dash/empty
        if v_str in ["✓", "1", "True", "true", "yes", "da"]:
            return True
        if v_str in ["✗", "x", "-", "N/A", "n/a", ""]:
            return False
        return len(v_str) > 0  # Fallback if any custom text/value exists

    # 4. Level 4: Interactive Tickboxes for Features (BA, CA, YM, MDA, ER)
    col1, col2, col3, col4, col5 = st.columns(5)

    ba_val = col1.checkbox("BA", value=is_checked(row_data.get("BA", "")))
    ca_val = col2.checkbox("CA", value=is_checked(row_data.get("CA", "")))
    ym_val = col3.checkbox("YM", value=is_checked(row_data.get("YM", "")))
    mda_val = col4.checkbox("MDA", value=is_checked(row_data.get("MDA", "")))
    er_val = col5.checkbox("ER", value=is_checked(row_data.get("ER", "")))
    
    # Optional debug expander to verify exact values coming from the file
    with st.expander("🔍 View Raw Row Data (Debug)"):
        st.write(row_data)
        
    # 4. Level 4: Interactive Tickboxes for Features (BA, CA, YM, MDA, ER)
    col1, col2, col3, col4, col5 = st.columns(5)

    ba_val = col1.checkbox("BA", value=is_checked(row_data.get("BA", "")))
    ca_val = col2.checkbox("CA", value=is_checked(row_data.get("CA", "")))
    ym_val = col3.checkbox("YM", value=is_checked(row_data.get("YM", "")))
    mda_val = col4.checkbox("MDA", value=is_checked(row_data.get("MDA", "")))
    er_val = col5.checkbox("ER", value=is_checked(row_data.get("ER", "")))
