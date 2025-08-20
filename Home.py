import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit_authenticator as stauth

# --- USER AUTHENTICATION ---
# This app now uses Streamlit's built-in secrets management for security.
# The credentials are read from the `secrets.toml` file configured in Streamlit Cloud.

authenticator = stauth.Authenticate(
    st.secrets['credentials'],
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login', 'main')

# --- Main App Logic (executed only after successful login) ---
if authentication_status:
    authenticator.logout('Logout', 'main')

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

    # Custom styled title at the top with a logo
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image("logo.png", width=100)

    with col_title:
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
            "unacceptable": 100,
            "acceptable": 50,
        },
        "IPV": {
            "unacceptable": 100,
            "acceptable": 90,
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
        "Default": {
            "unacceptable": 100,
            "acceptable": 65,
        }
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
        antigens = [col.replace(' Distrib', '') for col in distrib_cols]

        all_antigen_cols = distrib_cols + admin_cols
        id_vars = [col for col in data_processed.columns if col not in all_antigen_cols]

        df_long = pd.melt(data_processed,
                          id_vars=id_vars,
                          value_vars=all_antigen_cols,
                          var_name='AntigenType',
                          value_name='Count')

        df_long['Antigen'] = df_long['AntigenType'].apply(lambda x: x.split(' ')[0])
        df_long['Type'] = df_long['AntigenType'].apply(lambda x: 'Distributed' if 'Distrib' in x else 'Administered')
        
        df_pivot = df_long.pivot_table(index=id_vars + ['Antigen'],
                                       columns='Type',
                                       values='Count').reset_index()
        
        df_pivot.columns.name = None
        df_pivot = df_pivot.rename(columns={'Distributed': 'Distributed', 'Administered': 'Administered'})
        df_pivot["Distributed"] = pd.to_numeric(df_pivot["Distributed"], errors="coerce").fillna(0)
        df_pivot["Administered"] = pd.to_numeric(df_pivot["Administered"], errors="coerce").fillna(0)
        
        df_pivot["Utilization Rate"] = df_pivot.apply(
            lambda row: round((row["Administered"] / row["Distributed"] * 100), 0) if row["Distributed"] > 0 else 0,
            axis=1
        )
        df_pivot["Utilization Category"] = df_pivot.apply(categorize_utilization, axis=1)
        
        return df_pivot

    df = prepare_data(st.session_state["immunization_data"].copy())

    # --- Sidebar Filters
