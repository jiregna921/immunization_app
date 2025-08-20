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
    background-color: #e6f4f1; /* Light green background for better visibility */
}

/* Header styling - now with reduced font size */
.main-header-container {
    background-color: #004643;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 0.25rem;
}

.main-header-container h1 {
    color: white;
    margin: 0;
    text-align: center;
    font-size: 1.5rem;
}

/* Custom metric styling */
.custom-metric-box {
    background-color: #004643;
    padding: 0.5rem;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.custom-metric-label {
    font-size: 1rem;
    font-weight: bold;
    color: white;
    margin-bottom: 0.25rem;
}

.custom-metric-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
}

/* Spacing for Streamlit native components */
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

/* Reduce space between sections */
.stMarkdown hr {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Utilization Dashboard", 
    layout="wide",
    page_icon="💉"
)

# --- Title ---
st.markdown(
    f"""
    <div class="main-header-container">
        <h1>📊 Vaccine Utilization Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Load data ---
if "immunization_data" not in st.session_state:
    st.info("No dataset found. A sample dataset has been loaded for demonstration.")
    dummy_data = {
        "Period": ["2023-Q4"]*6,
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

# --- Thresholds ---
VACCINE_THRESHOLDS = {
    "BCG": {"unacceptable": 100, "acceptable": 50},
    "IPV": {"unacceptable": 100, "acceptable": 90},
    "Measles": {"unacceptable": 100, "acceptable": 65},
    "Penta": {"unacceptable": 100, "acceptable": 95},
    "Rota": {"unacceptable": 100, "acceptable": 90},
    "Default": {"unacceptable": 100, "acceptable": 65}
}

def categorize_utilization(row):
    rate = row["Utilization Rate"]
    antigen = row["Antigen"]
    thresholds = VACCINE_THRESHOLDS.get(antigen, VACCINE_THRESHOLDS["Default"])
    if rate > thresholds["unacceptable"]:
        return "Unacceptable"
    elif rate >= thresholds["acceptable"]:
        return "Acceptable"
    else:
        return "Low Utilization"

@st.cache_data
def prepare_data(data):
    data_processed = data.copy()
    distrib_cols = [col for col in data_processed.columns if 'Distrib' in str(col)]
    admin_cols = [col for col in data_processed.columns if 'Admin' in str(col)]
    all_antigen_cols = distrib_cols + admin_cols
    id_vars = [col for col in data_processed.columns if col not in all_antigen_cols]

    df_long = pd.melt(data_processed, id_vars=id_vars, value_vars=all_antigen_cols,
                      var_name='AntigenType', value_name='Count')
    df_long['Antigen'] = df_long['AntigenType'].apply(lambda x: x.split(' ')[0])
    df_long['Type'] = df_long['AntigenType'].apply(lambda x: 'Distributed' if 'Distrib' in x else 'Administered')

    df_pivot = df_long.pivot_table(index=id_vars + ['Antigen'], columns='Type', values='Count').reset_index()
    df_pivot.columns.name = None
    df_pivot["Distributed"] = pd.to_numeric(df_pivot["Distributed"], errors="coerce").fillna(0)
    df_pivot["Administered"] = pd.to_numeric(df_pivot["Administered"], errors="coerce").fillna(0)
    df_pivot["Utilization Rate"] = df_pivot.apply(
        lambda row: round((row["Administered"] / row["Distributed"] * 100), 0) if row["Distributed"] > 0 else 0,
        axis=1
    )
    df_pivot["Utilization Category"] = df_pivot.apply(categorize_utilization, axis=1)
    return df_pivot

df = prepare_data(st.session_state["immunization_data"].copy())

# --- Sidebar filters ---
st.sidebar.header("🧪 Filter Data")
available_periods = sorted(df["Period"].unique().tolist(), reverse=True)
available_regions = sorted(df["Region"].dropna().unique().tolist())
available_antigens = sorted(df["Antigen"].dropna().unique().tolist())
selected_period = st.sidebar.selectbox("Select Period", available_periods)

with st.sidebar.expander("Select Regions"):
    all_regions_selected = st.checkbox("All Regions", value=True, key="all_regions")
    selected_regions = available_regions if all_regions_selected else [r for r in available_regions if st.checkbox(r, value=False, key=f"region_{r}")]
    if not selected_regions:
        selected_regions = available_regions

available_zones = sorted(df[df["Region"].isin(selected_regions)]["Zone"].dropna().unique().tolist())
with st.sidebar.expander("Select Zones"):
    all_zones_selected = st.checkbox("All Zones", value=True, key="all_zones")
    selected_zones = available_zones if all_zones_selected else [z for z in available_zones if st.checkbox(z, value=False, key=f"zone_{z}")]
    if not selected_zones:
        selected_zones = available_zones

selected_antigen = st.sidebar.selectbox("Select Antigen", available_antigens, index=0)

# --- Filtering ---
filtered_df = df[(df["Period"] == selected_period) & df["Region"].isin(selected_regions) & df["Zone"].isin(selected_zones) & (df["Antigen"] == selected_antigen)]
if filtered_df.empty:
    st.warning("⚠️ No data found for the selected filters.")
    st.stop()

# --- Summary metrics ---
total_distributed = filtered_df["Distributed"].sum()
total_administered = filtered_df["Administered"].sum()
overall_utilization_rate = round((total_administered / total_distributed * 100) if total_distributed > 0 else 0, 0)
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Vaccines Distributed</div><div class="custom-metric-value">{total_distributed:,.0f}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Vaccines Administered</div><div class="custom-metric-value">{total_administered:,.0f}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Overall Utilization Rate</div><div class="custom-metric-value">{overall_utilization_rate:.0f}%</div></div>', unsafe_allow_html=True)
st.markdown("---")

# --- Woreda Counts ---
total_woredas = len(filtered_df["Woreda"].unique())
category_counts = filtered_df["Utilization Category"].value_counts()
st.subheader("Woreda Counts by Utilization Category")
col_w1, col_w2, col_w3, col_w4 = st.columns(4)
with col_w1:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Total Woredas</div><div class="custom-metric-value">{total_woredas:,.0f}</div></div>', unsafe_allow_html=True)
with col_w2:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Acceptable</div><div class="custom-metric-value">{category_counts.get("Acceptable", 0):,.0f}</div></div>', unsafe_allow_html=True)
with col_w3:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Unacceptable</div><div class="custom-metric-value">{category_counts.get("Unacceptable", 0):,.0f}</div></div>', unsafe_allow_html=True)
with col_w4:
    st.markdown(f'<div class="custom-metric-box"><div class="custom-metric-label">Low Utilization</div><div class="custom-metric-value">{category_counts.get("Low Utilization", 0):,.0f}</div></div>', unsafe_allow_html=True)
st.markdown("---")

# --- Pie chart + Woreda category table ---
st.subheader("Overall Utilization Breakdown")
category_counts_pie = filtered_df["Utilization Category"].value_counts().reset_index()
category_counts_pie.columns = ["Category", "Count"]
category_counts_pie["Percentage"] = (category_counts_pie["Count"] / category_counts_pie["Count"].sum() * 100).round(0)
category_counts_pie.reset_index(drop=True, inplace=True)

col_text, col_pie = st.columns([1, 2])
with col_text:
    breakdown_html = """
<div class="custom-metric-box">
    <div style="text-align: center; color: white; font-size: 1.2rem; margin-bottom: 0.25rem;">Total Woredas {0}</div>
    <div style="text-align: center; color: white; font-size: 1.2rem; margin-bottom: 0.25rem;">Acceptable {1}</div>
    <div style="text-align: center; color: white; font-size: 1.2rem; margin-bottom: 0.25rem;">Unacceptable {2}</div>
    <div style="text-align: center; color: white; font-size: 1.2rem; margin-bottom: 0.25rem;">Low Utilization {3}</div>
</div>
    """.format(
        f"{total_woredas:,.0f}",
        f"{category_counts.get('Acceptable', 0):,.0f}",
        f"{category_counts.get('Unacceptable', 0):,.0f}",
        f"{category_counts.get('Low Utilization', 0):,.0f}"
    )
    st.markdown(breakdown_html, unsafe_allow_html=True)
with col_pie:
    color_map = {"Acceptable": "green", "Unacceptable": "blue", "Low Utilization": "red"}
    pie_fig = px.pie(category_counts_pie.reset_index(), values="Count", names="Category", hole=0.0, color="Category", color_discrete_map=color_map)
    pie_fig.update_traces(textinfo='percent', textfont=dict(color="white"), textposition='inside')
    pie_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title="", font=dict(color='black'), height=350)
    st.plotly_chart(pie_fig, use_container_width=True)

st.markdown("---")

# --- Bar chart ---
groupby_col = "Region" if len(selected_regions) == len(available_regions) else "Zone"
stacked_bar_data = filtered_df.groupby([groupby_col, "Utilization Category"]).size().reset_index(name='Count')
total_by_group = stacked_bar_data.groupby(groupby_col)["Count"].sum().reset_index(name='Total')
stacked_bar_data = stacked_bar_data.merge(total_by_group, on=groupby_col)
stacked_bar_data["Percentage"] = (stacked_bar_data["Count"] / stacked_bar_data["Total"] * 100).round(0)
bar_fig = go.Figure()
for category in ["Acceptable", "Low Utilization", "Unacceptable"]:
    f_data = stacked_bar_data[stacked_bar_data["Utilization Category"] == category]
    bar_fig.add_trace(go.Bar(x=f_data[groupby_col], y=f_data["Percentage"], name=category, marker_color=color_map[category],
                             text=f_data["Percentage"], textposition='inside', insidetextanchor='middle', texttemplate='%{y:.0f}%',
                             hovertemplate=f"<b>%{{x}}</b><br>{category}: %{{y:.0f}}%<br>District Count: %{{customdata}}<extra></extra>",
                             customdata=f_data['Count']))
bar_fig.update_layout(barmode="stack", yaxis=dict(title="Percentage (%)", range=[0, 100], tickformat=".0f"),
                      xaxis=dict(title=groupby_col, tickangle=-45),
                      title=f"100% Stacked Utilization by {groupby_col} - {selected_antigen} ({selected_period})",
                      legend_title_text="Utilization Category", bargap=0.2,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                      height=600)
st.plotly_chart(bar_fig, use_container_width=True)

st.markdown("---")
with st.expander("📋 Show Woreda-Level Data"):
    st.dataframe(filtered_df[["Region", "Zone", "Woreda", "Antigen", "Distributed", "Administered", "Utilization Rate", "Utilization Category"]]
                 .sort_values(by="Utilization Rate", ascending=False).reset_index(drop=True))
