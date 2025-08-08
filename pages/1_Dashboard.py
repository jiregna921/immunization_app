import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Utilization Dashboard", 
    layout="wide",
    page_icon="💉" # Sets the icon for the browser tab
)

# --- Add a logo to the main page ---
# The logo is in the 'logo' folder relative to the app's root directory.
# Replace 'logo.png' with your actual logo file name.
st.image("logo/logo.png", width=100)

st.title("📊 Vaccine Utilization Dashboard")

if "immunization_data" not in st.session_state:
    st.error("❌ No dataset found. Please upload a file on the Home page.")
    st.stop()

# --- Custom Utilization Categorization based on the provided image
def categorize_utilization(row):
    """
    Categorizes the utilization rate based on the thresholds provided in the image.
    Low Utilization: <65%
    Acceptable: 65% - 100%
    Unacceptable: >100%
    """
    rate = row["Utilization Rate"]
    if rate > 100:
        return "Unacceptable (>100%)"
    elif 65 <= rate <= 100:
        return "Acceptable (65–100%)"
    else:
        return "Low Utilization (<65%)"

# --- Cached Data Processing (Rewritten for your wide data format) ---
@st.cache_data
def prepare_data(data):
    """
    Transforms the wide-format data (e.g., 'BCG Distrib', 'IPV Distrib')
    into a long-format DataFrame suitable for analysis.
    """
    data_processed = data.copy()
    
    # Identify all columns related to distributed and administered vaccines
    distrib_cols = [col for col in data_processed.columns if 'Distrib' in str(col)]
    admin_cols = [col for col in data_processed.columns if 'Admin' in str(col)]

    # Get the unique antigens by cleaning the column names
    antigens = [col.replace(' Distrib', '') for col in distrib_cols]

    # Combine all relevant columns for melting
    all_antigen_cols = distrib_cols + admin_cols
    id_vars = [col for col in data_processed.columns if col not in all_antigen_cols]

    # Melt the DataFrame to convert from wide to long format
    df_long = pd.melt(data_processed, 
                      id_vars=id_vars, 
                      value_vars=all_antigen_cols,
                      var_name='AntigenType',
                      value_name='Count')

    # Separate 'Antigen' name and 'Type' (Distributed or Administered)
    df_long['Antigen'] = df_long['AntigenType'].apply(lambda x: x.split(' ')[0])
    df_long['Type'] = df_long['AntigenType'].apply(lambda x: 'Distributed' if 'Distrib' in x else 'Administered')
    
    # Pivot the table to get 'Distributed' and 'Administered' as separate columns
    df_pivot = df_long.pivot_table(index=id_vars + ['Antigen'],
                                   columns='Type',
                                   values='Count').reset_index()
    
    # Clean up column names after pivoting
    df_pivot.columns.name = None
    df_pivot = df_pivot.rename(columns={'Distributed': 'Distributed', 'Administered': 'Administered'})

    # Fill any NaN values with 0 and convert to numeric
    df_pivot["Distributed"] = pd.to_numeric(df_pivot["Distributed"], errors="coerce").fillna(0)
    df_pivot["Administered"] = pd.to_numeric(df_pivot["Administered"], errors="coerce").fillna(0)
    
    # Calculate Utilization Rate and Category
    df_pivot["Utilization Rate"] = df_pivot.apply(
        lambda row: round((row["Administered"] / row["Distributed"] * 100), 2) if row["Distributed"] > 0 else 0,
        axis=1
    )
    df_pivot["Utilization Category"] = df_pivot.apply(categorize_utilization, axis=1)
    
    return df_pivot

# Process the data using the new function
df = prepare_data(st.session_state["immunization_data"].copy())

# --- Sidebar Filters (using standardized column names) ---
st.sidebar.header("🧪 Filter Data")

available_periods = sorted(df["Period"].unique().tolist(), reverse=True)
available_regions = ["All"] + sorted(df["Region"].dropna().unique().tolist())
available_antigens = sorted(df["Antigen"].dropna().unique().tolist())

selected_period = st.sidebar.selectbox("Select Period", available_periods)
selected_region = st.sidebar.selectbox("Select Region", available_regions, index=0)

# Filter zones based on the selected region
if selected_region == "All":
    available_zones = ["All"] + sorted(df["Zone"].dropna().unique().tolist())
else:
    available_zones = ["All"] + sorted(df[df["Region"] == selected_region]["Zone"].dropna().unique().tolist())
    
selected_zone = st.sidebar.selectbox("Select Zone", available_zones, index=0)

selected_antigen = st.sidebar.selectbox("Select Antigen", available_antigens, index=0)

# --- Filtering ---
filtered_df = df[(df["Period"] == selected_period)].copy()

if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]
if selected_zone != "All":
    filtered_df = filtered_df[filtered_df["Zone"] == selected_zone]
if selected_antigen:
    filtered_df = filtered_df[filtered_df["Antigen"] == selected_antigen]

if filtered_df.empty:
    st.warning("⚠️ No data found for the selected filters. Please adjust your selections.")
    st.stop()

# --- Displaying Summary Metrics Horizontally ---
total_distributed = filtered_df["Distributed"].sum()
total_administered = filtered_df["Administered"].sum()
overall_utilization_rate = round(
    (total_administered / total_distributed * 100) if total_distributed > 0 else 0, 2
)

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Vaccines Distributed", value=f"{total_distributed:,.0f}")
with col2:
    st.metric(label="Total Vaccines Administered", value=f"{total_administered:,.0f}")
with col3:
    st.metric(label="Overall Utilization Rate", value=f"{overall_utilization_rate:.2f}%")
st.markdown("---")

# --- Summary and Visualization Data Preparation ---
category_counts = filtered_df["Utilization Category"].value_counts().reset_index()
category_counts.columns = ["Category", "Count"]

total_count = category_counts["Count"].sum()
if total_count > 0:
    category_counts["Percentage"] = (100 * category_counts["Count"] / total_count).round(2)
else:
    category_counts["Percentage"] = 0

# --- Color Mapping (Updated to match the image) ---
color_map = {
    "Unacceptable (>100%)": "blue",
    "Acceptable (65–100%)": "#008B8B", # Dark Cyan (A nice teal)
    "Low Utilization (<65%)": "red" # Changed from a lighter red to a full red
}

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader(f"Utilization Category Distribution ({selected_antigen})")
    bar_fig = px.bar(
        category_counts,
        x="Category",
        y="Count",
        color="Category",
        text="Percentage",
        color_discrete_map=color_map,
        title=f"Vaccine Utilization Categories - {selected_antigen} ({selected_period})",
    )
    bar_fig.update_traces(texttemplate='%{text:.2s}%', textposition="outside", 
                           textfont_color=['white' if cat == 'Low Utilization (<65%)' else 'black' for cat in category_counts['Category']])
    bar_fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(bar_fig, use_container_width=True)

with col_chart2:
    st.subheader("Utilization Category Breakdown")
    pie_fig = px.pie(
        category_counts,
        values="Count",
        names="Category",
        title="Utilization Category Distribution",
        hole=0.4,
        color="Category",
        color_discrete_map=color_map,
    )
    # Set text color to white for better contrast
    pie_fig.update_traces(textfont_color="white")
    st.plotly_chart(pie_fig, use_container_width=True)

st.markdown("---")
with st.expander("📋 Show Woreda-Level Data"):
    st.dataframe(filtered_df[[
        "Region", "Zone", "Woreda", "Antigen", "Distributed", "Administered", "Utilization Rate", "Utilization Category"
    ]].sort_values(by="Utilization Rate", ascending=False).reset_index(drop=True))
