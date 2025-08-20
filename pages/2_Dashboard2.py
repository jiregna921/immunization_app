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
    page_title="Dashboard 2",
    layout="wide",
    page_icon="2️⃣"
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
<div class="main-header-container" style="background-color: #33a18a; padding: 1rem; border-radius: 10px; margin-bottom: 0.25rem;">
    <h1>Second Immunization Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Filters specific to this dashboard ---
st.sidebar.header("Dashboard 2 Filters")

available_periods = sorted(df["Period"].unique().tolist(), reverse=True)
selected_period = st.sidebar.selectbox("Select Period", available_periods)

# Filter for regions to see a more detailed view
available_regions = sorted(df["Region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", available_regions)

# --- Filtering the data ---
filtered_df = df[(df["Period"] == selected_period) & (df["Region"] == selected_region)].copy()

if filtered_df.empty:
    st.warning("⚠️ No data found for the selected filters. Please adjust your selections.")
    st.stop()

# --- Dashboard 2 Content: Example Charts ---
st.subheader(f"Utilization Rate by Antigen in {selected_region}")
antigen_utilization = filtered_df.groupby('Antigen').apply(
    lambda x: (x['Administered'].sum() / x['Distributed'].sum() * 100) if x['Distributed'].sum() > 0 else 0
).reset_index(name='Utilization Rate')

fig = px.line(antigen_utilization,
              x='Antigen',
              y='Utilization Rate',
              markers=True,
              title=f"Utilization Rate by Antigen in {selected_region} ({selected_period})")

st.plotly_chart(fig, use_container_width=True)

# --- Other visualizations or tables for this dashboard ---
st.subheader(f"Woreda-level Details for {selected_region}")
st.dataframe(filtered_df[['Woreda', 'Antigen', 'Distributed', 'Administered', 'Utilization Rate']].sort_values(by="Utilization Rate", ascending=False))
