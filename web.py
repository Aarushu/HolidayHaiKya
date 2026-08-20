import streamlit as st
import weather_engine

st.set_page_config(
    page_title="Dehradun Weather Notice",
    page_icon="⛈️",
    layout="centered"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
    
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Make the metrics look a bit bolder */
    div[data-testid="stMetricValue"] {
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)


st.title("Dehradun Weather Risk & DM Holiday Notice")


if st.button("↻ Refresh Data", type="primary"):
    with st.spinner("Fetching meteorological data and local feeds..."):
        
      
        alert_level, warning_desc = weather_engine.fetch_accurate_imd_pdf_warning()
        total_mm, max_mm_hr = weather_engine.fetch_openmeteo_precipitation()
        news_feed, dm_order_found = weather_engine.scrape_dm_and_news_updates()
        
        if "RED" in alert_level or total_mm > 65.0:
            base_prob = 90
        elif "ORANGE" in alert_level or total_mm > 35.0:
            base_prob = 65
        elif "YELLOW" in alert_level or total_mm > 10.0:
            base_prob = 30
        else:
            base_prob = 5
            
        final_prob = 98 if dm_order_found else base_prob
        dm_status = "CONFIRMED ORDER DETECTED" if dm_order_found else "No Explicit Order Yet"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Meteorological Data")
            st.metric(label="Expected Rain (Next 24h)", value=f"{total_mm} mm")
            st.metric(label="Max Intensity", value=f"{max_mm_hr} mm/hr")
            st.info(f"**Alert Level:** {alert_level}\n\n{warning_desc}")
            
        with col2:
            st.subheader("Holiday Prediction Engine")
            st.metric(label="Holiday Chance", value=f"{final_prob}%")
            if dm_order_found:
                st.success(f"**DM Circular:** {dm_status}")
            else:
                st.warning(f"**DM Circular:** {dm_status}")
            
        st.divider()
        
        st.subheader("Live Scraped DM Announcements & News")
        st.code(news_feed, language="text")
        
else:
   
    st.info("Click 'Refresh Data' to load the latest Dehradun forecast and news.")