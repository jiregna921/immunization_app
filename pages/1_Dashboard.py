import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Utilization Dashboard", 
    layout="wide",
    page_icon="💉"
)

# The custom CSS for the dark theme has been removed to revert to the default Streamlit styling.

st.title("📊 Vaccine Utilization Dashboard")

# --- Correcting the No Dataset Found error with a dummy dataset ---
if "immunization_data" not in st.session_state:
    st.info("No dataset found. A sample dataset has been loaded for demonstration.")
    # Creating a dummy dataset to allow the dashboard to run without an uploaded file
    dummy_data = {
        "Period": ["2023-Q4", "2023-Q4", "2023-Q4", "2023-Q4", "2023-Q4", "2023-Q4"],
        "Region": ["Region A", "Region A", "Region B", "Region B", "Region C", "Region C"],
        "Zone": ["Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Zone 6"],
        "Woreda": ["Woreda A1", "Woreda A2", "Woreda B1", "Woreda B2", "Woreda C1", "Woreda C2"],
        "BCG Distrib": [1000, 1500, 2000, 1200, 800, 1800],
        "BCG Admin": [800, 1400, 1800, 500, 750, 1700],
        "IPV Distrib": [500, 800, 1000, 600, 400, 900],
        "IPV Admin": [480, 750, 950, 300, 380, 850],
        "Measles Distrib": [1200, 1000, 1500, 800, 600, 1100],
        "Measles Admin": [700, 950, 1400, 500, 550, 1050],
        "Penta Distrib": [900, 1100, 1300, 700, 500, 1000],
        "Penta Admin": [850, 1050, 1250, 650, 450, 980],
        "Rota Distrib": [700, 900, 1200, 500, 300, 800],
        "Rota Admin": [650, 800, 1100, 450, 280, 750],
    }
    st.session_state["immunization_data"] = pd.DataFrame(dummy_data)


# --- Threshold configuration for each vaccine ---
VACCINE_THRESHOLDS = {
    "BCG": {
        "unacceptable": 100,  # >100%
        "acceptable": 50,     # >50% to 100%
    },
    "IPV": {
        "unacceptable": 100,  # >100%
        "acceptable": 90,     # >90% to 100%
    },
    "Measles": {
        "unacceptable": 100,
        "acceptable": 65,
    },
    "Penta": {
        "unacceptable": 100,
        "acceptable": 95,
    },
    "Rota": {
        "unacceptable": 100,
        "acceptable": 90,
    },
    # Add a default for any other vaccines not listed
    "Default": {
        "unacceptable": 100,
        "acceptable": 65, # Using 65 as a default threshold
    }
}

def categorize_utilization(row):
    """
    Categorizes the utilization rate based on the vaccine-specific thresholds.
    """
    rate = row["Utilization Rate"]
    antigen = row["Antigen"]
    
    thresholds = VACCINE_THRESHOLDS.get(antigen, VACCINE_THRESHOLDS["Default"])

    if rate > thresholds["unacceptable"]:
        return "Unacceptable"
    elif rate >= thresholds["acceptable"]:
        return "Acceptable"
    else:
        return "Low Utilization"

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
    
    # Calculate Utilization Rate and Category, rounded to 0 decimal places
    df_pivot["Utilization Rate"] = df_pivot.apply(
        lambda row: round((row["Administered"] / row["Distributed"] * 100), 0) if row["Distributed"] > 0 else 0,
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
    (total_administered / total_distributed * 100) if total_distributed > 0 else 0, 0
)

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Vaccines Distributed", value=f"{total_distributed:,.0f}")
with col2:
    st.metric(label="Total Vaccines Administered", value=f"{total_administered:,.0f}")
with col3:
    st.metric(label="Overall Utilization Rate", value=f"{overall_utilization_rate:.0f}%")
st.markdown("---")

# --- Displaying Woreda Counts by Category ---
total_woredas = len(filtered_df["Woreda"].unique())
category_counts = filtered_df["Utilization Category"].value_counts()

st.subheader("Woreda Counts by Utilization Category")
col_woredas1, col_woredas2, col_woredas3, col_woredas4 = st.columns(4)

with col_woredas1:
    st.metric(label="Total Woredas", value=f"{total_woredas:,.0f}")
with col_woredas2:
    st.metric(label="Acceptable", value=f"{category_counts.get('Acceptable', 0):,.0f}")
with col_woredas3:
    st.metric(label="Unacceptable", value=f"{category_counts.get('Unacceptable', 0):,.0f}")
with col_woredas4:
    st.metric(label="Low Utilization", value=f"{category_counts.get('Low Utilization', 0):,.0f}")
st.markdown("---")


# --- Summary and Visualization Data Preparation ---
# Data for the pie chart
category_counts_pie = filtered_df["Utilization Category"].value_counts().reset_index()
category_counts_pie.columns = ["Category", "Count"]

# Data for the 100% stacked bar chart, dynamically grouped by Region or Zone
if selected_region == "All":
    groupby_col = "Region"
else:
    groupby_col = "Zone"

# Group by the selected column and Utilization Category, then calculate counts
stacked_bar_data = filtered_df.groupby([groupby_col, "Utilization Category"]).size().reset_index(name='Count')

# Calculate the total count per group (Region or Zone)
total_by_group = stacked_bar_data.groupby(groupby_col)["Count"].sum().reset_index(name='Total')

# Merge the total counts back to the stacked_bar_data
stacked_bar_data = stacked_bar_data.merge(total_by_group, on=groupby_col)

# Calculate the percentage for each category within each group
stacked_bar_data["Percentage"] = (stacked_bar_data["Count"] / stacked_bar_data["Total"] * 100).round(0)

# --- Color Mapping ---
color_map = {
    "Acceptable": "green", 
    "Unacceptable": "blue",
    "Low Utilization": "red"
}

# Adjust column widths for better layout
col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    st.subheader(f"Utilization Breakdown by {'Region' if selected_region == 'All' else 'Zone'} ({selected_antigen})")
    
    # Corrected approach using plotly.graph_objects for explicit stacking
    bar_fig = go.Figure()
    
    # Define the order of categories for stacking
    categories = ["Acceptable", "Low Utilization", "Unacceptable"]
    
    for category in categories:
        filtered_data = stacked_bar_data[stacked_bar_data["Utilization Category"] == category]
        bar_fig.add_trace(go.Bar(
            x=filtered_data[groupby_col],
            y=filtered_data["Percentage"],
            name=category,
            marker_color=color_map[category],
            text=filtered_data["Percentage"],
            textposition='inside',
            insidetextanchor='middle',
            texttemplate='%{y:.0f}%',
            hovertemplate=f"<b>%{{x}}</b><br>{category}: %{{y:.0f}}%<br>District Count: %{{customdata}}<extra></extra>",
            customdata=filtered_data['Count']
        ))
    
    bar_fig.update_layout(
        barmode="stack",
        yaxis=dict(
            title="Percentage (%)",
            range=[0, 100],
            tickformat=".0f"
        ),
        xaxis=dict(
            title=groupby_col,
            tickangle=-45
        ),
        title=f"100% Stacked Utilization by {'Region' if selected_region == 'All' else 'Zone'} - {selected_antigen} ({selected_period})",
        legend_title_text="Utilization Category",
        bargap=0.2,
        showlegend=True
    )

    st.plotly_chart(bar_fig, use_container_width=True)

with col_chart2:
    st.subheader("Overall Utilization Breakdown")
    pie_fig = px.pie(
        category_counts_pie,
        values="Count",
        names="Category",
        title="Overall Utilization Distribution",
        hole=0.4,
        color="Category",
        color_discrete_map=color_map,
    )
    # Reverting chart colors to default
    pie_fig.update_traces(textfont_color="black") # Assuming black text on white background is readable
    pie_fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        title_font=dict(size=18, color='black'),
        font=dict(color='black')
    )
    st.plotly_chart(pie_fig, use_container_width=True)

st.markdown("---")
with st.expander("📋 Show Woreda-Level Data"):
    st.dataframe(filtered_df[[
        "Region", "Zone", "Woreda", "Antigen", "Distributed", "Administered", "Utilization Rate", "Utilization Category"
    ]].sort_values(by="Utilization Rate", ascending=False).reset_index(drop=True))
