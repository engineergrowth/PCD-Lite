"""
PCD-Lite Analytics Dashboard
Streamlit dashboard for visualizing recommendation analytics and A/B testing results
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="PCD-Lite Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .variant-a {
        border-left-color: #ff7f0e;
    }
    .variant-b {
        border-left-color: #2ca02c;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def fetch_api_data(endpoint: str, params: dict = None) -> dict:
    """Fetch data from the API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API: {e}")
        return None

def format_percentage(value: float) -> str:
    """Format percentage values"""
    return f"{value:.2f}%"

def format_number(value: int) -> str:
    """Format large numbers with commas"""
    return f"{value:,}"

def create_metric_card(title: str, value: str, delta: str = None, variant: str = None):
    """Create a metric card component"""
    variant_class = f" variant-{variant.lower()}" if variant else ""
    st.markdown(f"""
    <div class="metric-card{variant_class}">
        <h4>{title}</h4>
        <h2>{value}</h2>
        {f'<p>{delta}</p>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main dashboard application"""
    st.title("📊 PCD-Lite Analytics Dashboard")
    st.markdown("Personalized Content Discovery - A/B Testing Analytics")
    
    # Sidebar controls
    st.sidebar.header("Dashboard Controls")
    
    # Time period selector
    days = st.sidebar.selectbox(
        "Select Time Period",
        options=[1, 3, 7, 14, 30],
        index=2,
        format_func=lambda x: f"Last {x} days"
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # API status check
    st.sidebar.header("API Status")
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.sidebar.success("✅ API Connected")
        else:
            st.sidebar.error("❌ API Error")
    except:
        st.sidebar.error("❌ API Offline")
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🧪 A/B Testing", "🎬 Content", "🔍 Sessions"])
    
    with tab1:
        st.header("📈 Overview Metrics")
        
        # Fetch analytics data
        analytics_data = fetch_api_data("/analytics", {"days": days})
        
        if analytics_data and "metrics" in analytics_data:
            metrics = analytics_data["metrics"]
            
            # Key metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                create_metric_card(
                    "Total Sessions",
                    format_number(metrics["total_sessions"]),
                    f"Last {days} days"
                )
            
            with col2:
                create_metric_card(
                    "Total Impressions",
                    format_number(metrics["total_impressions"]),
                    f"Last {days} days"
                )
            
            with col3:
                create_metric_card(
                    "Total Clicks",
                    format_number(metrics["total_clicks"]),
                    f"Last {days} days"
                )
            
            with col4:
                create_metric_card(
                    "Overall CTR",
                    format_percentage(metrics["ctr"]),
                    f"Last {days} days"
                )
            
            # Charts row
            col1, col2 = st.columns(2)
            
            with col1:
                # CTR by variant
                variant_data = {
                    "Variant": ["A (Popularity)", "B (Similarity)"],
                    "CTR": [metrics["variant_a_ctr"], metrics["variant_b_ctr"]],
                    "Impressions": [metrics["variant_a_impressions"], metrics["variant_b_impressions"]],
                    "Clicks": [metrics["variant_a_clicks"], metrics["variant_b_clicks"]]
                }
                
                fig = px.bar(
                    variant_data, 
                    x="Variant", 
                    y="CTR",
                    title="Click-Through Rate by Variant",
                    color="Variant",
                    color_discrete_map={"A (Popularity)": "#ff7f0e", "B (Similarity)": "#2ca02c"}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Impressions vs Clicks
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name="Impressions",
                    x=["Variant A", "Variant B"],
                    y=[metrics["variant_a_impressions"], metrics["variant_b_impressions"]],
                    marker_color=["#ff7f0e", "#2ca02c"]
                ))
                fig.add_trace(go.Bar(
                    name="Clicks",
                    x=["Variant A", "Variant B"],
                    y=[metrics["variant_a_clicks"], metrics["variant_b_clicks"]],
                    marker_color=["#ff7f0e", "#2ca02c"],
                    opacity=0.7
                ))
                fig.update_layout(
                    title="Impressions vs Clicks by Variant",
                    barmode="group"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Popular genres and movies
            col1, col2 = st.columns(2)
            
            with col1:
                if metrics["most_popular_genres"]:
                    genres_df = pd.DataFrame(metrics["most_popular_genres"])
                    fig = px.pie(
                        genres_df, 
                        values="count", 
                        names="genre",
                        title="Most Popular Genres"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if metrics["most_clicked_movies"]:
                    movies_df = pd.DataFrame(metrics["most_clicked_movies"])
                    fig = px.bar(
                        movies_df, 
                        x="movie_id", 
                        y="clicks",
                        title="Most Clicked Movies",
                        labels={"movie_id": "Movie ID", "clicks": "Click Count"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.error("Unable to fetch analytics data. Please check if the API is running.")
    
    with tab2:
        st.header("🧪 A/B Testing Analysis")
        
        # Fetch variant performance data
        variant_data = fetch_api_data("/analytics/variants", {"days": days})
        
        if variant_data and "performance" in variant_data:
            performance = variant_data["performance"]
            
            # Variant comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Variant A (Popularity-based)")
                variant_a = performance["variant_a"]
                create_metric_card(
                    "Sessions",
                    format_number(variant_a["sessions"]),
                    variant="a"
                )
                create_metric_card(
                    "Impressions",
                    format_number(variant_a["impressions"]),
                    variant="a"
                )
                create_metric_card(
                    "Clicks",
                    format_number(variant_a["clicks"]),
                    variant="a"
                )
                if variant_a["impressions"] > 0:
                    ctr_a = (variant_a["clicks"] / variant_a["impressions"]) * 100
                    create_metric_card(
                        "CTR",
                        format_percentage(ctr_a),
                        variant="a"
                    )
            
            with col2:
                st.subheader("Variant B (Similarity-based)")
                variant_b = performance["variant_b"]
                create_metric_card(
                    "Sessions",
                    format_number(variant_b["sessions"]),
                    variant="b"
                )
                create_metric_card(
                    "Impressions",
                    format_number(variant_b["impressions"]),
                    variant="b"
                )
                create_metric_card(
                    "Clicks",
                    format_number(variant_b["clicks"]),
                    variant="b"
                )
                if variant_b["impressions"] > 0:
                    ctr_b = (variant_b["clicks"] / variant_b["impressions"]) * 100
                    create_metric_card(
                        "CTR",
                        format_percentage(ctr_b),
                        variant="b"
                    )
            
            # Statistical significance (simplified)
            st.subheader("Statistical Analysis")
            
            if variant_a["impressions"] > 0 and variant_b["impressions"] > 0:
                ctr_a = (variant_a["clicks"] / variant_a["impressions"]) * 100
                ctr_b = (variant_b["clicks"] / variant_b["impressions"]) * 100
                
                improvement = ((ctr_b - ctr_a) / ctr_a) * 100 if ctr_a > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "CTR Difference",
                        f"{ctr_b - ctr_a:.2f}%",
                        f"{improvement:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Sample Size",
                        f"{variant_a['impressions'] + variant_b['impressions']:,}",
                        "Total Impressions"
                    )
                
                with col3:
                    confidence = "High" if min(variant_a["impressions"], variant_b["impressions"]) > 100 else "Low"
                    st.metric(
                        "Confidence",
                        confidence,
                        "Based on sample size"
                    )
            
            # Recommendation
            st.subheader("Recommendation")
            if variant_a["impressions"] > 0 and variant_b["impressions"] > 0:
                ctr_a = (variant_a["clicks"] / variant_a["impressions"]) * 100
                ctr_b = (variant_b["clicks"] / variant_b["impressions"]) * 100
                
                if ctr_b > ctr_a * 1.05:  # 5% improvement threshold
                    st.success("🎯 Variant B (Similarity-based) is performing better. Consider rolling out to more users.")
                elif ctr_a > ctr_b * 1.05:
                    st.success("🎯 Variant A (Popularity-based) is performing better. Consider rolling out to more users.")
                else:
                    st.info("📊 Both variants are performing similarly. Continue testing with more data.")
            else:
                st.warning("⚠️ Insufficient data for statistical analysis. Continue collecting data.")
        
        else:
            st.error("Unable to fetch variant performance data.")
    
    with tab3:
        st.header("🎬 Content Analysis")
        
        # Fetch catalog data
        catalog_data = fetch_api_data("/catalog", {"limit": 50})
        
        if catalog_data and "movies" in catalog_data:
            movies_df = pd.DataFrame(catalog_data["movies"])
            
            # Content overview
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Movies", format_number(catalog_data["total_movies"]))
            
            with col2:
                avg_rating = movies_df["rating"].mean()
                st.metric("Average Rating", f"{avg_rating:.1f}")
            
            with col3:
                avg_runtime = movies_df["runtime"].mean()
                st.metric("Average Runtime", f"{avg_runtime:.0f} min")
            
            # Genre distribution
            st.subheader("Genre Distribution")
            genre_counts = {}
            for genres in movies_df["genre"]:
                for genre in genres:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            if genre_counts:
                genre_df = pd.DataFrame(list(genre_counts.items()), columns=["Genre", "Count"])
                fig = px.bar(
                    genre_df, 
                    x="Count", 
                    y="Genre",
                    orientation="h",
                    title="Movies by Genre"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Rating distribution
            st.subheader("Rating Distribution")
            fig = px.histogram(
                movies_df, 
                x="rating",
                nbins=20,
                title="Movie Rating Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Runtime vs Rating
            st.subheader("Runtime vs Rating")
            fig = px.scatter(
                movies_df, 
                x="runtime", 
                y="rating",
                hover_data=["title", "genre"],
                title="Runtime vs Rating Scatter Plot"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Top movies table
            st.subheader("Top Movies by Rating")
            top_movies = movies_df.nlargest(10, "rating")[["title", "rating", "runtime", "release_year"]]
            st.dataframe(top_movies, use_container_width=True)
        
        else:
            st.error("Unable to fetch catalog data.")
    
    with tab4:
        st.header("🔍 Session Analysis")
        
        # Session search
        session_id = st.text_input("Enter Session ID to view events", placeholder="e.g., 12345")
        
        if session_id:
            session_data = fetch_api_data(f"/session/{session_id}/events")
            
            if session_data and "events" in session_data:
                events_df = pd.DataFrame(session_data["events"])
                
                if not events_df.empty:
                    st.subheader(f"Session {session_id} Events")
                    
                    # Event summary
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Events", len(events_df))
                    
                    with col2:
                        impressions = len(events_df[events_df["event_type"] == "impression"])
                        st.metric("Impressions", impressions)
                    
                    with col3:
                        clicks = len(events_df[events_df["event_type"] == "click"])
                        st.metric("Clicks", clicks)
                    
                    # Event timeline
                    st.subheader("Event Timeline")
                    events_df["timestamp"] = pd.to_datetime(events_df["timestamp"])
                    events_df = events_df.sort_values("timestamp")
                    
                    fig = px.timeline(
                        events_df,
                        x_start="timestamp",
                        x_end="timestamp",
                        y="event_type",
                        color="variant",
                        title="Event Timeline"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Events table
                    st.subheader("Event Details")
                    st.dataframe(events_df, use_container_width=True)
                
                else:
                    st.warning(f"No events found for session {session_id}")
            
            else:
                st.error(f"Unable to fetch events for session {session_id}")
        
        else:
            st.info("Enter a session ID to view its events")

if __name__ == "__main__":
    main()
