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
        filter_mode = st.radio("Group By:", ["Floor (NIVEL)", "PLOT number"])

        if filter_mode == "Floor (NIVEL)" and nivel_col:
            individual_levels = set()
            for l_str in df[nivel_col].dropna().astype(str):
                for line in l_str.replace(";", "\n").split("\n"):
                    clean_line = re.sub(r'\s*\(\d+\)$', '', line).strip()
                    if clean_line:
                        for token in clean_line.split():
                            if token.upper() not in ["ETAJ", "SUBSOL"]:
                                individual_levels.add(token.upper())
            
            levels = sorted(list(individual_levels))
            selected_level = st.selectbox("Select Floor:", levels)
            
            # Strict token-level matching to prevent multi-counting
            def match_floor(val):
                if pd.isna(val): return False
                tokens = str(val).upper().split()
                return selected_level in tokens

            df_filtered = df[df[nivel_col].apply(match_floor)]
            total_doors = int(df_filtered["Numeric_Total"].sum())

            st.write(f"**Doors on {selected_level} (Total Instances: {total_doors}):**")
            for _, r in df_filtered.iterrows():
                qty = int(r.get("Numeric_Total", 1))
                st.text(f"• {r.get(mark_col, 'N/A')} ({r.get(type_col, 'N/A')}) [Qty: {qty}]")

        elif filter_mode == "PLOT number" and plot_col:
            individual_plots = set()
            for p_str in df[plot_col].dropna().astype(str):
                matches = re.findall(r'PLOT\s*\d+', p_str, re.IGNORECASE)
                if matches:
                    for m in matches:
                        individual_plots.add(m.upper())
                else:
                    for token in p_str.replace(";", ",").replace("\n", " ").split():
                        if token.strip():
                            individual_plots.add(token.strip().upper())
            
            plots = sorted(list(individual_plots))
            selected_plot = st.selectbox("Select PLOT:", plots)
            
            # Strict token-level matching so a row is only counted if it explicitly targets this exact plot token
            def match_plot(val):
                if pd.isna(val): return False
                # Split cell text into individual plot words/tokens
                tokens = re.findall(r'PLOT\s*\d+|\b\d+\b', str(val), re.IGNORECASE)
                return selected_plot.upper() in [t.upper() for t in tokens]

            df_filtered = df[df[plot_col].apply(match_plot)]
            total_doors = int(df_filtered["Numeric_Total"].sum())

            st.write(f"**Doors in {selected_plot} (Total Instances: {total_doors}):**")
            for _, r in df_filtered.iterrows():
                qty = int(r.get("Numeric_Total", 1))
                st.text(f"• {r.get(mark_col, 'N/A')} ({r.get(type_col, 'N/A')}) [Qty: {qty}]")
