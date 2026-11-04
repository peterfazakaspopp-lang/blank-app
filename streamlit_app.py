import streamlit as st
import pandas as pd
import os
import json
import urllib.request
import urllib.error

st.set_page_config(layout="wide")
st.title("ASX_UM_XX_ALL")

# Initialize session states
if "search_active" not in st.session_state:
    st.session_state.search_active = False

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# --- GEMINI Q&A CHAT COMPONENT (TOP CONTAINER) ---
st.subheader("💬 Project Code & Data Assistant (Powered by Gemini)")

gemini_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not gemini_key:
    st.info("💡 To enable the free AI chat assistant, please configure your `GEMINI_API_KEY` in Streamlit secrets or environment variables.")
else:
    # Display chat history first
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Top-positioned input bar using text_input + button
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            user_query = st.text_input("Ask a question about your doors, scripts, or project files...", label_visibility="collapsed", placeholder="Ask a question about your doors, scripts, or project files...")
        with col2:
            submit_chat = st.form_submit_button("Send 🚀", use_container_width=True)

    if submit_chat and user_query:
        st.session_state.chat_messages.append({"role": "user", "content": user_query})

        context_data = ""
        target_files = ["PLOT_MASTER.tsv", "streamlit_app.py", "README.md"]
        
        for file_name in target_files:
            if os.path.exists(file_name):
                try:
                    with open(file_name, "r", encoding="utf-8-sig") as f:
                        content = f.read()
                        context_data += f"\n--- File: {file_name} ---\n{content[:4000]}\n"
                except Exception:
                    pass

        system_prompt = (
            "You are an expert AI assistant helping an architect audit Revit door clearances and project data. "
            "Answer the user's question using ONLY the provided project file context below. "
            "Always cite the file path or data source you used in your answer. "
            "If the answer cannot be found in the context, explicitly state that you cannot find the answer based on the current data."
        )

        full_prompt = f"{system_prompt}\n\nProject Context:\n{context_data}\n\nUser Question: {user_query}"

        try:
            req_data = json.dumps({
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }]
            }).encode("utf-8")

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"

            req = urllib.request.Request(
                url,
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req) as resp:
                res_body = json.loads(resp.read().decode("utf-8"))
                answer = res_body["candidates"][0]["content"]["parts"][0]["text"]
                st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                st.rerun()

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            st.error(f"Gemini API Error ({e.code}): {error_body}")
        except Exception as e:
            st.error(f"Error communicating with Gemini API: {e}")

st.markdown("---")

# --- DOOR DATA EXPLORER ---
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

    st.sidebar
