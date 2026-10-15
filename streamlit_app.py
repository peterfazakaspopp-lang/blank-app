import streamlit as st
import pandas as pd
import os

st.title("🗂️ Master Interactive Door Schedule Explorer")

@st.cache_data
def load_data():
    file_path = "PLOT_MASTER.tsv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, sep="\t", encoding="latin-1")
        if "Family" in df.columns:
            df = df[~df["Family"].astype(str).str.contains("Grand total|Total|Family", case=False, na=False)]
        return df
    else:
        st.error(f"File not found: {file_path}. Please upload PLOT_MASTER.tsv to your GitHub repository.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    fam_col = "Family" if "Family" in df.columns else df.columns[0]
    type_col = "TIP" if "TIP" in df.columns else df.columns[1]
    mark_col = "INDICATIV USA" if "INDICATIV USA" in df.columns else df.columns[3]

    families = sorted([str(x) for x in df[fam_col].dropna().unique() if str(x).strip() and "total" not in str(x).lower()])
    
    if families:
        selected_family = st.selectbox("Family:", families)
        df_fam = df[df[fam_col].astype(str) == selected_family]

        types_in_fam = sorted([str(x) for x in df_fam[type_col].dropna().unique() if str(x).strip()])
        if types_in_fam:
            selected_type = st.selectbox("Type:", types_in_fam)
            df_type = df_fam[df_fam[type_col].astype(str) == selected_type]

            door_marks = sorted([str(x) for x in df_type[mark_col].dropna().unique() if str(x).strip()])
            if door_marks:
                selected_door = st.selectbox("Door Mark:", door_marks)

                matching_rows = df_type[df_type[mark_col].astype(str) == selected_door]
                if not matching_rows.empty:
                    row_data = matching_rows.iloc[0]

                    st.divider()
                    st.subheader(f"Parameters for Door Mark: {selected_door}")

                    def is_checked(val):
                        if pd.isna(val):
                            return False
                        v_str = str(val).strip().lower()
                        # Catch any checkmark, 1, true, yes, or non-empty character flags
                        return v_str in ["✓", "yes", "da", "1", "true", "x"] or len(v_str) > 0

                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.checkbox("BA", value=is_checked(row_data.get("BA", "")), key=f"ba_{selected_door}")
                    col2.checkbox("CA", value=is_checked(row_data.get("CA", "")), key=f"ca_{selected_door}")
                    col3.checkbox("YM", value=is_checked(row_data.get("YM", "")), key=f"ym_{selected_door}")
                    col4.checkbox("MDA", value=is_checked(row_data.get("MDA", "")), key=f"mda_{selected_door}")
                    col5.checkbox("ER", value=is_checked(row_data.get("ER", "")), key=f"er_{selected_door}")

                    # --- DEBUG SECTION ---
                    with st.expander("🔍 View Raw Row Data from TSV"):
                        st.write(row_data.to_dict())
