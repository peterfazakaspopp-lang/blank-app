import pandas as pd
import streamlit as st

st.title("🗂️ Interactive Door Schedule Explorer")

# 1. Load your exported Excel/TSV files (combining plots if needed)
@st.cache_data
def load_data():
    # Example loading PLOT_1; expand to combine PLOT_1 through PLOT_5
    df = pd.read_csv(r"D:\PROIECTE\ASX\Tablouri tamplarie\PLOT_1.xls", sep="\t")
    return df

df = load_data()

# 2. Level 1: Family Selection
families = sorted(df["AMPLASARE/ TIP USA/ NR CANATURI - REPEZENTARE CONFORM DESEN"].dropna().unique())
selected_family = st.selectbox("Select Door Family", families)

# Filter dataframe based on Family
df_fam = df[df["AMPLASARE/ TIP USA/ NR CANATURI - REPEZENTARE CONFORM DESEN"] == selected_family]

# 3. Level 2: Type / Type Mark Selection
type_marks = sorted(df_fam["INDICATIV USA"].dropna().unique())
selected_type_mark = st.selectbox("Select Type / Type Mark", type_marks)

# Filter further
df_type = df_fam[df_fam["INDICATIV USA"] == selected_type_mark]

# 4. Level 3: Door Mark Selection
door_marks = sorted(df_type["INDICATIV USA"].dropna().unique()) # or specific instance mark if available
selected_door = st.selectbox("Select Door Mark", door_marks)

# Get the specific row data
row_data = df_type[df_type["INDICATIV USA"] == selected_door].iloc[0]

st.divider()
st.subheader(f"Door Details for: {selected_door}")

# 5. Level 4: Interactive Tickboxes for Features (BA, CA, YM, MDA, ER)
# Assuming columns match your headers: "BA", "CA", "YM", "MDA", "ER"
col1, col2, col3, col4, col5 = st.columns(5)

ba_val = col1.checkbox("BA (Bara antipanica)", value=(str(row_data.get("BA", "")) == "✓"))
ca_val = col2.checkbox("CA (Control acces)", value=(str(row_data.get("CA", "")) == "✓"))
ym_val = col3.checkbox("YM (Yala masterkey)", value=(str(row_data.get("YM", "")) == "✓"))
mda_val = col4.checkbox("MDA (Auto incendiu)", value=(str(row_data.get("MDA", "")) == "✓"))
er_val = col5.checkbox("ER", value=(str(row_data.get("ER", "")) == "✓"))
