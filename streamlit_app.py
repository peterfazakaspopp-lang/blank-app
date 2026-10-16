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
                # Split by spaces, commas, or newlines to get distinct level tokens
                tokens = [t.upper() for t in re.split(r'[\s,\n]+', str(val))]
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
            
            def match_plot(val):
                if pd.isna(val): return False
                # Extract all plot references in this cell (e.g., "PLOT 1", "PLOT 3")
                cell_plots = [m.upper() for m in re.findall(r'PLOT\s*\d+', str(val), re.IGNORECASE)]
                if not cell_plots:
                    # Fallback token check
                    cell_plots = [t.upper() for t in re.split(r'[\s,\n]+', str(val))]
                return selected_plot.upper() in cell_plots

            df_filtered = df[df[plot_col].apply(match_plot)]
            total_doors = int(df_filtered["Numeric_Total"].sum())

            st.write(f"**Doors in {selected_plot} (Total Instances: {total_doors}):**")
            for _, r in df_filtered.iterrows():
                qty = int(r.get("Numeric_Total", 1))
                st.text(f"• {r.get(mark_col, 'N/A')} ({r.get(type_col, 'N/A')}) [Qty: {qty}]")
