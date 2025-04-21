import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="DSP ID Tracker", page_icon="📊", layout="wide")

# Title with emoji
st.title("📊 Missing DSP ID Tracker")
st.markdown("""
**Displays stores that are:**
1. In **Pending Launch** pipeline stage
2. With **In progress** onboarding status
3. Missing **any** DSP IDs (UberEats, DoorDash, or Grubhub)
""")

# Load data directly from GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/bradbishop1978/dsp-id-tracker/main/dsp_id.csv"
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
    # Convert text to lowercase for consistent comparison
    data['pipeline_stage'] = data['pipeline_stage'].str.lower()
    data['onboarding_status'] = data['onboarding_status'].str.lower()
    
    # Apply filters
    filtered_data = data[
        (data['pipeline_stage'] == 'pending launch') &
        (data['onboarding_status'] == 'in progress') &
        (data['ubereats_id'].isna() | 
         data['doordash_id'].isna() | 
         data['grubhub_id'].isna())
    ].copy()
    
    # Create a column showing which DSP IDs are missing
    def get_missing_dsps(row):
        missing = []
        if pd.isna(row['ubereats_id']):
            missing.append('UberEats')
        if pd.isna(row['doordash_id']):
            missing.append('DoorDash')
        if pd.isna(row['grubhub_id']):
            missing.append('Grubhub')
        return ', '.join(missing) if missing else 'None'
    
    filtered_data['Missing DSPs'] = filtered_data.apply(get_missing_dsps, axis=1)
    
    # Create clickable store names
    filtered_data['Store'] = filtered_data.apply(
        lambda x: f'<a href="https://www.lulastoremanager.com/stores/{x["store_id"]}" target="_blank">{x["store_name"]}</a>', 
        axis=1
    )
    
    # Display results
    if not filtered_data.empty:
        st.success(f"🔍 Found {len(filtered_data)} stores missing DSP IDs")
        
        # Select columns to display
        display_cols = [
            'Store', 'company_name', 'Missing DSPs',
            'ubereats_id', 'doordash_id', 'grubhub_id',
            'pipeline_stage', 'onboarding_status', 'store_status'
        ]
        
        # Filter to only columns that exist in the data
        display_cols = [col for col in display_cols if col in filtered_data.columns]
        
        # Display as HTML table to render links
        st.write(
            filtered_data[display_cols]
            .sort_values('store_name')
            .to_html(escape=False, index=False), 
            unsafe_allow_html=True
        )
        
        # Download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Missing DSP Stores",
            data=csv,
            file_name="missing_dsp_stores.csv",
            mime="text/csv"
        )
        
        # Show summary metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Stores", len(filtered_data))
        col2.metric("Unique Companies", filtered_data['company_name'].nunique())
        
        # Count of missing each DSP
        missing_ue = len(filtered_data[filtered_data['ubereats_id'].isna()])
        missing_dd = len(filtered_data[filtered_data['doordash_id'].isna()])
        missing_gh = len(filtered_data[filtered_data['grubhub_id'].isna()])
        
        col3.metric("Missing UberEats", missing_ue)
        st.write(f"Missing DoorDash: {missing_dd} | Missing Grubhub: {missing_gh}")
        
    else:
        st.info("🎉 All stores have complete DSP IDs - great job!")
        
    # Raw data toggle
    with st.expander("🔍 View All Raw Data"):
        st.dataframe(data)
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
