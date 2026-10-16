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
    fire_col = "REZISTENTA FOC" if "REZISTENTA FOC" in df.columns else None

    df["Clean_Family"] = df[fam_col].astype(str).str.upper()
    df["Clean_Type"] = df[type_col].astype(str).str.upper()

    if "TOTAL" in df.columns:
        df["Numeric_Total"] = pd.to_numeric(df["TOTAL"], errors="coerce").fillna(1)
    else:
        df["Numeric_Total"] = 1

    def is_checked(val):
        if pd.isna(val):
            return False
        v_str = str(val).strip().lower()
        return v_str in ["✓", "yes", "da", "1", "true", "x"]

    # --- SIDEBAR SEARCH & NAVIGATION ---
    st.sidebar.subheader("🔍 Advanced Door Search")
    
    families = sorted([x for x in df["Clean_Family"].dropna().unique() if x.strip() and "TOTAL" not in x and "LINKED REVIT MODEL" not in x])
    selected_family = st.sidebar.selectbox("Select Family:", families)
    
    df_fam = df[df["Clean_Family"] == selected_family]

    # Dimension search input (e.g. 1000x2160 or part of it)
    dim_query = st.sidebar.text_input("Dimension Search (e.g., 1000x2160):", "").strip().lower()

    # Fire rating filter options
    fire_ratings = ["All"] + sorted([str(x) for x in df_fam[fire_col].dropna().unique() if str(x).strip()]) if fire_col else ["All"]
    selected_fire = st.sidebar.selectbox("Fire Rating / Type (UM, UM-C, EI60, etc.):", fire_ratings)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Required Parameters:**")
    req_ba = st.sidebar.checkbox("BA (BARA ANTIPANICA)")
    req_ca = st.sidebar.checkbox("CA (CONTROL ACCES)")
    req_ym = st.sidebar.checkbox("YM (YALA MASTERKEY)")
    req_mda = st.sidebar.checkbox("MDA (DESCHIDERE AUTOMATA)")
    req_er = st.sidebar.checkbox("ER (ELECTROMAGNET)")

    search_triggered = st.sidebar.button("🔎 Search Door Configuration")

    main_col, side_col = st.columns([2, 1])

    with main_col:
        if search_triggered:
            st.subheader(f"Search Results for Family: {selected_family}")
            
            # Filter by family & dimensions if provided
            sub_df = df_fam.copy()
            if dim_query:
                sub_df = sub_df[sub_df["Clean_Type"].str.lower().str.contains(dim_query, na=False)]
            
            if selected_fire != "All" and fire_col:
                sub_df = sub_df[sub_df[fire_col].astype(str).str.lower() == selected_fire.lower()]

            if sub_df.empty:
                st.warning(f"❌ **The door type does not exist** for family '{selected_family}' with dimensions matching '{dim_query}' and fire rating '{selected_fire}'.")
            else:
                # Check parameter matches among filtered rows
                matched_rows = []
                for _, r in sub_df.iterrows():
                    match_ba = is_checked(r.get("BA", "")) == req_ba
                    match_ca = is_checked(r.get("CA", "")) == req_ca
                    match_ym = is_checked(r.get("YM", "")) == req_ym
                    match_mda = is_checked(r.get("MDA", "")) == req_mda
                    match_er = is_checked(r.get("ER", "")) == req_er

                    if match_ba and match_ca and match_ym and match_mda and match_er:
                        matched_rows.append(r)

                if matched_rows:
                    st.success(f"✅ Found {len(matched_rows)} matching door instance(s) with the exact parameter configuration!")
                    for m_row in matched_rows:
                        st.info(f"**Type**: `{m_row.get(type_col, 'N/A')}`  |  **INDICATIV**: `{m_row.get(mark_col, 'N/A')}`")
                else:
                    st.info(f"⚠️ **The door type exists** with those dimensions/fire rating, **but not with all the specific parameters selected**. It needs another code (INDICATIV).")
                    with st.expander("View available types with these dimensions/fire rating"):
                        for _, r in sub_df.iterrows():
                            st.text(f"• Type: {r.get(type_col, 'N/A')} | INDICATIV: {r.get(mark_col, 'N/A')}")
        else:
            st.subheader("🗂️ Hierarchical Door Explorer")
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

                        parameters = ["BA", "CA", "YM", "MDA", "ER"]
                        param_descriptions = {
                            "BA": "BARA ANTIPANICA",
                            "CA": "CONTROL ACCES",
                            "YM": "YALA MASTERKEY",
                            "MDA": "DESCHIDERE AUTOMATA INCENDIU",
                            "ER": "ELECTROMAGNET DE RETINERE"
                        }
                        
                        cols = st.columns(len(parameters))
                        for i, param in enumerate(parameters):
                            checked = is_checked(row_data.get(param, ""))
                            status_icon = "✅" if checked else "❌"
                            desc = param_descriptions.get(param, "")
                            
                            cols[i].markdown(
                                f"**{param}**: {status_icon}<br>"
                                f"<small style='text-transform: uppercase; color: #888;'>{desc}</small>",
                                unsafe_allow_html=True
                            )

                        with st.expander("🔍 View Raw Row Data from TSV", expanded=True):
                            st.write(row_data.to_dict())

    with side_col:
        st.subheader("📍 Quick Availability")
        
        total_schedule_instances = int(df["Numeric_Total"].sum())
        st.info(f"📊 **Model Baseline Summary**\n\n• Unique TSV Rows: {len(df)}\n• Total Schedule Instances: {total_schedule_instances}")
        
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
            
            def match_floor(val):
                if pd.isna(val): return False
                return selected_level.upper() in str(val).upper()

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
            
            def match_plot(val):
                if pd.isna(val): return False
                return selected_plot.upper() in str(val).upper()

            df_filtered = df[df[plot_col].apply(match_plot)]
            total_doors = int(df_filtered["Numeric_Total"].sum())

            st.write(f"**Doors in {selected_plot} (Total Instances: {total_doors}):**")
            for _, r in df_filtered.iterrows():
                qty = int(r.get("Numeric_Total", 1))
                st.text(f"• {r.get(mark_col, 'N/A')} ({r.get(type_col, 'N/A')}) [Qty: {qty}]")
