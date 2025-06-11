import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import create_download_button

def format_metrics(df):
    """Format metrics for display"""
    df = df.copy()
    df['impressions'] = df['impressions'].map('{:,}'.format)
    df['clicks'] = df['clicks'].map('{:,}'.format)
    df['conversions'] = df['conversions'].map('{:,}'.format)
    df['spend'] = df['spend'].map('${:,.2f}'.format)
    df['ctr'] = df['ctr'].map('{:.2f}%'.format)
    df['cpc'] = df['cpc'].map('${:.2f}'.format)
    df['conversion_rate'] = df['conversion_rate'].map('{:.2f}%'.format)
    df['roi'] = df['roi'].map('{:.2f}'.format)
    return df

def render_campaign_performance(df):
    """Render the campaign performance dashboard"""
    st.subheader("Campaign Performance Dashboard")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Geographic Analysis", "Performance Patterns", "Campaign Insights"])
    
    with tab1:
        # Geographic aggregation
        geo_metrics = df.groupby(['country', 'state', 'city']).agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'spend': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Calculate derived metrics
        geo_metrics['ctr'] = (geo_metrics['clicks'] / geo_metrics['impressions'] * 100).round(2)
        geo_metrics['cpc'] = (geo_metrics['spend'] / geo_metrics['clicks']).round(2)
        geo_metrics['conversion_rate'] = (geo_metrics['conversions'] / geo_metrics['clicks'] * 100).round(2)
        geo_metrics['roi'] = (geo_metrics['conversions'] / geo_metrics['spend']).round(2)
        
        # Country Performance Analysis
        st.subheader("Country Performance Analysis")
        country_metrics = geo_metrics.groupby('country').agg({
            'conversions': 'sum',
            'clicks': 'sum',
            'spend': 'sum',
            'impressions': 'sum'
        }).reset_index()
        
        # Calculate derived metrics for country level
        country_metrics['ctr'] = (country_metrics['clicks'] / country_metrics['impressions'] * 100).round(2)
        country_metrics['cpc'] = (country_metrics['spend'] / country_metrics['clicks']).round(2)
        country_metrics['conversion_rate'] = (country_metrics['conversions'] / country_metrics['clicks'] * 100).round(2)
        country_metrics['roi'] = (country_metrics['conversions'] / country_metrics['spend']).round(2)
        
        country_metrics = country_metrics.sort_values('conversion_rate', ascending=False)
        
        # Display country metrics table
        display_country_metrics = format_metrics(country_metrics)
        st.dataframe(display_country_metrics, hide_index=True)
        
        fig = px.bar(
            country_metrics,
            x='country',
            y='conversion_rate',
            color='spend',
            title='Conversion Rate by Country',
            labels={'conversion_rate': 'Conversion Rate (%)', 'country': 'Country', 'spend': 'Spend ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Spend vs Conversions by State
        st.subheader("Spend vs Conversions by State")
        fig = px.scatter(
            geo_metrics,
            x='spend',
            y='conversions',
            color='ctr',
            size='impressions',
            hover_data=['country', 'state', 'city', 'clicks'],
            title='Spend vs Conversions (Bubble size: Impressions, Color: CTR)',
            labels={'spend': 'Total Spend ($)', 'conversions': 'Total Conversions'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Campaign Performance by Location
        st.subheader("Campaign Performance by Location")
        display_geo_metrics = format_metrics(geo_metrics)
        st.dataframe(display_geo_metrics, hide_index=True)
    
    with tab2:
        # Performance by day of week
        df['day_of_week'] = pd.to_datetime(df['date']).dt.day_name()
        daily_metrics = df.groupby('day_of_week').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'spend': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Calculate derived metrics for daily metrics
        daily_metrics['ctr'] = (daily_metrics['clicks'] / daily_metrics['impressions'] * 100).round(2)
        daily_metrics['cpc'] = (daily_metrics['spend'] / daily_metrics['clicks']).round(2)
        daily_metrics['conversion_rate'] = (daily_metrics['conversions'] / daily_metrics['clicks'] * 100).round(2)
        daily_metrics['roi'] = (daily_metrics['conversions'] / daily_metrics['spend']).round(2)
        
        # Display daily metrics table
        st.subheader("Daily Performance Metrics")
        display_daily_metrics = format_metrics(daily_metrics)
        st.dataframe(display_daily_metrics, hide_index=True)
        
        # Performance by Day of Week
        st.subheader("Performance by Day of Week")
        fig = px.bar(
            daily_metrics,
            x='day_of_week',
            y=['ctr', 'conversion_rate'],
            barmode='group',
            title='CTR and Conversion Rate by Day of Week',
            labels={'value': 'Rate (%)', 'day_of_week': 'Day of Week'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top Performing States
        st.subheader("Top 5 States by ROI")
        state_metrics = geo_metrics.groupby('state').agg({
            'conversions': 'sum',
            'spend': 'sum',
            'clicks': 'sum',
            'impressions': 'sum'
        }).reset_index()
        state_metrics['roi'] = (state_metrics['conversions'] / state_metrics['spend']).round(2)
        state_metrics['ctr'] = (state_metrics['clicks'] / state_metrics['impressions'] * 100).round(2)
        state_metrics['conversion_rate'] = (state_metrics['conversions'] / state_metrics['clicks'] * 100).round(2)
        state_metrics['cpc'] = (state_metrics['spend'] / state_metrics['clicks']).round(2)
        top_states = state_metrics.sort_values('roi', ascending=False).head(5)
        
        # Display state metrics table
        display_state_metrics = format_metrics(top_states)
        st.dataframe(display_state_metrics, hide_index=True)
        
        fig = px.bar(
            top_states,
            x='state',
            y='roi',
            color='spend',
            title='Top 5 States by ROI',
            labels={'roi': 'ROI (Conversions/Spend)', 'state': 'State', 'spend': 'Spend ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Campaign efficiency analysis
        campaign_metrics = df.groupby('campaign_id').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'spend': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        campaign_metrics['ctr'] = (campaign_metrics['clicks'] / campaign_metrics['impressions'] * 100).round(2)
        campaign_metrics['cpc'] = (campaign_metrics['spend'] / campaign_metrics['clicks']).round(2)
        campaign_metrics['conversion_rate'] = (campaign_metrics['conversions'] / campaign_metrics['clicks'] * 100).round(2)
        campaign_metrics['roi'] = (campaign_metrics['conversions'] / campaign_metrics['spend']).round(2)
        
        # Campaign Efficiency Analysis
        st.subheader("Campaign Efficiency Analysis")
        fig = px.scatter(
            campaign_metrics,
            x='cpc',
            y='conversion_rate',
            color='ctr',
            size='spend',
            hover_data=['campaign_id', 'clicks', 'conversions'],
            title='Campaign Efficiency: CPC vs Conversion Rate (Bubble size: Spend, Color: CTR)',
            labels={'cpc': 'Cost per Click ($)', 'conversion_rate': 'Conversion Rate (%)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top 10 Campaigns by ROI
        st.subheader("Top 10 Campaigns by ROI")
        top_campaigns = campaign_metrics.sort_values('roi', ascending=False).head(10)
        
        # Display top campaigns table
        display_top_campaigns = format_metrics(top_campaigns)
        st.dataframe(display_top_campaigns, hide_index=True)
        
        fig = px.bar(
            top_campaigns,
            x='campaign_id',
            y='roi',
            color='spend',
            title='Top 10 Campaigns by ROI',
            labels={'roi': 'ROI (Conversions/Spend)', 'campaign_id': 'Campaign ID', 'spend': 'Spend ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Campaign Performance Table
        st.subheader("Campaign Performance Details")
        display_campaign_metrics = format_metrics(campaign_metrics)
        st.dataframe(display_campaign_metrics, hide_index=True)
    
    # Download button
    create_download_button(df, 'campaign_performance.csv') 