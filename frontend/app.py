"""
🐦 Twitter Sentiment Analysis - Modern Streamlit Frontend
Stunning interface for sentiment analysis with advanced features
"""

import streamlit as st
import requests
import json
import pandas as pd
import os
from datetime import datetime
import logging
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# ============================================================================
# SETUP & CONFIGURATION
# ============================================================================

# Setup frontend logging
FRONTEND_LOG_FILE = Path("./logs/frontend_interactions.log")
FRONTEND_LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(FRONTEND_LOG_FILE),
        logging.StreamHandler()
    ]
)
frontend_logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🐦 Twitter Sentiment Analyzer",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Twitter Sentiment Analysis - Powered by BERTweet & FastAPI"
    }
)

# ============================================================================
# CUSTOM STYLING & THEMES
# ============================================================================

st.markdown("""
<style>
    /* Main page styling */
    .main {
        background: #000000;
        color: white;
        background-attachment: fixed;
    }

    /* Make most default text white */
    body {
        background-color: #000000;
        color: white;
    }

    /* Streamlit text elements */
    [data-testid="stMarkdownContainer"] {
        color: white;
    }

    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
        color: white;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Sentiment badges */
    .sentiment-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
        font-size: 1.1rem;
        margin: 0.5rem 0;
    }
    
    .sentiment-positive {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4);
    }
    
    .sentiment-negative {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.4);
    }
    
    .sentiment-neutral {
        background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(149, 165, 166, 0.4);
    }
    
    /* Result container */
    .result-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border-top: 4px solid #667eea;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #333;
        padding: 1rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        color: #667eea;
        border-bottom: 3px solid #667eea;
    }
    
    /* Sidebar styling */
    .sidebar {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Info box styling */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #667eea;
    }
    
    /* Text input styling */
    .stTextArea textarea {
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Slider styling */
    .stSlider [data-baseweb="slider"] {
        background: #e0e0e0;
    }
    
    /* Table styling */
    .dataframe {
        border-collapse: collapse;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        text-align: left;
    }
    
    .dataframe td {
        padding: 0.75rem;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .dataframe tr:hover {
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="header-container">
    <h1 class="header-title">🐦 Twitter Sentiment Analyzer</h1>
    <p class="header-subtitle">✨ Powered by Advanced NLP & Machine Learning</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

st.sidebar.markdown("# ⚙️ Configuration")
st.sidebar.divider()

# API URL
api_base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")

api_base_url = st.sidebar.text_input(
    "🔗 API Base URL",
    value=api_base_url,
    help="Enter the backend FastAPI server URL (or set API_BASE_URL env var)"
)

# Confidence Threshold
st.sidebar.markdown("### 🎯 Confidence Threshold")
confidence_threshold = st.sidebar.slider(
    "Set Minimum Confidence (%)",
    min_value=0,
    max_value=100,
    value=50,
    step=5,
    help="Only predictions above this threshold will be marked as reliable"
)

# Threshold indicator
if confidence_threshold >= 80:
    threshold_indicator = "🔒 Very Strict"
    threshold_color = "#e74c3c"
elif confidence_threshold >= 60:
    threshold_indicator = "⚖️ Balanced"
    threshold_color = "#f39c12"
elif confidence_threshold >= 30:
    threshold_indicator = "🔓 Relaxed"
    threshold_color = "#27ae60"
else:
    threshold_indicator = "🔓 Very Relaxed"
    threshold_color = "#3498db"

st.sidebar.markdown(f"""
<div style="background: linear-gradient(135deg, {threshold_color} 0%, {threshold_color}CC 100%); 
            color: white; padding: 1rem; border-radius: 10px; text-align: center; font-weight: 600;">
    {threshold_indicator}<br><span style="font-size: 0.9rem;">Current: {confidence_threshold}%</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()

# API Health Check
@st.cache_resource
def check_api_health():
    try:
        response = requests.get(f"{api_base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

api_healthy = check_api_health()

if api_healthy:
    st.sidebar.success("✅ API Connected")
    try:
        health = requests.get(f"{api_base_url}/health", timeout=5).json()
        st.sidebar.info(f"📊 Model Loaded: {'✅ Yes' if health.get('model_loaded') else '⚠️ Using Fallback'}")
        st.sidebar.info(f"💻 Device: {health.get('device', 'Unknown')}")
    except:
        pass
else:
    st.sidebar.error("❌ API Disconnected")
    st.sidebar.warning(f"Cannot reach: {api_base_url}")

st.sidebar.divider()

# Instructions
st.sidebar.markdown("""
### 📖 How to Use

1. **Set Threshold**: Adjust confidence level in slider above
2. **Enter Text**: Type or paste a tweet (max 280 chars)
3. **Analyze**: Click the analyze button
4. **View Results**: See sentiment, confidence, and scores
5. **Check History**: Review all previous analyses

### 🎨 Features

- 🔍 Real-time sentiment analysis
- 📊 Confidence scoring
- 📈 Batch processing (up to 100 tweets)
- 📝 Analysis history
- 📈 Performance metrics
- 🔒 Threshold filtering
""")

st.sidebar.divider()

# About
st.sidebar.markdown("""
### ℹ️ About

**Twitter Sentiment Analyzer** uses state-of-the-art NLP models 
to classify tweets as Positive, Negative, or Neutral.

Built with ❤️ using FastAPI & Streamlit
""")

# ============================================================================
# MAIN CONTENT
# ============================================================================

if not api_healthy:
    st.error("""
    ❌ **Cannot Connect to Backend API**
    
    Please ensure the backend is running:
    ```bash
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
    ```
    """)
    st.stop()

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Single Analysis", "📊 Batch Analysis", "📊 History & Stats", "📈 Metrics"])

# ==================== TAB 1: SINGLE ANALYSIS ====================
with tab1:
    col1, col2 = st.columns([3, 1], gap="large")
    
    with col1:
        st.markdown("<h3 style='color: #333; margin-bottom: 1rem;'>Analyze a Single Tweet</h3>", unsafe_allow_html=True)
        
        tweet_text = st.text_area(
            "✍️ Enter Tweet Text:",
            placeholder="Type or paste your tweet here... (maximum 280 characters)",
            height=120,
            max_chars=280,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<p style='margin-top: 1.5rem; text-align: center;'>", unsafe_allow_html=True)
        char_count = len(tweet_text)
        remaining = 280 - char_count
        
        # Character counter with color
        if remaining > 100:
            color = "#27ae60"
        elif remaining > 20:
            color = "#f39c12"
        else:
            color = "#e74c3c"
        
        st.markdown(f"""
        <div style='background: {color}; color: white; padding: 1rem; border-radius: 10px; 
                    text-align: center; font-weight: 600;'>
            <div style='font-size: 1.5rem;'>{char_count}</div>
            <div style='font-size: 0.9rem;'>{remaining} left</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</p>", unsafe_allow_html=True)
    
    # Analyze button
    if st.button("🔍 Analyze Sentiment", use_container_width=True, key="single_analyze"):
        if not tweet_text.strip():
            st.warning("📝 Please enter some text to analyze")
            frontend_logger.warning("Empty text analysis attempted")
        else:
            with st.spinner("🔄 Analyzing sentiment..."):
                frontend_logger.info(f"Analysis: '{tweet_text[:50]}...'")
                try:
                    threshold_decimal = confidence_threshold / 100.0
                    
                    response = requests.post(
                        f"{api_base_url}/predict",
                        json={"text": tweet_text, "threshold": threshold_decimal},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        sentiment = result.get("sentiment", "Unknown")
                        confidence = result.get("confidence", 0)
                        confidence_pct = result.get("confidence_percentage", 0)
                        meets_threshold = result.get("meets_threshold", False)
                        warning = result.get("warning", None)
                        label_scores = result.get("label_scores", {})
                        
                        frontend_logger.info(f"Prediction: {sentiment} ({confidence:.4f})")
                        
                        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                        
                        # Results header
                        col1, col2, col3 = st.columns(3, gap="large")
                        
                        with col1:
                            if sentiment == "Positive":
                                st.markdown(
                                    "<div class='sentiment-badge sentiment-positive'>😊 POSITIVE</div>",
                                    unsafe_allow_html=True
                                )
                            elif sentiment == "Negative":
                                st.markdown(
                                    "<div class='sentiment-badge sentiment-negative'>😢 NEGATIVE</div>",
                                    unsafe_allow_html=True
                                )
                            else:
                                st.markdown(
                                    "<div class='sentiment-badge sentiment-neutral'>😐 NEUTRAL</div>",
                                    unsafe_allow_html=True
                                )
                        
                        with col2:
                            st.metric("Confidence Score", f"{confidence_pct:.1f}%", f"{confidence:.3f}")
                        
                        with col3:
                            status = "✅ Passed" if meets_threshold else "⚠️ Below Threshold"
                            st.metric("Threshold Status", status)
                        
                        st.divider()
                        
                        # Warning if below threshold
                        if warning:
                            st.warning(f"⚠️ {warning}")
                        
                        # Score breakdown with visualization
                        st.markdown("### 📊 Confidence Breakdown")
                        
                        score_col1, score_col2 = st.columns(2)
                        
                        with score_col1:
                            # Bar chart
                            fig = go.Figure(data=[
                                go.Bar(
                                    x=list(label_scores.values()),
                                    y=list(label_scores.keys()),
                                    orientation='h',
                                    marker=dict(
                                        color=['#27ae60' if label == 'Positive' else '#e74c3c' if label == 'Negative' else '#95a5a6' 
                                               for label in label_scores.keys()]
                                    )
                                )
                            ])
                            fig.update_layout(
                                title="Score Distribution",
                                xaxis_title="Confidence",
                                yaxis_title="Sentiment",
                                height=300,
                                margin=dict(l=0, r=0, t=30, b=0),
                                showlegend=False
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with score_col2:
                            st.markdown("**Individual Scores:**")
                            for label, score in label_scores.items():
                                col1_inner, col2_inner = st.columns([1, 4])
                                with col1_inner:
                                    st.write(f"**{label}**")
                                with col2_inner:
                                    st.progress(score, text=f"{score:.1%}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Store in history
                        if "history" not in st.session_state:
                            st.session_state.history = []
                        
                        st.session_state.history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "text": tweet_text,
                            "sentiment": sentiment,
                            "confidence": confidence,
                            "confidence_pct": confidence_pct,
                            "scores": label_scores,
                            "meets_threshold": meets_threshold
                        })
                        
                        st.success("✅ Analysis complete!")
                    
                    else:
                        # Try to surface backend error details
                        try:
                            err = response.json()
                        except Exception:
                            err = {"detail": response.text}

                        st.error(f"❌ API Error: {response.status_code}")
                        st.error(str(err.get("detail", err)))
                        frontend_logger.error(f"API Error {response.status_code}: {err}")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend API")
                    frontend_logger.error("Connection error")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    frontend_logger.error(f"Exception: {str(e)}")

# ==================== TAB 2: BATCH ANALYSIS ====================
with tab2:
    st.markdown("<h3 style='color: #333; margin-bottom: 1rem;'>Batch Sentiment Analysis</h3>", unsafe_allow_html=True)
    st.markdown("Analyze up to 100 tweets at once")
    
    batch_text = st.text_area(
        "📝 Enter Tweets (one per line):",
        placeholder="Tweet 1\nTweet 2\nTweet 3\n...",
        height=150,
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        batch_count = len([t for t in batch_text.split("\n") if t.strip()])
        st.metric("Tweets", batch_count)
    
    with col2:
        if batch_count > 100:
            st.metric("Status", "❌ Too Many", "Max 100")
        elif batch_count == 0:
            st.metric("Status", "⏳ Ready")
        else:
            st.metric("Status", "✅ Ready")
    
    if st.button("📊 Analyze Batch", use_container_width=True, key="batch_analyze"):
        texts = [t.strip() for t in batch_text.split("\n") if t.strip()]
        
        if not texts:
            st.warning("📝 Please enter at least one tweet")
        elif len(texts) > 100:
            st.warning("❌ Maximum 100 tweets per batch")
        else:
            with st.spinner(f"🔄 Analyzing {len(texts)} tweets..."):
                frontend_logger.info(f"Batch analysis: {len(texts)} tweets")
                try:
                    threshold_decimal = confidence_threshold / 100.0
                    
                    response = requests.post(
                        f"{api_base_url}/predict-batch",
                        json={"texts": texts, "threshold": threshold_decimal},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        predictions = response_data.get("predictions", [])
                        stats = response_data.get("statistics", {})
                        
                        # Statistics cards
                        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                        st.markdown("### 📊 Batch Statistics")
                        
                        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                        
                        with stat_col1:
                            st.metric("Total Analyzed", stats.get("total_predictions", 0))
                        
                        with stat_col2:
                            st.metric("Passed Threshold", stats.get("passed_threshold", 0))
                        
                        with stat_col3:
                            st.metric("Below Threshold", stats.get("failed_threshold", 0))
                        
                        with stat_col4:
                            pass_rate = stats.get("pass_rate", 0)
                            st.metric("Pass Rate", f"{pass_rate:.1f}%")
                        
                        st.divider()
                        
                        # Results table
                        st.markdown("### 📋 Detailed Results")
                        
                        results_df = []
                        for i, pred in enumerate(predictions, 1):
                            results_df.append({
                                "#": i,
                                "Tweet": pred["text"][:50] + "..." if len(pred["text"]) > 50 else pred["text"],
                                "Sentiment": pred["sentiment"],
                                "Confidence": f"{pred.get('confidence_percentage', 0):.1f}%",
                                "Status": "✅ Pass" if pred.get("meets_threshold") else "⚠️ Fail"
                            })
                        
                        df = pd.DataFrame(results_df)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # Visualization
                        st.divider()
                        st.markdown("### 📈 Sentiment Distribution")
                        
                        sentiment_counts = {}
                        for pred in predictions:
                            sentiment = pred["sentiment"]
                            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                        
                        fig = px.pie(
                            values=list(sentiment_counts.values()),
                            names=list(sentiment_counts.keys()),
                            color_discrete_map={
                                "Positive": "#27ae60",
                                "Negative": "#e74c3c",
                                "Neutral": "#95a5a6"
                            },
                            hole=0.4
                        )
                        fig.update_layout(height=350)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.success("✅ Batch analysis complete!")
                    
                    else:
                        try:
                            err = response.json()
                        except Exception:
                            err = {"detail": response.text}

                        st.error(f"❌ API Error: {response.status_code}")
                        st.error(str(err.get("detail", err)))
                        frontend_logger.error(f"Batch API Error {response.status_code}: {err}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    frontend_logger.error(f"Batch Exception: {str(e)}")

# ==================== TAB 3: HISTORY & STATS ====================
with tab3:
    st.markdown("<h3 style='color: #333; margin-bottom: 1rem;'>Analysis History & Statistics</h3>", unsafe_allow_html=True)
    
    if "history" not in st.session_state or len(st.session_state.history) == 0:
        st.info("📝 No analysis history yet. Perform some analyses to see results here.")
    else:
        history_data = st.session_state.history
        
        # Summary stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Analyses", len(history_data))
        
        with col2:
            positive_count = sum(1 for h in history_data if h["sentiment"] == "Positive")
            st.metric("Positive", positive_count)
        
        with col3:
            negative_count = sum(1 for h in history_data if h["sentiment"] == "Negative")
            st.metric("Negative", negative_count)
        
        st.divider()
        
        # History table
        st.markdown("### 📋 Recent Analyses")
        
        history_df = []
        for h in reversed(history_data[-20:]):  # Last 20
            history_df.append({
                "Time": h["timestamp"],
                "Tweet": h["text"][:50] + "..." if len(h["text"]) > 50 else h["text"],
                "Sentiment": h["sentiment"],
                "Confidence": f"{h.get('confidence_pct', 0):.1f}%",
                "Passed": "✅" if h.get("meets_threshold") else "⚠️"
            })
        
        df = pd.DataFrame(history_df)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Charts
        st.divider()
        st.markdown("### 📊 Analysis Distribution")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            sentiment_dist = {"Positive": 0, "Negative": 0, "Neutral": 0}
            for h in history_data:
                sentiment_dist[h["sentiment"]] = sentiment_dist.get(h["sentiment"], 0) + 1
            
            fig = px.pie(
                values=list(sentiment_dist.values()),
                names=list(sentiment_dist.keys()),
                color_discrete_map={
                    "Positive": "#27ae60",
                    "Negative": "#e74c3c",
                    "Neutral": "#95a5a6"
                }
            )
            fig.update_layout(height=350, title="Sentiment Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            confidence_avg = sum(h.get("confidence", 0) for h in history_data) / len(history_data)
            passed_count = sum(1 for h in history_data if h.get("meets_threshold"))
            
            fig = go.Figure(data=[
                go.Bar(
                    x=["Passed Threshold", "Below Threshold"],
                    y=[passed_count, len(history_data) - passed_count],
                    marker=dict(color=["#27ae60", "#e74c3c"])
                )
            ])
            fig.update_layout(height=350, title="Threshold Analysis", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 4: METRICS ====================
with tab4:
    st.markdown("<h3 style='color: #333; margin-bottom: 1rem;'>System Metrics & Performance</h3>", unsafe_allow_html=True)
    
    try:
        metrics_response = requests.get(f"{api_base_url}/metrics-summary", timeout=5).json()
        logs_response = requests.get(f"{api_base_url}/logs", timeout=5).json()
        
        # Metrics summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Predictions",
                metrics_response.get("counters", {}).get("total_predictions", 0)
            )
        
        with col2:
            st.metric(
                "Total Requests",
                metrics_response.get("counters", {}).get("total_api_requests", 0)
            )
        
        with col3:
            st.metric(
                "Total Errors",
                metrics_response.get("counters", {}).get("total_errors", 0)
            )
        
        with col4:
            st.metric(
                "Error Rate",
                f"{metrics_response.get('error_rate_percent', 0):.1f}%"
            )
        
        st.divider()
        
        # System info
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🖥️ System Status")
            st.info(f"""
            **Model Loaded:** {'✅ Yes' if metrics_response.get('model_loaded') else '⚠️ Using Fallback'}
            
            **Last Prediction:** {metrics_response.get('last_prediction', 'Never')}
            """)
        
        with col2:
            st.markdown("### 📊 Logging Statistics")
            st.info(f"""
            **Predictions Logged:** {logs_response.get('total_predictions', 0)}
            
            **Performance Entries:** {logs_response.get('performance_entries', 0)}
            
            **Log Size:** {logs_response.get('api_log_size_mb', 0):.2f} MB
            """)
        
    except:
        st.error("❌ Cannot fetch metrics from backend")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem; font-size: 0.9rem;'>
    <p>🐦 <strong>Twitter Sentiment Analyzer</strong> | Powered by FastAPI & Streamlit</p>
    <p>Built with ❤️ using BERTweet model and advanced NLP techniques</p>
    <p style='font-size: 0.8rem; color: #999;'>Last Updated: 2026-05-29</p>
</div>
""", unsafe_allow_html=True)
