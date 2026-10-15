import streamlit as st
import pandas as pd
import os

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

    # Convert Family and Type columns to uppercase for consistent display
    df["Clean_Family"] = df[fam_col].astype(str).str.upper()
    df["Clean_Type"] = df[type_col].astype(str).str.upper()

    main_col, side_col = st.columns([2, 1])

    with main_col:
        st.subheader("🗂️ Hierarchical Door Explorer")
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

                        parameters = ["BA", "CA", "YM", "MDA", "ER"]
                        cols = st.columns(len(parameters))

                        for i, param in enumerate(parameters):
                            checked = is_checked(row_data.get(param, ""))
                            if checked:
                                cols[i].markdown(f"**{param}**: ✅")
                            else:
                                cols[i].markdown(f"**{param}**: ❌")

                        with st.expander("🔍 View Raw Row Data from TSV", expanded=True):
                            st.write(row_data.to_dict())

    with side_col:
        st.subheader("📍 Quick Availability")
        filter_mode = st.radio("Group By:", ["Floor (NIVEL)", "Plot (FT RAL)"])

        if filter_mode == "Floor (NIVEL)" and nivel_col:
            levels = sorted([str(x) for x in df[nivel_col].dropna().unique() if str(x).strip()])
            selected_level = st.selectbox("Select Floor:", levels)
            df_filtered = df[df[nivel_col].astype(str) == selected_level]
            st.write(f"**Doors on {selected_level} ({len(df_filtered)}):**")
            
            for _, r in df_filtered.iterrows():
                st.text(f"• {r.get(mark_col, 'N/A')} ({r.get(type_col, 'N/A')})")

        elif filter_mode == "Plot (FT RAL)" and plot_col:
            all_raw_plots = df[plot_col].dropna().astype(str)
            individual_plots = set()
            for p_str in all_raw_plots:
                for token in p_str.replace(";", ",").split(","):
                    clean_token = token.strip()
                    if clean_token:
                        individual_plots.add(clean_token)
            
            plots = sorted(list(individual_plots))
            selected_plot = st.selectbox("Select Plot:", plots)
            
            df_filtered = df[df[plot_col].astype(str).str.contains(selected_plot, case=False, na=False)]
            st.write(f"**Doors in {selected_plot} ({len(df_filtered)}):**")
            
            for _, r in df_filtered.iterrows():
                st.text(f"• {r.get(mark_col, 'N/A')} ({r.get(type_col, 'N/A')})")
