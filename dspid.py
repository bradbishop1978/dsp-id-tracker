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
    # Create clickable store names by appending the store ID to the URL
    data['Store'] = data.apply(
        lambda x: f'<a href="https://www.lulastoremanager.com/stores/{x["store_id"]}" target="_blank">{x.get("store_name", "Unnamed Store")}</a>', 
        axis=1
    )
    
    # Rearrange columns as requested
    column_order = ['company_name', 'Store', 'ubereats_status', 'doordash_status', 'grubhub_status', 'onboarding_status']
    
    # Ensure all columns are in the correct order and exist in the data
    column_order = [col for col in column_order if col in data.columns]
    
    # Apply styling for numerical values to be green and bold
    def style_numeric(val):
        # This will make the numerical values green and bold
        return 'color: green; font-weight: bold;' if isinstance(val, (int, float)) else ''

    # Apply the style to the relevant columns
    styled_data = data[column_order].style.applymap(style_numeric, subset=['ubereats_status', 'doordash_status', 'grubhub_status'])
    
    # Display the raw data with clickable store names in the new order
    st.write("### Full DSP Status Report")
    st.write(
        styled_data.to_html(escape=False, index=False),  # Render the HTML link correctly
        unsafe_allow_html=True
    )

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
    a {
        text-decoration: none;
        color: #0068c9;
    }
    a:hover {
        text-decoration: underline;
    }
    .stDataFrame {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)
