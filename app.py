# <!-- VERCEL BEST PRACTICES START -->
## Best practices for developing on Vercel
# - Treat Vercel Functions as stateless + ephemeral (no durable RAM/FS, use Supabase cloud database instead of SQLite)
# - Store secrets in Vercel Env Variables (st.secrets); not in git or hardcoded strings
# - Tune Fluid Compute knobs (maxDuration) for long I/O-heavy API database Realtime streams
# <!-- VERCEL BEST PRACTICES END -->

import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, timedelta, timezone
import plotly.express as px
import time

# 1. Config oo la jaanqaadaya Vercel Fluid Compute Settings
st.set_page_config(page_title="Real-Time IoT Dashboard", layout="wide")

st.title("🔋 Real-Time PostgreSQL SCADA Dashboard")
st.write("Live telemetry environmental streams from remote Supabase cloud")

# 2. Isku-xirka Supabase Credentials (Vercel Secure Environment Variables)
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_eDskTzDraePwlaXa5Y3z5Q_fUe4O-Lk")

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

# 3. Soo Jiidashada Xogta Snapshot-ka hore
def get_latest_telemetry(window_minutes=10):
    try:
        recent = (datetime.now(timezone.utc) - timedelta(minutes=window_minutes)).isoformat()
        
        response = supabase.table("Telemetry Metric Averages")\
            .select("device_id, metric, timestamp, value, unit, status")\
            .gte("timestamp", recent)\
            .order("timestamp", ascending=False)\
            .limit(100)\
            .execute()
            
        if response.data:
            df = pd.DataFrame(response.data)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Naqshadaynta Sifiraha Bidix (Sidebar Controls)
st.sidebar.header("📡 Live Stream Control")
window = st.sidebar.slider("Time window (minutes)", 1, 60, 15)
chart_type = st.sidebar.selectbox("Select Chart Type", ["Line", "Bar", "Area"])

# Auto-refresh loop engine si loogu ekaysiiyo Real-time WebSocket Stream dhanka UI-ga
# Tani waxay si toos ah u cusbooneysiisaa UI-ga 3-dii sekanba mar iyadoo aan la riixin badanka refresh
refresh_rate = st.sidebar.slider("Refresh rate (seconds)", 2, 10, 3)

# 4. Main Data Processing Logic
df_telemetry = get_latest_telemetry(window)

# Kaararka Tirokoobka ee Sare (Top Stats Row)
col1, col2, col3 = st.columns(3)
with col1:
    active_devices = df_telemetry["device_id"].unique().tolist() if not df_telemetry.empty else []
    st.metric("Nodes Discovered", len(active_devices))
with col2:
    if not df_telemetry.empty:
        latest_time = df_telemetry['timestamp'].max()
        st.metric("Latest Signal Pulse", latest_time.strftime("%H:%M:%S"))
    else:
        st.metric("Latest Signal Pulse", "No data")
with col3:
    # Xisaabi inta xogood ee CRITICAL ah (Aan caadiga ahayn)
    anomalies = 0
    if not df_telemetry.empty:
        anomalies = df_telemetry[(df_telemetry['status'] == 'CRITICAL') | (df_telemetry['value'].astype(float) > 240)].shape[0]
    st.metric("System Anomalies", anomalies)

st.divider()

# 5. Qaybta Jaantusyada Dynamic-ga ah (Plotly Charts - MIDAB CAGAAR AH)
st.subheader("📊 Selected Duration Trends")
if not df_telemetry.empty:
    df_chart = df_telemetry.groupby(['timestamp', 'metric'])['value'].sum().reset_index()

    # Palette midabyo cagaar ah oo kala duwan (Green SCADA Theme)
    green_palette = ['#10b981', '#059669', '#34d399', '#6ee7b7', '#a7f3d0']

    if chart_type == "Bar":
        fig = px.bar(df_chart, x="timestamp", y="value", color="metric", barmode="group", 
                     template="plotly_dark", color_discrete_sequence=green_palette)
    elif chart_type == "Line":
        fig = px.line(df_chart, x="timestamp", y="value", color="metric", 
                      template="plotly_dark", color_discrete_sequence=green_palette)
    else:
        fig = px.area(df_chart, x="timestamp", y="value", color="metric", 
                      template="plotly_dark", color_discrete_sequence=green_palette)

    fig.update_layout(
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        legend_title_text="Metrics"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Awaiting upcoming telemetry environment packets...")

st.divider()

# Telemetry data table grid
st.subheader("📋 Active SCADA Bus Interface")
if not df_telemetry.empty:
    available_cols = [c for c in ["device_id", "metric", "value", "unit", "timestamp", "status"] if c in df_telemetry.columns]
    st.dataframe(df_telemetry[available_cols], use_container_width=True)
else:
    st.info("No telemetry data available in the selected time window.")

# 6. Automatic Loop Interceptor
time.sleep(refresh_rate)
st.rerun()
