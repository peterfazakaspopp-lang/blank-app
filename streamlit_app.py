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

# Initialize session state for search mode
if "search_active" not in st.session_state:
    st.session_state.search_active = False

if not df.empty:
    fam_col = "Family" if "Family" in df.columns else df.columns[0]
    type_col = "TIP" if "TIP" in df.columns else df.columns[1]
    mark_col = "INDICATIV USA" if "INDICATIV USA" in df.columns else df.columns[3]
    fire_col = "REZISTENTA FOC" if "REZISTENTA FOC" in df.columns else None

    df["Clean_Family"] = df[fam_col].astype(str).str.upper()
    df["Clean_Type"] = df[type_col].astype(str).str.upper()

    def is_checked(val):
        if pd.isna(val):
            return False
        v_str = str(val).strip().lower()
        return v_str in ["✓", "yes", "da", "1", "true", "x"]

    # --- SIDEBAR SEARCH & NAVIGATION ---
    st.sidebar.subheader("🔍 Advanced Door Search")
    
    families = sorted([x for x in df["Clean_Family"].dropna().unique() if x.strip() and "TOTAL" not in x and "LINKED REVIT MODEL" not in x])
    selected_sidebar_family = st.sidebar.selectbox("Select Family for Search:", families)
    
    df_sidebar_fam = df[df["Clean_Family"] == selected_sidebar_family]

    dim_query = st.sidebar.text_input("Dimension Search (e.g., 1000x2160):", "").strip().lower()

    fire_ratings = ["All"] + sorted([str(x) for x in df_sidebar_fam[fire_col].dropna().unique() if str(x).strip()]) if fire_col else ["All"]
    selected_fire = st.sidebar.selectbox("Fire Rating / Type (UM, UM-C, EI60, etc.):", fire_ratings)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Required Parameters:**")
    req_ba = st.sidebar.checkbox("BA (BARA ANTIPANICA)")
    req_ca = st.sidebar.checkbox("CA (CONTROL ACCES)")
    req_ym = st.sidebar.checkbox("YM (YALA MASTERKEY)")
    req_mda = st.sidebar.checkbox("MDA (DESCHIDERE AUTOMATA)")
    req_er = st.sidebar.checkbox("ER (ELECTROMAGNET)")

    search_triggered = st.sidebar.button("🔎 Search Door Configuration")
    if search_triggered:
        st.session_state.search_active = True

    # --- MAIN VIEW ---
    if st.session_state.search_active:
        if st.button("🔙 Back to Hierarchical Explorer"):
            st.session_state.search_active = False
            st.rerun()

        st.subheader(f"Search Results for Family: {selected_sidebar_family}")
        
        sub_df = df_sidebar_fam.copy()
        if dim_query:
            sub_df = sub_df[sub_df["Clean_Type"].str.lower().str.contains(dim_query, na=False)]
        
        if selected_fire != "All" and fire_col:
            sub_df = sub_df[sub_df[fire_col].astype(str).str.lower() == selected_fire.lower()]

        if sub_df.empty:
            st.warning(f"❌ **The door type does not exist** for family '{selected_sidebar_family}' with dimensions matching '{dim_query}' and fire rating '{selected_fire}'.")
        else:
            matched_rows = []
            for _, r in sub_df.iterrows():
                match_ba = is_checked(r.get("BA", "")) == req_ba if req_ba else True
                match_ca = is_checked(r.get("CA", "")) == req_ca if req_ca else True
                match_ym = is_checked(r.get("YM", "")) == req_ym if req_ym else True
                match_mda = is_checked(r.get("MDA", "")) == req_mda if req_mda else True
                match_er = is_checked(r.get("ER", "")) == req_er if req_er else True

                if match_ba and match_ca and match_ym and match_mda and match_er:
                    matched_rows.append(r)

            if matched_rows:
                st.success(f"✅ Found {len(matched_rows)} matching door instance(s) with the exact parameter configuration!")
                for m_row in matched_rows:
                    t_val = m_row.get(type_col, 'N/A')
                    m_val = m_row.get(mark_col, 'N/A')
                    
                    ba_icon = "✅" if is_checked(m_row.get("BA", "")) else "❌"
                    ca_icon = "✅" if is_checked(m_row.get("CA", "")) else "❌"
                    ym_icon = "✅" if is_checked(m_row.get("YM", "")) else "❌"
                    mda_icon = "✅" if is_checked(m_row.get("MDA", "")) else "❌"
                    er_icon = "✅" if is_checked(m_row.get("ER", "")) else "❌"

                    st.info(
                        f"**Type**: `{t_val}`  |  **INDICATIV**: `{m_val}`<br>"
                        f"&nbsp;&nbsp;&nbsp;&nbsp;**BA**: {ba_icon} &nbsp;|&nbsp; **CA**: {ca_icon} &nbsp;|&nbsp; **YM**: {ym_icon} &nbsp;|&nbsp; **MDA**: {mda_icon} &nbsp;|&nbsp; **ER**: {er_icon}",
                        icon="🚪"
                    )
            else:
                st.info(f"⚠️ **The door type exists** with those dimensions/fire rating, **but not with all the specific parameters selected**. It needs another code (INDICATIV).")
                with st.expander("View available types with these dimensions/fire rating"):
                    for _, r in sub_df.iterrows():
                        t_val = r.get(type_col, 'N/A')
                        m_val = r.get(mark_col, 'N/A')
                        ba_icon = "✅" if is_checked(r.get("BA", "")) else "❌"
                        ca_icon = "✅" if is_checked(r.get("CA", "")) else "❌"
                        ym_icon = "✅" if is_checked(r.get("YM", "")) else "❌"
                        mda_icon = "✅" if is_checked(r.get("MDA", "")) else "❌"
                        er_icon = "✅" if is_checked(r.get("ER", "")) else "❌"
                        st.text(f"• Type: {t_val} | INDICATIV: {m_val} [BA:{ba_icon} CA:{ca_icon} YM:{ym_icon} MDA:{mda_icon} ER:{er_icon}]")
    else:
        st.subheader("🗂️ Hierarchical Door Explorer")
        
        selected_main_family = st.selectbox("Family:", families)
        df_fam = df[df["Clean_Family"] == selected_main_family]

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
import os
from openai import OpenAI

# --- OPENAI Q&A CHAT COMPONENT ---
st.markdown("---")
st.subheader("💬 Project Code & Data Assistant")

# Initialize OpenAI client using Streamlit secrets or environment variables
api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

if not api_key:
    st.info("💡 To enable the AI chat assistant, please configure your `OPENAI_API_KEY` in `.streamlit/secrets.toml` or your environment variables.")
else:
    client = OpenAI(api_key=api_key)

    # Chat input for user queries
    user_query = st.chat_input("Ask a question about your doors, scripts, or project files (e.g., 'Which doors have less than 7cm clearance?')...")

    if user_query:
        with st.chat_message("user"):
            st.write(user_query)

        # Gather context from local files if available (e.g., PLOT_MASTER.tsv or python scripts)
        context_data = ""
        target_files = ["PLOT_MASTER.tsv"]
        
        for file_ name in target_files:
            if os.path.exists(file_name):
                try:
                    with open(file_name, "r", encoding="utf-8-sig") as f:
                        # Read snippet or summary to avoid overloading context limit
                        content = f.read()
                        context_data += f"\n--- File: {file_name} ---\n{content[:5000]}" # Truncate if too long
                except Exception as e:
                    pass

        # Prompt engineering providing context and source citation requirements
        system_prompt = (
            "You are an expert AI assistant helping an architect audit Revit door clearances and project data. "
            "Answer the user's question using ONLY the provided project file context below. "
            "Always cite the file path or data source you used in your answer. "
            "If the answer cannot be found in the context, explicitly state that you cannot find the answer based on the current data."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Project Context:\n{context_data}\n\nUser Question: {user_query}"}
        ]

        with st.chat_message("assistant"):
            with st.spinner("Analyzing project data..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini", # or gpt-4o
                        messages=messages,
                        temperature=0.2
                    )
                    answer = response.choices[0].message.content
                    st.write(answer)
                except Exception as e:
                    st.error(f"Error communicating with OpenAI API: {e}")

