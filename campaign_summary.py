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
    return df

def render_campaign_summary(df):
    """Render the campaign summary dashboard"""
    st.subheader("Campaign Summary Dashboard")
    
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Spend", f"${df['spend'].sum():,.2f}")
    with col2:
        st.metric("Total Impressions", f"{df['impressions'].sum():,}")
    with col3:
        st.metric("Total Clicks", f"{df['clicks'].sum():,}")
    
    # Top 10 Campaigns by Spend
    st.subheader("Top 10 Campaigns by Spend")
    top_campaigns = df.groupby('campaign_id')['spend'].sum().sort_values(ascending=False).head(10).reset_index()
    
    fig = px.bar(
        top_campaigns,
        x='campaign_id',
        y='spend',
        title='Top 10 Campaigns by Spend',
        labels={'spend': 'Spend ($)', 'campaign_id': 'Campaign ID'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # CTR trend over time
    st.subheader("CTR Trend Over Time")
    daily_metrics = df.groupby('date').agg({
        'clicks': 'sum',
        'impressions': 'sum'
    }).reset_index()
    daily_metrics['ctr'] = (daily_metrics['clicks'] / daily_metrics['impressions'] * 100).round(2)
    
    fig = px.line(
        daily_metrics,
        x='date',
        y='ctr',
        title='CTR Trend Over Time',
        labels={'ctr': 'CTR (%)', 'date': 'Date'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Clicks vs Conversions per Campaign
    st.subheader("Clicks vs Conversions per Campaign")
    campaign_metrics = df.groupby('campaign_id').agg({
        'clicks': 'sum',
        'conversions': 'sum'
    }).reset_index()
    
    fig = px.bar(
        campaign_metrics,
        x='campaign_id',
        y=['clicks', 'conversions'],
        barmode='group',
        title='Clicks vs Conversions per Campaign',
        labels={'value': 'Count', 'campaign_id': 'Campaign ID'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Campaign breakdown by date
    st.subheader("Campaign Breakdown by Date")
    daily_campaign_metrics = df.groupby(['date', 'campaign_id']).agg({
        'impressions': 'sum',
        'clicks': 'sum',
        'conversions': 'sum',
        'spend': 'sum'
    }).reset_index()
    
    daily_campaign_metrics['ctr'] = (daily_campaign_metrics['clicks'] / daily_campaign_metrics['impressions'] * 100).round(2)
    daily_campaign_metrics['cpc'] = (daily_campaign_metrics['spend'] / daily_campaign_metrics['clicks']).round(2)
    daily_campaign_metrics['conversion_rate'] = (daily_campaign_metrics['conversions'] / daily_campaign_metrics['clicks'] * 100).round(2)
    
    display_daily_metrics = format_metrics(daily_campaign_metrics)
    st.dataframe(display_daily_metrics, hide_index=True)
    
    # Download button
    create_download_button(df, 'campaign_summary.csv') 