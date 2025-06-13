import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import streamlit as st

# Page config
st.set_page_config(
    page_title="Load Agent Dashboard",
    page_icon="📊",
    layout="wide"
)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/loads")

# Create database engine
engine = create_engine(DATABASE_URL)

def get_bookings_per_day():
    """Get number of bookings per day."""
    query = """
    SELECT 
        DATE(recorded_at) as date,
        COUNT(*) as bookings
    FROM calls 
    WHERE status = 'BOOKED'
    GROUP BY DATE(recorded_at)
    ORDER BY date DESC
    LIMIT 30
    """
    return pd.read_sql(query, engine)

def get_rate_difference():
    """Get average difference between negotiated and offer rates."""
    query = """
    SELECT 
        DATE(recorded_at) as date,
        AVG(negotiated_rate - offer_rate) as rate_diff
    FROM calls c
    JOIN loads l ON c.load_id = l.id
    WHERE status = 'BOOKED'
    GROUP BY DATE(recorded_at)
    ORDER BY date DESC
    LIMIT 30
    """
    return pd.read_sql(query, engine)

def get_sentiment_breakdown():
    """Get breakdown of call sentiments."""
    query = """
    SELECT 
        sentiment,
        COUNT(*) as count
    FROM calls
    WHERE sentiment IS NOT NULL
    GROUP BY sentiment
    """
    return pd.read_sql(query, engine)

def get_recent_loads():
    """Get most recent loads."""
    query = """
    SELECT 
        l.*,
        c.status,
        c.negotiated_rate,
        c.sentiment
    FROM loads l
    LEFT JOIN calls c ON l.id = c.load_id
    ORDER BY l.created_at DESC
    LIMIT 10
    """
    return pd.read_sql(query, engine)

# Dashboard title
st.title("📊 Load Agent Dashboard")

# Create three columns for metrics
col1, col2, col3 = st.columns(3)

# Get data
bookings_df = get_bookings_per_day()
rate_diff_df = get_rate_difference()
sentiment_df = get_sentiment_breakdown()
recent_loads_df = get_recent_loads()

# Calculate metrics
total_bookings = bookings_df['bookings'].sum()
avg_rate_diff = rate_diff_df['rate_diff'].mean()
positive_sentiment = sentiment_df[sentiment_df['sentiment'] == 'positive']['count'].sum()

# Display metrics
with col1:
    st.metric("Total Bookings (30d)", total_bookings)
with col2:
    st.metric("Avg Rate Difference", f"${avg_rate_diff:.2f}")
with col3:
    st.metric("Positive Sentiment %", f"{(positive_sentiment / sentiment_df['count'].sum() * 100):.1f}%")

# Create two columns for charts
col1, col2 = st.columns(2)

# Bookings per day chart
with col1:
    st.subheader("Bookings per Day")
    fig = px.bar(
        bookings_df,
        x='date',
        y='bookings',
        title="Daily Bookings (Last 30 Days)"
    )
    st.plotly_chart(fig, use_container_width=True)

# Rate difference chart
with col2:
    st.subheader("Rate Negotiation")
    fig = px.line(
        rate_diff_df,
        x='date',
        y='rate_diff',
        title="Average Rate Difference (Last 30 Days)"
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)

# Sentiment breakdown
st.subheader("Call Sentiment Breakdown")
fig = px.pie(
    sentiment_df,
    values='count',
    names='sentiment',
    title="Call Sentiment Distribution"
)
st.plotly_chart(fig, use_container_width=True)

# Recent loads table
st.subheader("Recent Loads")
st.dataframe(
    recent_loads_df[[
        'origin_city', 'origin_state', 'dest_city', 'dest_state',
        'equipment', 'pickup_ts', 'distance_mi', 'offer_rate',
        'status', 'negotiated_rate', 'sentiment'
    ]].rename(columns={
        'origin_city': 'Origin City',
        'origin_state': 'Origin State',
        'dest_city': 'Destination City',
        'dest_state': 'Destination State',
        'equipment': 'Equipment',
        'pickup_ts': 'Pickup Time',
        'distance_mi': 'Distance (mi)',
        'offer_rate': 'Offer Rate ($)',
        'status': 'Status',
        'negotiated_rate': 'Negotiated Rate ($)',
        'sentiment': 'Sentiment'
    }),
    use_container_width=True
)
