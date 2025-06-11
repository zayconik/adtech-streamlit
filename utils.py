import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def calculate_metrics(df):
    """Calculate common metrics from the dataframe"""
    metrics = {
        'total_spend': df['spend'].sum(),
        'total_clicks': df['clicks'].sum(),
        'total_impressions': df['impressions'].sum(),
        'total_conversions': df['conversions'].sum(),
        'ctr': (df['clicks'].sum() / df['impressions'].sum() * 100) if df['impressions'].sum() > 0 else 0,
        'cpc': (df['spend'].sum() / df['clicks'].sum()) if df['clicks'].sum() > 0 else 0,
        'cpm': (df['spend'].sum() / df['impressions'].sum() * 1000) if df['impressions'].sum() > 0 else 0,
        'conversion_rate': (df['conversions'].sum() / df['clicks'].sum() * 100) if df['clicks'].sum() > 0 else 0
    }
    return metrics

def display_kpi_cards(metrics):
    """Display KPI cards for metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Spend", f"${metrics['total_spend']:,.2f}")
    with col2:
        st.metric("Total Clicks", f"{metrics['total_clicks']:,.0f}")
    with col3:
        st.metric("Total Impressions", f"{metrics['total_impressions']:,.0f}")
    with col4:
        st.metric("Total Conversions", f"{metrics['total_conversions']:,.0f}")
    
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("CTR", f"{metrics['ctr']:.2f}%")
    with col6:
        st.metric("CPC", f"${metrics['cpc']:.2f}")
    with col7:
        st.metric("CPM", f"${metrics['cpm']:.2f}")
    with col8:
        st.metric("Conv. Rate", f"{metrics['conversion_rate']:.2f}%")

def create_download_button(df, filename):
    """Create a download button for the dataframe"""
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

def plot_top_campaigns(df, metric, title, n=10):
    """Plot top N campaigns by specified metric"""
    top_campaigns = df.groupby('campaign_id')[metric].sum().sort_values(ascending=False).head(n)
    
    fig = px.bar(
        top_campaigns,
        title=title,
        labels={'value': metric.replace('_', ' ').title(), 'campaign_id': 'Campaign ID'}
    )
    
    fig.update_layout(
        showlegend=False,
        xaxis_title="Campaign ID",
        yaxis_title=metric.replace('_', ' ').title()
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_trend(df, metric, title):
    """Plot trend of metric over time"""
    daily_metric = df.groupby('date')[metric].sum().reset_index()
    
    fig = px.line(
        daily_metric,
        x='date',
        y=metric,
        title=title
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=metric.replace('_', ' ').title()
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_pie_chart(df, column, title):
    """Create a pie chart for distribution"""
    distribution = df.groupby(column)['spend'].sum().reset_index()
    
    fig = px.pie(
        distribution,
        values='spend',
        names=column,
        title=title
    )
    
    st.plotly_chart(fig, use_container_width=True) 