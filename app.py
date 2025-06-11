import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pyathena import connect
from utils import (
    calculate_metrics,
    display_kpi_cards,
    create_download_button,
    plot_top_campaigns,
    plot_trend,
    plot_pie_chart
)
from campaign_summary import render_campaign_summary
from campaign_performance import render_campaign_performance
from creative_performance import render_creative_performance

# Set page config
st.set_page_config(
    page_title="AdTech Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize Athena connection
@st.cache_resource
def get_athena_connection():
    return connect(
        s3_staging_dir='s3://adtech-reporting-data/athena_processed/',
        region_name='us-east-1'
    )

# Cache data loading
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(query):
    conn = get_athena_connection()
    return pd.read_sql(query, conn)

def get_common_filters():
    """Get common filters for all dashboards"""
    filters = {}
    
    # Date range filter
    min_date = datetime(2023, 1, 1)  # Adjust based on your data
    max_date = datetime.now()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    filters['date_range'] = date_range
    
    # Get unique values for filters, excluding unknown values
    countries_query = """
        SELECT DISTINCT country 
        FROM adtech_db.campaign_performance 
        WHERE country IS NOT NULL 
        AND country != 'Unknown'
    """
    campaigns_query = """
        SELECT DISTINCT campaign_id 
        FROM adtech_db.campaign_performance 
        WHERE campaign_id IS NOT NULL 
        AND campaign_id != 'unknown_campaign'
    """
    brands_query = """
        SELECT DISTINCT brand 
        FROM adtech_db.campaign_performance 
        WHERE brand IS NOT NULL 
        AND brand != 'Unknown'
    """
    
    countries = ['All'] + sorted(load_data(countries_query)['country'].tolist())
    campaigns = ['All'] + sorted(load_data(campaigns_query)['campaign_id'].tolist())
    brands = ['All'] + sorted(load_data(brands_query)['brand'].tolist())
    
    # Brand filter
    selected_brands = st.sidebar.multiselect(
        "Select Brands",
        options=brands,
        default=brands[:1] if brands else []
    )
    filters['brand'] = selected_brands
    
    # Campaign filter
    selected_campaigns = st.sidebar.multiselect(
        "Select Campaigns",
        options=campaigns,
        default=campaigns[:1] if campaigns else []
    )
    filters['campaign_id'] = selected_campaigns
    
    # Country filter
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        options=countries,
        default=countries[:1] if countries else []
    )
    filters['country'] = selected_countries
    
    return filters

def build_where_clause(filters, include_ad_id=False):
    """Build WHERE clause for Athena queries"""
    conditions = []
    
    # Base conditions to exclude unknown values
    conditions.extend([
        "campaign_id != 'unknown_campaign'",
        "date IS NOT NULL",
        "brand != 'Unknown'",
        "country != 'Unknown'",
        "state != 'Unknown'",
        "city != 'Unknown'",
        "zipcode != '000000'"
    ])
    
    # Add ad_id condition only for creative performance
    if include_ad_id:
        conditions.append("ad_id != 'unknown_ad'")
    
    if filters.get('date_range'):
        start_date, end_date = filters['date_range']
        conditions.append(f"date >= DATE('{start_date}')")
        conditions.append(f"date <= DATE('{end_date}')")
    
    if filters.get('brand') and 'All' not in filters['brand']:
        brands_str = "', '".join(filters['brand'])
        conditions.append(f"brand IN ('{brands_str}')")
    
    if filters.get('campaign_id') and 'All' not in filters['campaign_id']:
        campaigns_str = "', '".join(filters['campaign_id'])
        conditions.append(f"campaign_id IN ('{campaigns_str}')")
    
    if filters.get('country') and 'All' not in filters['country']:
        countries_str = "', '".join(filters['country'])
        conditions.append(f"country IN ('{countries_str}')")
    
    return " AND ".join(conditions) if conditions else "1=1"

def main():
    st.title("AdTech Analytics Dashboard")
    
    # Get filters
    filters = get_common_filters()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "Campaign Summary",
        "Campaign Performance",
        "Creative Performance"
    ])
    
    # Tab 1: Campaign Summary
    with tab1:
        st.header("Campaign Summary Dashboard")
        where_clause = build_where_clause(filters)
        query = f"""
        SELECT 
            date,
            campaign_id,
            brand,
            SUM(impressions) as impressions,
            SUM(clicks) as clicks,
            SUM(conversions) as conversions,
            SUM(spend) as spend
        FROM adtech_db.campaign_performance
        WHERE {where_clause}
        GROUP BY date, campaign_id, brand
        ORDER BY date
        """
        
        with st.spinner("Loading campaign summary data..."):
            df = load_data(query)
            if not df.empty:
                render_campaign_summary(df)
            else:
                st.warning("No data available for the selected filters.")
    
    # Tab 2: Campaign Performance
    with tab2:
        st.header("Campaign Performance Dashboard")
        where_clause = build_where_clause(filters)
        query = f"""
        SELECT 
            date,
            campaign_id,
            brand,
            country,
            state,
            city,
            SUM(impressions) as impressions,
            SUM(clicks) as clicks,
            SUM(conversions) as conversions,
            SUM(spend) as spend
        FROM adtech_db.campaign_performance
        WHERE {where_clause}
        GROUP BY date, campaign_id, brand, country, state, city
        ORDER BY date
        """
        
        with st.spinner("Loading campaign performance data..."):
            df = load_data(query)
            if not df.empty:
                render_campaign_performance(df)
            else:
                st.warning("No data available for the selected filters.")
    
    # Tab 3: Creative Performance
    with tab3:
        st.header("Creative Performance Dashboard")
        where_clause = build_where_clause(filters, include_ad_id=True)
        query = f"""
        SELECT 
            date,
            campaign_id,
            ad_id,
            brand,
            country,
            state,
            city,
            SUM(impressions) as impressions,
            SUM(clicks) as clicks,
            SUM(conversions) as conversions,
            SUM(spend) as spend
        FROM adtech_db.creative_performance
        WHERE {where_clause}
        GROUP BY date, campaign_id, ad_id, brand, country, state, city
        ORDER BY date
        """
        
        with st.spinner("Loading creative performance data..."):
            df = load_data(query)
            if not df.empty:
                render_creative_performance(df)
            else:
                st.warning("No data available for the selected filters.")

if __name__ == "__main__":
    main() 