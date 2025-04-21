import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="DSP ID Tracker", page_icon="📊", layout="wide")

# Title with emoji
st.title("📊 DSP ID Tracker")
st.markdown("""
**Displays stores with:**
- Missing DSP IDs (UberEats, DoorDash, Grubhub)
- Blank store_status
- Pipeline Stage = 'Pending Launch'
- Onboarding Status = 'Inprogress'
""")

# Load data directly from GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/bradbishop1978/dsp-id-tracker/main/dsp_id.csv"
    try:
        df = pd.read_csv(url)
        # Ensure empty strings are treated as NaN
        df.replace('', pd.NA, inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

data = load_data()

if data is not None:
    # Apply filters
    filtered_data = data[
        (data['ubereats_id'].isna()) &
        (data['doordash_id'].isna()) &
        (data['grubhub_id'].isna()) &
        (data['store_status'].isna()) &
        (data['pipeline_stage'].str.lower() == 'pending launch') &
        (data['onboarding_status'].str.lower() == 'inprogress')
    ].copy()

    # Display results
    if not filtered_data.empty:
        st.success(f"🔍 Found {len(filtered_data)} stores matching criteria")
        
        # Create clickable store names
        filtered_data['Store'] = filtered_data.apply(
            lambda x: f'<a href="https://www.lulastoremanager.com/stores/{x["store_id"]}" target="_blank">{x["store_name"]}</a>', 
            axis=1
        )
        
        # Create missing DSP IDs summary
        filtered_data['Missing DSPs'] = "All (UE, DD, GH)"
        
        # Select and order columns for display
        display_cols = [
            'Store', 'company_name', 'Missing DSPs', 
            'pipeline_stage', 'onboarding_status', 'store_status',
            'store_email', 'store_phone'
        ]
        
        # Filter to only columns that exist in the data
        display_cols = [col for col in display_cols if col in filtered_data.columns]
        
        # Display as HTML to render links
        st.write(
            filtered_data[display_cols]
            .sort_values('store_name')
            .to_html(escape=False, index=False), 
            unsafe_allow_html=True
        )
        
        # Download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="missing_dsp_stores.csv",
            mime="text/csv"
        )
        
        # Metrics summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Matching Stores", len(filtered_data))
        with col2:
            st.metric("Companies", filtered_data['company_name'].nunique())
        with col3:
            st.metric("Pending Launch", len(filtered_data))
        
    else:
        st.info("🎉 No stores match all the specified criteria - great job!")
        
    # Raw data toggle
    with st.expander("🔍 View Raw Data"):
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