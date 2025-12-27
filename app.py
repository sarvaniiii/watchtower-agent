import streamlit as st
import json
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from agent_watchtower import WatchtowerAgent
from config import MOCK_LOCATIONS

# Page configuration
st.set_page_config(
    page_title="🛰️ Watchtower Agent",
    page_icon="🛰️",
    layout="wide"
)

# Initialize agent
@st.cache_resource
def get_agent():
    return WatchtowerAgent()

agent = get_agent()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .alert-critical {
        background-color: #ff4d4d;
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        font-weight: bold;
    }
    .alert-warning {
        background-color: #ffcc00;
        padding: 1rem;
        border-radius: 0.5rem;
        color: black;
        font-weight: bold;
    }
    .alert-safe {
        background-color: #4CAF50;
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        font-weight: bold;
    }
    .agent-card {
        background-color: #000000;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🛰️ Watchtower Controls")
    
    st.subheader("Agent Configuration")
    use_mock = st.checkbox("Use Mock Data", value=True, help="Use simulated disaster data")
    auto_scan = st.checkbox("Auto-scan Mode", value=False, help="Continuously monitor locations")
    
    st.subheader("Monitoring Settings")
    selected_location = st.selectbox("Select Location", MOCK_LOCATIONS)
    
    scan_interval = st.slider("Scan Interval (seconds)", 5, 60, 10, 
                            disabled=not auto_scan)
    
    if st.button("🚀 Manual Scan", type="primary", use_container_width=True):
        st.session_state.manual_scan = True
    
    if st.button("🔄 Reset Alerts", type="secondary", use_container_width=True):
        st.session_state.alerts = []
        st.session_state.last_scan = None
        st.rerun()

# Initialize session state
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = None

# Main header
st.markdown('<h1 class="main-header">🛰️ Watchtower Agent - DAOsaster Response System</h1>', unsafe_allow_html=True)

# Dashboard layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🌍 Real-time Monitoring")
    
    # Status indicators
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        total_alerts = len(st.session_state.alerts)
        st.metric("Total Alerts", total_alerts)
    
    with status_col2:
        critical_alerts = len([a for a in st.session_state.alerts if a.get('status') == 'CRITICAL'])
        st.metric("Critical Alerts", critical_alerts, delta=None)
    
    with status_col3:
        last_scan_time = st.session_state.last_scan or "Never"
        st.metric("Last Scan", last_scan_time)
    
    # Monitoring area
    st.markdown("### Current Location Monitor")
    
    with st.expander("📍 Monitoring Details", expanded=True):
        st.info(f"Currently monitoring: **{selected_location}**")
        
        if auto_scan or st.session_state.get('manual_scan'):
            with st.spinner("Scanning for disaster signals..."):
                # Fetch data
                data = agent.fetch_signal(selected_location, use_mock=use_mock)
                time.sleep(1)  # Simulate processing
                
                # Analyze
                severity = agent.analyze_signal(data)
                
                # Generate alert
                alert = agent.generate_alert(severity, data)
                
                # Emit log
                log_message = agent.emit_log(alert, data)
                
                # Store in session
                st.session_state.alerts.insert(0, alert)
                st.session_state.last_scan = datetime.now().strftime("%H:%M:%S")
                
                # Display result
                if severity == "CRITICAL":
                    st.markdown(f'<div class="alert-critical">{log_message}</div>', unsafe_allow_html=True)
                elif severity == "WARNING":
                    st.markdown(f'<div class="alert-warning">{log_message}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="alert-safe">✅ No threats detected in {selected_location}</div>', unsafe_allow_html=True)
                
                # Show raw data
                with st.expander("View Raw Sensor Data"):
                    st.json(data)
                
                st.session_state.manual_scan = False

with col2:
    st.subheader("📊 Alert Dashboard")
    
    if st.session_state.alerts:
        # Create alert dataframe
        df_alerts = pd.DataFrame(st.session_state.alerts)
        
        # Display recent alerts
        st.markdown("### Recent Alerts")
        for alert in st.session_state.alerts[:5]:
            status_color = {
                "CRITICAL": "🔴",
                "WARNING": "🟡",
                "SAFE": "🟢"
            }.get(alert['status'], "⚪")
            
            st.markdown(f"""
            <div class="agent-card">
                {status_color} **{alert['status']}** - {alert['location']}<br>
                <small>Type: {alert['event_type']} | {alert['timestamp'][11:19]}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Alert statistics
        st.markdown("### Alert Statistics")
        if not df_alerts.empty:
            status_counts = df_alerts['status'].value_counts()
            
            fig = go.Figure(data=[go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=.3,
                marker_colors=['#ff4d4d', '#ffcc00', '#4CAF50']
            )])
            fig.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No alerts yet. Run a scan to begin monitoring.")

# Alert Log Section
st.markdown("---")
st.subheader("📜 Alert Log")

if st.session_state.alerts:
    log_df = pd.DataFrame(st.session_state.alerts)
    
    # Format for display
    display_df = log_df[['alert_id', 'timestamp', 'status', 'location', 'event_type', 'severity']].copy()
    display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    st.dataframe(
        display_df,
        column_config={
            "status": st.column_config.TextColumn(
                "Status",
                help="Alert status",
                width="small"
            ),
            "severity": st.column_config.TextColumn(
                "Severity Level",
                help="Severity level",
                width="small"
            )
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Export option
    if st.button("📥 Export Alerts as JSON"):
        alerts_json = json.dumps(st.session_state.alerts, indent=2)
        st.download_button(
            label="Download JSON",
            data=alerts_json,
            file_name=f"watchtower_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
else:
    st.info("Alert log is empty. Run scans to populate.")

# Agent Information
with st.expander("🤖 Agent Information"):
    st.markdown("""
    ### Watchtower Agent (Agent A)
    
    **Core Purpose:** Acts as the "eyes and ears" of the DAOsaster response system by continuously monitoring external disaster signals.
    
    **Key Functions:**
    1. **fetch_signal()** - Pulls disaster data from APIs or mock sources
    2. **analyze_signal()** - Applies safety thresholds to classify severity
    3. **generate_alert()** - Creates standardized alert payloads
    4. **emit_log()** - Generates human-readable logs for monitoring
    
    **Next in Pipeline:** Alerts are forwarded to Agent B (Auditor) for verification.
    """)

# Auto-scan functionality
if auto_scan:
    time.sleep(scan_interval)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("*🛰️ Watchtower Agent v1.0 | Part of DAOsaster Response System*")