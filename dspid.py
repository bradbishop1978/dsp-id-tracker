import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Set page config
st.set_page_config(page_title="DSP ID Tracker", page_icon="📊", layout="wide")

# Title with emoji
st.title("📊 DSP Status Report Viewer")
st.markdown("""
**Displays the full contents of the DSP Status Report:**
This will show the raw data from the `dsp_status_report.csv` file, as it is.
""")

# Add auto-refresh options in the sidebar
st.sidebar.title("Refresh Settings")
refresh_interval = st.sidebar.selectbox(
    "Auto-refresh interval",
    [None, 10, 30, 60, 120, 300],
    format_func=lambda x: "Disabled" if x is None else f"Every {x} seconds"
)

# Display last refresh time
last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
refresh_text = st.sidebar.empty()
refresh_text.info(f"Last refreshed: {last_refresh}")

# Manual refresh button
if st.sidebar.button("🔄 Refresh Data Now"):
    st.experimental_rerun()

# Load data with TTL (Time To Live) cache
@st.cache_data(ttl=300)  # Cache expires after 5 minutes
def load_data():
    url = "https://raw.githubusercontent.com/bradbishop1978/dsp-id-tracker/main/dsp_status_report.csv"
    try:
        df = pd.read_csv(url)
        # Convert empty strings to NaN
        df = df.replace('', pd.NA)
        # Replace "missing" and NaN with ***
        df = df.replace("Missing", "***").fillna("***")
        # Format "ID Present" to green italic using HTML
        df = df.replace("ID Present", "<span style='color:green; font-style:italic;'>ID Present</span>")
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
        # This will only apply to actual numerical values (int or float)
        if isinstance(val, (int, float)) and not pd.isna(val):
            return 'color: green; font-weight: bold;'
        return ''
    
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
        max-height: 400px;
        overflow-y: auto;
    }
    /* Sticky header */
    .stDataFrame thead {
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 10;
    }
    .stDataFrame tbody tr:nth-child(odd) {
        background-color: #f9f9f9;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #ffffff;
    }
    .stDataFrame td, .stDataFrame th {
        padding: 8px 12px;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

# Auto-refresh functionality
if refresh_interval:
    time.sleep(1)  # Small delay to ensure UI renders first
    refresh_progress = st.sidebar.progress(0)
    for i in range(refresh_interval):
        # Update progress bar
        progress_val = i / refresh_interval
        refresh_progress.progress(progress_val)
        time.sleep(1)
    
    # Rerun the app when the timer completes
    st.experimental_rerun()
