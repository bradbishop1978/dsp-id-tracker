import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="DSP ID Tracker", page_icon="📊", layout="wide")

# Title with emoji
st.title("📊 DSP Status Report Viewer")
st.markdown("""
**Displays the DSP Status Report:**
This will show the stores with clickable names, their DSP IDs status, and onboarding status.
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
    
    # Drop 'store_id' and 'store_name' columns
    data = data.drop(columns=['store_id', 'store_name'])

    # Replace NaN values with "missing"
    data = data.fillna('missing')

    # Sort by 'company_name'
    data = data.sort_values(by='company_name')

    # Reorder columns to match the requested order
    column_order = ['company_name', 'Store', 'ubereats_status', 'doordash_status', 'grubhub_status', 'onboarding_status']
    
    # Filter columns that exist in the dataframe
    column_order = [col for col in column_order if col in data.columns]

    # Apply styles to numeric values (make them green and bold)
    def style_numeric(val):
        if isinstance(val, (int, float)):
            return 'font-weight: bold; color: green'
        return ''

    # Display the filtered and styled data
    st.write("### DSP Status Report")

    # Style numeric columns and display the data as a table
    styled_data = data[column_order].style.applymap(style_numeric, subset=['ubereats_status', 'doordash_status', 'grubhub_status'])

    # Display the styled dataframe
    st.dataframe(styled_data)

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

# Add some custom styling
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
