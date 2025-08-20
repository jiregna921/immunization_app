import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Custom CSS for improved styling ---
st.markdown("""
<style>
/* Overall page layout and styling */
.stApp {
    padding-top: 1rem;
    background-color: #F0F2F6; /* Light gray background for better visibility */
}

/* Header styling - now with reduced font size */
.main-header-container {
    background-color: #004643;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 0.25rem; /* Reduced from 0.5rem to 0.25rem for more compact layout */
}

.main-header-container h1 {
    color: white;
    margin: 0;
    text-align: center;
    font-size: 1.5rem; /* Reduced from 2.5rem to 1.5rem */
}

/* Custom metric styling, using title's color theme */
.custom-metric-box {
    background-color: #004643;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.custom-metric-label {
    font-size: 1rem; /* Reduced size */
    font-weight: bold;
    color: white;
    margin-bottom: 0.25rem;
}

.custom-metric-value {
    font-size: 1.5rem; /* Reduced size */
    font-weight: bold;
    color: white;
}

/* Spacing and layout for Streamlit's native components */
.st-emotion-cache-1kyx5v0 {
    gap: 0.5rem;
}

.st-emotion-cache-1f19s7 {
    padding-top: 0;
}

/* Custom styling for text content */
.stMarkdown p {
    font-size: 1.1rem;
    color: #333;
}

/* Custom table styling to match pie chart height */
.custom-table-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.custom-table {
    border-collapse: collapse;
    width: 100%;
}

.custom-table th, .custom-table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
}

.custom-table th {
    background-color: #004643;
    color: white;
    font-size: 1.2rem;
}

.custom-table td {
    font-size: 1.2rem;
}

.custom-table tr:nth-child(even) {
    background-color: #f2f2f2;
}

.custom-table tr:hover {
    background-color: #ddd;
}

.custom-table .total-row {
    font-weight: bold;
    background-color: #005f5a;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Utilization Dashboard",
    layout="wide",
    page_icon="💉"
)

# Custom styled title at the top, now with the smaller font
st.markdown(
    f"""
    <div class="main-header-container">
        <h1>📊 Vaccine Utilization Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

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
        "unacceptable": 100,  # >100%
        "acceptable": 50,      # >50% to 100%
    },
    "IPV": {
        "unacceptable": 100,  # >100%
        "acceptable": 90,      # >90% to 100%
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
available_regions = sorted(df["Region"].dropna().unique().tolist())
available_antigens = sorted(df["Antigen"].dropna().unique().tolist())

selected_period = st.sidebar.selectbox("Select Period", available_periods)

# Multi-select checkboxes for regions under an expander
with st.sidebar.expander("Select Regions"):
    all_regions_selected = st.checkbox("All Regions", value=True, key="all_regions")
    selected_regions = []
    if not all_regions_selected:
        for region in available_regions:
            if st.checkbox(region, value=False, key=f"region_{region}"):
                selected_regions.append(region)
    else:
        selected_regions = available_regions  # Select all regions if "All Regions" is checked
    if not selected_regions:
        selected_regions = available_regions  # Default to all if none selected

# Filter zones based on selected regions
available_zones = sorted(df[df["Region"].isin(selected_regions)]["Zone"].dropna().unique().tolist())

# Multi-select checkboxes for zones under an expander
with st.sidebar.expander("Select Zones"):
    all_zones_selected = st.checkbox("All Zones", value=True, key="all_zones")
    selected_zones = []
    if not all_zones_selected:
        for zone in available_zones:
            if st.checkbox(zone, value=False, key=f"zone_{zone}"):
                selected_zones.append(zone)
    else:
        selected_zones = available_zones  # Select all zones if "All Zones" is checked
    if not selected_zones:
        selected_zones = available_zones  # Default to all if none selected

selected_antigen = st.sidebar.selectbox("Select Antigen", available_antigens, index=0)

# --- Filtering ---
filtered_df = df[(df["Period"] == selected_period)].copy()

if selected_regions:
    filtered_df = filtered_df[filtered_df["Region"].isin(selected_regions)]
if selected_zones:
    filtered_df = filtered_df[filtered_df["Zone"].isin(selected_zones)]
if selected_antigen:
    filtered_df = filtered_df[filtered_df["Antigen"] == selected_antigen]

if filtered_df.empty:
    st.warning("⚠️ No data found for the selected filters. Please adjust your selections.")
    st.stop()

# --- Displaying Summary Metrics Horizontally with new styling ---
total_distributed = filtered_df["Distributed"].sum()
total_administered = filtered_df["Administered"].sum()
overall_utilization_rate = round(
    (total_administered / total_distributed * 100) if total_distributed > 0 else 0, 0
)

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Vaccines Distributed</div><div class="custom-metric-value">{total_distributed:,.0f}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Vaccines Administered</div><div class="custom-metric-value">{total_administered:,.0f}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Overall Utilization Rate</div><div class="custom-metric-value">{overall_utilization_rate:.0f}%</div></div>', unsafe_allow_html=True)
st.markdown("---")

# --- Displaying Woreda Counts by Utilization Category with new styling ---
st.subheader("Woreda Counts by Utilization Category")
col_table, col_pie = st.columns([1, 1])  # Equal width and height for table and pie chart
with col_table:
    # Calculate category counts and percentages
    category_counts = filtered_df["Utilization Category"].value_counts().reset_index()
    category_counts.columns = ["Woreda Category", "Total Counts"]
    total_woredas = category_counts["Total Counts"].sum()
    category_counts["Percentages"] = (category_counts["Total Counts"] / total_woredas * 100).round(0)  # 0 decimal places
    category_counts = category_counts[["Woreda Category", "Total Counts", "Percentages"]]  # Reorder columns
    category_counts.insert(0, "S/N", range(1, len(category_counts) + 1))  # Add S/N starting from 1
    
    # Add total summary row with corrected S/N
    total_row = pd.DataFrame({
        "S/N": [len(category_counts) + 1],
        "Woreda Category": ["Total"],
        "Total Counts": [total_woredas],
        "Percentages": [100]
    })
    category_counts = pd.concat([category_counts, total_row], ignore_index=True) # Reset index after concat
    
    # Generate HTML table from DataFrame
    def generate_html_table(df):
        html = '<div class="custom-table-container"><table class="custom-table">'
        # Table header
        html += '<thead><tr>'
        for col in df.columns:
            html += f'<th>{col}</th>'
        html += '</tr></thead>'
        # Table body
        html += '<tbody>'
        for index, row in df.iterrows():
            # Apply a special class for the total row
            row_class = 'total-row' if row['Woreda Category'] == 'Total' else ''
            html += f'<tr class="{row_class}">'
            for col in df.columns:
                # Format percentages with a '%' sign
                value = f"{row[col]:.0f}%" if col == "Percentages" else row[col]
                html += f'<td>{value}</td>'
            html += '</tr>'
        html += '</tbody></table></div>'
        return html

    st.markdown(generate_html_table(category_counts), unsafe_allow_html=True)
    
with col_pie:
    category_counts_pie = filtered_df["Utilization Category"].value_counts().reset_index()
    category_counts_pie.columns = ["Category", "Count"]
    pie_fig = px.pie(
        category_counts_pie,
        values="Count",
        names="Category",
        title="",
        hole=0.4,
        color="Category",
        color_discrete_map={"Acceptable": "green", "Unacceptable": "blue", "Low Utilization": "red"},
    )
    pie_fig.update_traces(
        textfont=dict(color="white"),
        textposition='inside',
        insidetextfont_color='white'
    )
    pie_fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        title="",
        font=dict(color='black')
    )
    st.plotly_chart(pie_fig, use_container_width=True)

st.markdown("---")

# --- Summary and Visualization Data Preparation ---
# Data for the 100% stacked bar chart, dynamically grouped by Region or Zone
if len(selected_regions) == len(available_regions):
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

# --- Charts stacked vertically, full-width ---
st.subheader(f"Utilization Breakdown by {'Region' if len(selected_regions) == len(available_regions) else 'Zone'} ({selected_antigen})")
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
    title=f"100% Stacked Utilization by {'Region' if len(selected_regions) == len(available_regions) else 'Zone'} - {selected_antigen} ({selected_period})",
    legend_title_text="Utilization Category",
    bargap=0.2,
    showlegend=True,
    # Updated legend position and orientation as requested
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)
st.plotly_chart(bar_fig, use_container_width=True)

st.markdown("---")
with st.expander("📋 Show Woreda-Level Data"):
    st.dataframe(filtered_df[[
        "Region", "Zone", "Woreda", "Antigen", "Distributed", "Administered", "Utilization Rate", "Utilization Category"
    ]].sort_values(by="Utilization Rate", ascending=False).reset_index(drop=True))