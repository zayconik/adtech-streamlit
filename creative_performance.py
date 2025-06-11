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

def render_creative_performance(df):
    """Render the creative performance dashboard"""
    st.subheader("Creative Performance Dashboard")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Creative Analysis", "Performance Patterns", "Campaign Context"])
    
    with tab1:
        # Creative-level metrics
        creative_metrics = df.groupby('ad_id').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'spend': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Calculate derived metrics
        creative_metrics['ctr'] = (creative_metrics['clicks'] / creative_metrics['impressions'] * 100).round(2)
        creative_metrics['cpc'] = (creative_metrics['spend'] / creative_metrics['clicks']).round(2)
        creative_metrics['conversion_rate'] = (creative_metrics['conversions'] / creative_metrics['clicks'] * 100).round(2)
        creative_metrics['roi'] = (creative_metrics['conversions'] / creative_metrics['spend']).round(2)
        
        # Top 10 Creatives by ROI
        st.subheader("Top 10 Creatives by ROI")
        top_creatives = creative_metrics.sort_values('roi', ascending=False).head(10)
        
        # Display top creatives table
        display_top_creatives = format_metrics(top_creatives)
        st.dataframe(display_top_creatives, hide_index=True)
        
        fig = px.bar(
            top_creatives,
            x='ad_id',
            y='roi',
            color='spend',
            title='Top 10 Creatives by ROI',
            labels={'roi': 'ROI (Conversions/Spend)', 'ad_id': 'Ad ID', 'spend': 'Spend ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Creative Performance Table
        st.subheader("Creative Performance Details")
        display_creative_metrics = format_metrics(creative_metrics)
        st.dataframe(display_creative_metrics, hide_index=True)
    
    with tab2:
        # Performance by day of week
        df['day_of_week'] = pd.to_datetime(df['date']).dt.day_name()
        daily_metrics = df.groupby('day_of_week').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'spend': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Calculate derived metrics
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
        
        # Top Performing Ads
        st.subheader("Top 5 Ads by ROI")
        top_ads = creative_metrics.sort_values('roi', ascending=False).head(5)
        
        # Display top ads table
        display_top_ads = format_metrics(top_ads)
        st.dataframe(display_top_ads, hide_index=True)
        
        fig = px.bar(
            top_ads,
            x='ad_id',
            y='roi',
            color='spend',
            title='Top 5 Ads by ROI',
            labels={'roi': 'ROI (Conversions/Spend)', 'ad_id': 'Ad ID', 'spend': 'Spend ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Campaign context analysis
        campaign_metrics = df.groupby(['campaign_id', 'country', 'state', 'city']).agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'spend': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Calculate derived metrics
        campaign_metrics['ctr'] = (campaign_metrics['clicks'] / campaign_metrics['impressions'] * 100).round(2)
        campaign_metrics['cpc'] = (campaign_metrics['spend'] / campaign_metrics['clicks']).round(2)
        campaign_metrics['conversion_rate'] = (campaign_metrics['conversions'] / campaign_metrics['clicks'] * 100).round(2)
        campaign_metrics['roi'] = (campaign_metrics['conversions'] / campaign_metrics['spend']).round(2)
        
        # Campaign Context Analysis
        st.subheader("Campaign Context Analysis")
        fig = px.scatter(
            campaign_metrics,
            x='spend',
            y='roi',
            color='ctr',
            size='impressions',
            hover_data=['campaign_id', 'country', 'state', 'city', 'clicks', 'conversions'],
            title='Campaign Performance by Location (Bubble size: Impressions, Color: CTR)',
            labels={'spend': 'Total Spend ($)', 'roi': 'ROI (Conversions/Spend)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Ad Performance by Campaign and Location
        st.subheader("Ad Performance by Campaign and Location")
        display_campaign_metrics = format_metrics(campaign_metrics)
        st.dataframe(display_campaign_metrics, hide_index=True)
    
    # Download button
    create_download_button(df, 'creative_performance.csv') 