import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="📈 Utilization Dashboard", layout="wide")

st.title("📈 Vaccine Utilization Dashboard")

# ✅ Check if data is uploaded
if "data" not in st.session_state:
    st.warning("⚠️ Please upload a dataset from the Home page first.")
    st.stop()

df = st.session_state["data"]

# ✅ Ensure required columns exist
required_columns = [
    "Region", "Zone", "Woreda", "Period",
    "BCG Distributed", "BCG Administered",
    "IPV Distributed", "IPV Administered",
    "Measles Distributed", "Measles Administered",
    "Penta Distributed", "Penta Administered",
    "Rota Distributed", "Rota Administered"
]

missing = [col for col in required_columns if col not in df.columns]
if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

# ✅ Calculate Utilization Rate
def calculate_utilization(row):
    total_distributed = sum([
        row["BCG Distributed"], row["IPV Distributed"],
        row["Measles Distributed"], row["Penta Distributed"],
        row["Rota Distributed"]
    ])
    total_administered = sum([
        row["BCG Administered"], row["IPV Administered"],
        row["Measles Administered"], row["Penta Administered"],
        row["Rota Administered"]
    ])
    if total_distributed == 0:
        return 0
    return (total_administered / total_distributed) * 100

df["Utilization Rate (%)"] = df.apply(calculate_utilization, axis=1)

# ✅ Categorize
def categorize(rate):
    if rate > 100:
        return "Unacceptable"
    elif 80 <= rate <= 100:
        return "Acceptable"
    else:
        return "Low Utilization"

df["Utilization Category"] = df["Utilization Rate (%)"].apply(categorize)

# ✅ Filters
periods = ["All"] + sorted(df["Period"].dropna().unique())
regions = ["All"] + sorted(df["Region"].dropna().unique())
zones = ["All"] + sorted(df["Zone"].dropna().unique())

col1, col2, col3 = st.columns(3)
selected_period = col1.selectbox("Filter by Period", periods)
selected_region = col2.selectbox("Filter by Region", regions)
selected_zone = col3.selectbox("Filter by Zone", zones)

# ✅ Apply filters
filtered_df = df.copy()
if selected_period != "All":
    filtered_df = filtered_df[filtered_df["Period"] == selected_period]
if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]
if selected_zone != "All":
    filtered_df = filtered_df[filtered_df["Zone"] == selected_zone]

# ✅ Count and Percentage
category_counts = filtered_df["Utilization Category"].value_counts().reindex(["Unacceptable", "Acceptable", "Low Utilization"], fill_value=0)
total = category_counts.sum()
category_percentages = (category_counts / total * 100).round(2)

st.subheader("Woreda Utilization Summary")
col1, col2 = st.columns(2)
with col1:
    st.write("### Count of Woredas")
    st.dataframe(category_counts.rename("Count"))

with col2:
    st.write("### Percentage of Woredas")
    st.dataframe(category_percentages.rename("%"))

# ✅ Bar Chart
fig1, ax1 = plt.subplots()
category_counts.plot(kind="bar", color=["blue", "green", "red"], ax=ax1)
ax1.set_title("Woreda Utilization by Category")
ax1.set_ylabel("Number of Woredas")
ax1.set_xlabel("Utilization Category")
st.pyplot(fig1)

# ✅ Pie Chart
fig2, ax2 = plt.subplots()
ax2.pie(category_percentages, labels=category_percentages.index, autopct="%1.1f%%", colors=["blue", "green", "red"], startangle=90)
ax2.set_title("Utilization Category Distribution")
st.pyplot(fig2)
