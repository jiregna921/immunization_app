# File: C:\Users\Sagni\Desktop\immunization_app\Home.py
import streamlit as st
import pandas as pd
import numpy as np
from difflib import SequenceMatcher

# --- Custom CSS for improved styling (copied from Dashboard.py) ---
st.markdown("""
<style>
/* Overall page layout and styling */
.stApp {
    padding-top: 1rem;
    background-color: #F0F2F6; /* Light gray background for better visibility */
}

/* Header styling */
.main-header-container {
    background-color: #004643;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 2rem;
}

.main-header-container h1 {
    color: white;
    margin: 0;
    text-align: center;
    font-size: 2.5rem;
}

/* Metric styling (not used here but kept for consistency) */
.metric-container {
    background-color: #E6F7FF;
    border: 1px solid #cceeff;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.metric-title {
    font-size: 1.2rem;
    font-weight: bold;
    color: #004643;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: #007bff;
}

/* Spacing and layout for metrics */
.st-emotion-cache-1kyx5v0 {
    gap: 0.5rem;
}

.st-emotion-cache-1f19s7 {
    padding-top: 0;
}

/* Custom styling for the file uploader and text */
.stMarkdown p {
    font-size: 1.1rem;
    color: #333;
}
</style>
""", unsafe_allow_html=True)

# Set the page configuration for the main page
st.set_page_config(
    page_title="Home - Data Triangulation",
    layout="centered",
    initial_sidebar_state="expanded",
    page_icon="🏠"
)

# Custom styled title at the top
st.markdown(
    f"""
    <div class="main-header-container">
        <h1>🏠 Data Triangulation and Preparation App</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("This application helps you combine two separate datasets (Distributed and Administered) into a single, clean file for analysis.")
st.markdown("---")

# --- Fuzzy Matching Helper Function ---
def fuzzy_match_and_map(df_to_map, df_target, key_col_to_map, key_col_target, threshold):
    """
    Finds the best fuzzy match for each entry in a column of df_to_map
    within a column of df_target and creates a mapping dictionary.
    Returns a dictionary of mappings and a list of unmatched items.
    """
    st.info(f"Finding best matches for '{key_col_to_map}' in '{key_col_target}' with a threshold of {threshold}%.")
    
    unique_to_map = df_to_map[key_col_to_map].dropna().unique()
    unique_target = df_target[key_col_target].dropna().unique()
    
    match_map = {}
    unmatched_items = []

    # Ensure the columns are string type for comparison
    unique_to_map = [str(item) for item in unique_to_map]
    unique_target = [str(item) for item in unique_target]

    with st.spinner("Processing fuzzy matches..."):
        for item_to_map in unique_to_map:
            best_match = None
            highest_ratio = 0
            
            # Find the best match in the target list
            for item_target in unique_target:
                # Use SequenceMatcher to calculate similarity ratio
                ratio = SequenceMatcher(None, item_to_map, item_target).ratio() * 100
                
                if ratio > highest_ratio:
                    highest_ratio = ratio
                    best_match = item_target
            
            # If the best match exceeds the threshold, add it to the map
            if highest_ratio >= threshold:
                match_map[item_to_map] = best_match
            else:
                unmatched_items.append(item_to_map)
                
    st.success(f"Fuzzy matching complete for '{key_col_to_map}'. Matches found: {len(match_map)}, unmatched: {len(unmatched_items)}.")
    
    return match_map, unmatched_items

# --- File Uploaders ---
st.subheader("1. Upload Your Datasets")
distributed_file = st.file_uploader(
    "Upload the 'Distributed' Data File (CSV or Excel)",
    type=["csv", "xlsx"],
    key="distributed_uploader"
)
administered_file = st.file_uploader(
    "Upload the 'Administered' Data File (CSV or Excel)",
    type=["csv", "xlsx"],
    key="administered_uploader"
)

# --- Merging Logic ---
if distributed_file and administered_file:
    try:
        # Read the files into pandas DataFrames
        @st.cache_data
        def load_data(uploaded_file):
            """Loads data from a CSV or Excel file."""
            if uploaded_file.name.endswith(".csv"):
                return pd.read_csv(uploaded_file)
            else:
                return pd.read_excel(uploaded_file)

        df_dist = load_data(distributed_file)
        df_admin = load_data(administered_file)

        st.success("✅ Files uploaded successfully! Now, let's configure the merging.")

        # --- Column Mapping for Merging ---
        st.subheader("2. Map Geographic and Period Columns")
        st.info("These columns will be used as the unique key to merge the two datasets.")

        # Create a list of all columns to filter from
        dist_all_cols = list(df_dist.columns)
        admin_all_cols = list(df_admin.columns)
        
        # Determine the initial default selections
        dist_geog_cols = [col for col in dist_all_cols if any(keyword in col.lower() for keyword in ['region', 'zone', 'woreda', 'city'])]
        dist_period_cols = [col for col in dist_all_cols if any(keyword in col.lower() for keyword in ['period', 'month', 'year', 'date'])]
        dist_vacc_cols = [col for col in dist_all_cols if col not in dist_geog_cols + dist_period_cols]

        admin_geog_cols = [col for col in admin_all_cols if any(keyword in col.lower() for keyword in ['region', 'zone', 'woreda', 'city'])]
        admin_period_cols = [col for col in admin_all_cols if any(keyword in col.lower() for keyword in ['period', 'month', 'year', 'date'])]
        admin_vacc_cols = [col for col in admin_all_cols if col not in admin_geog_cols + admin_period_cols]
        
        col_dist, col_admin = st.columns(2)

        with col_dist:
            st.markdown("**Distributed Data**")
            
            # Use filtered lists for each dropdown
            region_col_dist = st.selectbox("Select Region Column", dist_geog_cols, key="region_dist")
            
            # Remove the selected Region column from the options for Zone
            dist_zone_options = [col for col in dist_geog_cols if col != region_col_dist]
            zone_col_dist = st.selectbox("Select Zone Column", dist_zone_options, key="zone_dist")
            
            # Remove the selected Region and Zone columns from the options for Woreda
            dist_woreda_options = [col for col in dist_geog_cols if col not in [region_col_dist, zone_col_dist]]
            woreda_col_dist = st.selectbox("Select Woreda Column", dist_woreda_options, key="woreda_dist")

            period_col_dist = st.selectbox("Select Period Column", dist_period_cols, key="period_dist")

        with col_admin:
            st.markdown("**Administered Data**")
            
            region_col_admin = st.selectbox("Select Region Column", admin_geog_cols, key="region_admin")
            
            admin_zone_options = [col for col in admin_geog_cols if col != region_col_admin]
            zone_col_admin = st.selectbox("Select Zone Column", admin_zone_options, key="zone_admin")
            
            admin_woreda_options = [col for col in admin_geog_cols if col not in [region_col_admin, zone_col_admin]]
            woreda_col_admin = st.selectbox("Select Woreda Column", admin_woreda_options, key="woreda_admin")
            
            period_col_admin = st.selectbox("Select Period Column", admin_period_cols, key="period_admin")
            
        st.markdown("---")
        st.subheader("2.1. Set Fuzzy Matching Thresholds")
        st.info("Adjust the similarity threshold for each geographic column to account for spelling differences. A higher value requires a closer match.")

        col_reg_thresh, col_zone_thresh, col_woreda_thresh = st.columns(3)
        with col_reg_thresh:
            region_threshold = st.slider("Region Threshold (%)", 0, 100, 90)
        with col_zone_thresh:
            zone_threshold = st.slider("Zone Threshold (%)", 0, 100, 85)
        with col_woreda_thresh:
            woreda_threshold = st.slider("Woreda Threshold (%)", 0, 100, 80)


        st.markdown("---")
        st.subheader("3. Select Vaccine Count Columns")
        st.info("Select all columns that represent vaccine counts from each dataset.")
        
        # The key columns that have been selected
        excluded_dist_cols = [region_col_dist, zone_col_dist, woreda_col_dist, period_col_dist]
        excluded_admin_cols = [region_col_admin, zone_col_admin, woreda_col_admin, period_col_admin]
        
        # Filter the column lists for the multiselect boxes, ensuring key columns are excluded
        dist_vaccine_options = [col for col in df_dist.columns if col not in excluded_dist_cols]
        admin_vaccine_options = [col for col in df_admin.columns if col not in excluded_admin_cols]
        
        col_dist_vacc, col_admin_vacc = st.columns(2)
        with col_dist_vacc:
            distrib_cols = st.multiselect("Select Distributed Vaccine Columns", dist_vaccine_options, key="distrib_cols")

        with col_admin_vacc:
            admin_cols = st.multiselect("Select Administered Vaccine Columns", admin_vaccine_options, key="admin_cols")

        # --- Button to Trigger Merging ---
        if st.button("Merge Datasets"):
            try:
                # Add validation to prevent selecting the same column as a key and a vaccine count
                if not distrib_cols or not admin_cols:
                    st.warning("Please select at least one vaccine count column from each dataset.")
                    st.stop()

                with st.spinner("Merging and processing data..."):
                    # Create mapping dictionaries for geographic and period columns
                    dist_rename_map = {
                        region_col_dist: "Region",
                        zone_col_dist: "Zone",
                        woreda_col_dist: "Woreda",
                        period_col_dist: "Period"
                    }
                    admin_rename_map = {
                        region_col_admin: "Region",
                        zone_col_admin: "Zone",
                        woreda_col_admin: "Woreda",
                        period_col_admin: "Period"
                    }
                    
                    # Create clean dataframes with standardized column names
                    df_dist_clean = df_dist[list(dist_rename_map.keys())].rename(columns=dist_rename_map)
                    df_admin_clean = df_admin[list(admin_rename_map.keys())].rename(columns=admin_rename_map)
                    
                    # Add vaccine count columns
                    df_dist_clean = df_dist_clean.assign(**{col: df_dist[col] for col in distrib_cols})
                    df_admin_clean = df_admin_clean.assign(**{col: df_admin[col] for col in admin_cols})
                    
                    # Keep a copy of the original Woreda column for comparison after mapping
                    df_admin_clean['Original_Woreda'] = df_admin_clean['Woreda']

                    # Apply fuzzy matching to the geographic columns
                    region_map, _ = fuzzy_match_and_map(df_admin_clean, df_dist_clean, "Region", "Region", region_threshold)
                    zone_map, _ = fuzzy_match_and_map(df_admin_clean, df_dist_clean, "Zone", "Zone", zone_threshold)
                    woreda_map, unmatched_woredas_list = fuzzy_match_and_map(df_admin_clean, df_dist_clean, "Woreda", "Woreda", woreda_threshold)
                    
                    # Identify unmatched Woredas from the administered data
                    unmatched_woredas_df = df_admin_clean[df_admin_clean['Woreda'].isin(unmatched_woredas_list)].reset_index(drop=True)
                    
                    # Apply the maps to the administered dataframe before merging
                    df_admin_clean["Region"] = df_admin_clean["Region"].map(region_map).fillna(df_admin_clean["Region"])
                    df_admin_clean["Zone"] = df_admin_clean["Zone"].map(zone_map).fillna(df_admin_clean["Zone"])
                    df_admin_clean["Woreda"] = df_admin_clean["Woreda"].map(woreda_map).fillna(df_admin_clean["Woreda"])

                    # Merge the dataframes on the common columns
                    merged_df = pd.merge(
                        df_dist_clean, 
                        df_admin_clean.drop(columns=['Original_Woreda']), 
                        on=["Period", "Region", "Zone", "Woreda"],
                        how="outer"
                    )

                    # Now, combine the vaccine columns.
                    for col in distrib_cols:
                        if col in merged_df.columns:
                            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce').fillna(0)
                        else:
                            merged_df[col] = pd.to_numeric(df_dist_clean[col], errors='coerce').fillna(0)
                    for col in admin_cols:
                        if col in merged_df.columns:
                            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce').fillna(0)
                        else:
                            merged_df[col] = pd.to_numeric(df_admin_clean[col], errors='coerce').fillna(0)
                        
                    # Store the merged dataframe in session state
                    st.session_state["immunization_data"] = merged_df

                st.success("🎉 Data merged successfully! You can now navigate to the dashboard.")
                
                # Show a preview of the merged data
                st.subheader("Preview of Merged Data")
                st.dataframe(merged_df.head())
                st.write(f"Final merged dataset has {merged_df.shape[0]} rows and {merged_df.shape[1]} columns.")
                
                # Display unmatched woredas if any exist
                if not unmatched_woredas_df.empty:
                    st.markdown("---")
                    st.subheader("⚠️ Unmatched Woredas Found")
                    st.warning(f"There were {len(unmatched_woredas_df['Woreda'].unique())} Woredas in the Administered dataset that did not find a match above the {woreda_threshold}% threshold.")
                    with st.expander("Show Unmatched Woredas"):
                        st.dataframe(unmatched_woredas_df[['Woreda']].drop_duplicates())
                        
                        # Create a download button for the unmatched data
                        csv_data = unmatched_woredas_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Unmatched Woredas as CSV",
                            data=csv_data,
                            file_name='unmatched_woredas.csv',
                            mime='text/csv'
                        )
                else:
                    st.success("✅ All Woredas were matched successfully!")
            
            except Exception as e:
                st.error(f"An error occurred during merging: {e}")

    except Exception as e:
        st.error(f"Error loading the files. Please ensure they are valid CSV or Excel formats. Error: {e}")

else:
    st.info("Please upload both data files to begin.")
