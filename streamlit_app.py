import streamlit as st
import pandas as pd
import os

st.title("🗂️ Master Interactive Door Schedule Explorer")

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

    # Convert Family and Type columns to uppercase for consistent display
    df["Clean_Family"] = df[fam_col].astype(str).str.upper()
    df["Clean_Type"] = df[type_col].astype(str).str.upper()

    families = sorted([x for x in df["Clean_Family"].dropna().unique() if x.strip() and "TOTAL" not in x and "LINKED REVIT MODEL" not in x])
    
    if families:
        selected_family = st.selectbox("Family:", families)
        df_fam = df[df["Clean_Family"] == selected_family]

        types_in_fam = sorted([x for x in df_fam["Clean_Type"].dropna().unique() if x.strip()])
        if types_in_fam:
            selected_type = st.selectbox("Type:", types_in_fam)
            df_type = df_fam[df_fam["Clean_Type"] == selected_type]

            door_marks = sorted([str(x) for x in df_type[mark_col].dropna().unique() if str(x).strip()])
            if door_marks:
                selected_door = st.selectbox("INDICATIV:", door_marks)

                matching_rows = df_type[df_type[mark_col].astype(str) == selected_door]
                if not matching_rows.empty:
                    row_data = matching_rows.iloc[0]

                    st.divider()
                    st.subheader(f"Parameters for INDICATIV: {selected_door}")

                    def is_checked(val):
                        if pd.isna(val):
                            return False
                        v_str = str(val).strip().lower()
                        return v_str in ["✓", "yes", "da", "1", "true", "x"]

                    # Display Green Ticks / Red Crosses for features (BA, CA, YM, MDA, ER)
                    parameters = ["BA", "CA", "YM", "MDA", "ER"]
                    cols = st.columns(len(parameters))

                    for i, param in enumerate(parameters):
                        checked = is_checked(row_data.get(param, ""))
                        if checked:
                            cols[i].markdown(f"**{param}**: ✅")
                        else:
                            cols[i].markdown(f"**{param}**: ❌")

                    # Raw Data Debug Expander expanded by default
                    with st.expander("🔍 View Raw Row Data from TSV", expanded=True):
                        st.write(row_data.to_dict())
