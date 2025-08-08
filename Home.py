import streamlit as st
import pandas as pd

# Custom CSS for a more attractive page
st.markdown(
    """
    <style>
    body {
        font-family: Arial, sans-serif;
    }
    
    /* Overall page layout and styling */
    .stApp {
        padding-top: 1rem;
        background-color: #F0F2F6; /* Light gray background for better visibility */
    }

    /* Styling for the combined logo and title header */
    .main-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        gap: 1.5rem;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
    }
    
    /* Styling for the title's colored background */
    .header-container {
        display: flex;
        align-items: center;
        background-color: #064E3B; /* A dark green for the title background */
        padding: 1rem;
        color: white;
        border-radius: 10px;
        flex-grow: 1;
        min-height: 80px;
    }
    .header-container h1 {
        color: white;
        margin: 0;
        white-space: nowrap;
        font-size: 2.5rem; /* Increased font size */
    }
    
    /* Styling for the body text, file uploader, and info messages */
    .stMarkdown p {
        font-size: 1.3rem; /* Increased font size for better readability */
        color: #333;
    }

    /* Styling for the file uploader box */
    .st-emotion-cache-1kyx5v0 {
        border: 2px dashed #D3D3D3;
        border-radius: 8px;
        background-color: #F8F8F8;
    }
    .st-emotion-cache-16p7j11 {
        color: #555;
    }
    /* Styling for the info messages */
    .st-emotion-cache-1s0z72r {
        background-color: #E6F7FF;
        border-left: 5px solid #0099E6;
        color: #0099E6;
        border-radius: 4px;
        padding: 10px;
        font-size: 1.2rem; /* Increased font size for info message */
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(
    page_title="Home",
    layout="wide", # Sets the page to full width
    initial_sidebar_state="auto"
)

# --- Header with logo and title ---
# The logo is in the 'logo' folder relative to the app's root directory.
# Replace 'logo.png' with your actual logo file name.
st.markdown(
    f"""
    <div class="main-header">
        <div class="logo-container">
            <img src="logo/logo.png" width="100">
        </div>
        <div class="header-container">
            <h1>Web based Immunization Data Triangulation Application</h1>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("""
Welcome to the Vaccine Utilization Dashboard.

Please upload your immunization data file below. The data will be available for all pages.
""")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Store the raw DataFrame in session state
        st.session_state["immunization_data"] = df
        st.success("✅ Data uploaded successfully! Please navigate to the dashboard page.")
        
        with st.expander("Preview of the uploaded data"):
            st.dataframe(df.head())

    except Exception as e:
        st.error(f"❌ An error occurred while reading the file: {e}")
else:
    st.info("Awaiting file upload...")
