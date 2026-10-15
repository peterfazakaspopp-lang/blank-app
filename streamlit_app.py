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
            # Extract all unique individual plots by splitting combined strings (e.g., "PLOT 1 PLOT 2" -> "PLOT 1", "PLOT 2")
            all_raw_plots = df[plot_col].dropna().astype(str)
            individual_plots = set()
            for p_str in all_raw_plots:
                # Split by spaces or keywords to get distinct plot names
                for token in p_str.replace(";", ",").split(","):
                    clean_token = token.strip()
                    if clean_token:
                        individual_plots.add(clean_token)
            
            plots = sorted(list(individual_plots))
            selected_plot = st.selectbox("Select Plot:", plots)
            
            # Filter rows where the plot column contains the selected individual plot token
            df_filtered = df[df[plot_col].astype(str).str.contains(selected_plot, case=False, na=False)]
            st.write(f"**Doors in {selected_plot} ({len(df_filtered)}):**")
            
            for _, r in df_filtered.iterrows():
                st.text(f"• {r.get(mark_col, 'N/A')} ({r.get(type_col, 'N/A')})")
