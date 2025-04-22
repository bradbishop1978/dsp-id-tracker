import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="DSP ID Tracker", page_icon="📊", layout="wide")

# Title with emoji
st.title("📊 DSP Status Report Viewer")
st.markdown("""
**Displays the full contents of the DSP Status Report:**
This will show the raw data from the `dsp_status_report.csv` file, as it is.
""")

# Load data directly from GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/bradbishop1978/dsp-id-tracker/main/dsp_status_report.csv"
    try:
        df = pd.read_csv(url)
        # Convert empty strings to NaN
        df = df.replace('', pd.NA)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

data = load_data()

if data is not None:
    # Display the raw data
    st.write("### Full DSP Status Report")
    st.dataframe(data)

    # Download button for raw data
    csv = data.to_csv(index=False)
    st.download_button(
        label="📥 Download DSP Status Report",
        data=csv,
        file_name="dsp_status_report.csv",
        mime="text/csv"
    )
else:
    st.warning("⚠️ Could not load data from GitHub. Please check the URL and try again.")

# Add some styling
st.markdown("""
<style>
    .stDataFrame {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)
