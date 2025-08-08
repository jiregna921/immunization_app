import streamlit as st
from utils.data_loader import load_dataset
from utils.calculator import calculate_utilization_and_category

st.set_page_config(page_title="Immunization Data Triangulation", layout="wide")
st.title("📥 Immunization Data Upload")

# File upload
uploaded_file = st.file_uploader("Upload merged dataset (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    st.session_state["uploaded_file"] = uploaded_file  # Save file in session
    df = load_dataset(uploaded_file)
    processed_df = calculate_utilization_and_category(df)
    st.session_state["processed_df"] = processed_df    # Save processed data in session

    st.success("✅ File uploaded and processed successfully!")

    st.subheader("Preview of Processed Data")
    st.dataframe(processed_df)

    st.download_button(
        label="📥 Download Processed Data",
        data=processed_df.to_csv(index=False),
        file_name="processed_dataset.csv",
        mime="text/csv"
    )
else:
    st.info("👈 Please upload a dataset file to begin.")
