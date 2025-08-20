import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Assume data is already loaded or passed via session state ---
if "immunization_data" not in st.session_state:
    st.warning("Data not loaded. Please go to the Home page first.")
    st.stop()
    
df = st.session_state["immunization_data"]

st.set_page_config(
    page_title="Dashboard 1",
    layout="wide",
    page_icon="1️⃣"
)

# Custom header for this page
st.markdown("""
<style>
.main-header-container h1 {
    color: white;
    font-size: 1.5rem;
    text-align: center;
}
</style>
<div class="main-header-container" style="background-color: #0072b2; padding: 1rem; border-radius: 10px; margin-bottom: 0.25rem;">
    <h1>First Immunization Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Filters specific to this dashboard ---
st.sidebar.header("Dashboard 1 Filters")

available_periods = sorted(df["Period"].unique().tolist(), reverse=True)
selected_period = st.sidebar.selectbox("Select Period", available_periods)

available_antigens = sorted(df["Antigen"].dropna().unique().tolist())
selected_antigen = st.sidebar.selectbox("Select Antigen", available_antigens)

# --- Filtering the data ---
filtered_df = df[(df["Period"] == selected_period) & (df["Antigen"] == selected_antigen)].copy()

if filtered_df.empty:
    st.warning("⚠️ No data found for the selected filters. Please adjust your selections.")
    st.stop()

# --- Dashboard 1 Content: Example Charts ---
st.subheader(f"Total Distributed vs Administered for {selected_antigen}")
summary_df = filtered_df.groupby('Region')[['Distributed', 'Administered']].sum().reset_index()

fig = px.bar(summary_df,
             x='Region',
             y=['Distributed', 'Administered'],
             barmode='group',
             title=f'Vaccine Distribution vs Administration by Region ({selected_antigen})')

st.plotly_chart(fig, use_container_width=True)

# --- Other visualizations or tables for this dashboard ---
st.subheader("Regional Utilization Rate")
regional_utilization = filtered_df.groupby('Region').apply(
    lambda x: (x['Administered'].sum() / x['Distributed'].sum() * 100) if x['Distributed'].sum() > 0 else 0
).reset_index(name='Utilization Rate')

st.dataframe(regional_utilization.sort_values(by="Utilization Rate", ascending=False).reset_index(drop=True))
