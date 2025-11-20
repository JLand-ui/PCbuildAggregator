import streamlit as st
import requests
from datetime import datetime

# 1. Set your Triform HTTP endpoint (from ENDPOINT PATH in Triform)
API_URL = "https://nexus.triform.ai/api/in/5088e1d4-45c2-403c-859d-377f77dcb76f/9412e01c-8566-4150-a7d6-1455497d7788"

# 2. Paste your ingress token here (from Triform Endpoints panel)
INGRESS_TOKEN = "be58aeecca41477157f1f22cf283bffa33c15483"

st.title("PC Build Price Aggregator 💻💸")

st.markdown("""
Paste your Prisjakt.nu links for each component below.  
Leave blank if you don't have a component.
""")

part_fields = [
    ("CPU", "cpu_link"),
    ("GPU", "gpu_link"),
    ("RAM", "ram_link"),
    ("Motherboard", "motherboard_link"),
    ("PSU", "psu_link"),
    ("Hard Drive", "harddrive_link"),
]

user_inputs = {}
for label, field in part_fields:
    user_inputs[field] = st.text_input(f"{label} Prisjakt URL", key=field)

# Persistent log (session state)
if "logs" not in st.session_state:
    st.session_state.logs = []

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {msg}")

if st.button("Calculate Build Price"):
    # Filter out empty links
    payload = {k: v for k, v in user_inputs.items() if v.strip()}
    log(f"Form submitted. Payload: {payload}")

    if not payload:
        msg = "Please enter at least one Prisjakt link."
        st.warning(msg)
        log(f"Warning: {msg}")
    else:
        with st.spinner("Fetching prices..."):
            try:
                headers = {
                    "Authorization": f"Bearer {INGRESS_TOKEN}"
                }
                resp = requests.post(API_URL, json=payload, headers=headers, timeout=60)
                log(f"Sent POST to API: {API_URL}")
                resp.raise_for_status()
                data = resp.json()
                log(f"Received response: {data}")

                if "error" in data:
                    st.error(f"Error: {data['error']}")
                    log(f"API Error: {data['error']}")
                else:
                    # Display results
                    results = data.get("results", [])
                    if results:
                        st.subheader("Component Prices (SEK)")
                        st.table([
                            {
                                "Part": r.get("name", "Unknown"),
                                "Current": r.get("current_price", "-"),
                                "6mo Ago": r.get("price_6mo_ago", "-"),
                                "1yr Ago": r.get("price_1yr_ago", "-"),
                            }
                            for r in results
                        ])
                    st.subheader("Total Build Cost (SEK)")
                    st.write(f"**Current:** {data.get('total_current', '-')}")
                    st.write(f"**6 months ago:** {data.get('total_6mo_ago', '-')}")
                    st.write(f"**1 year ago:** {data.get('total_1yr_ago', '-')}")
                    log("Query successful.")
            except Exception as e:
                st.error(f"Failed to get prices: {e}")
                log(f"Exception: {e}")

# Log window (shows after form)
with st.expander("Logs", expanded=False):
    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        if st.button("Clear logs", key="clear_logs"):
            st.session_state.logs = []
            st.experimental_rerun()
    with col1:
        if st.session_state.logs:
            for i, logmsg in enumerate(st.session_state.logs):
                st.write(f"{i+1}. {logmsg}")
        else:
            st.write("No logs yet.")

st.markdown("""
---
**How it works:**  
- Paste Prisjakt product links for each part.
- Click "Calculate Build Price".
- The app fetches the historical and current prices for each component and sums them up.

*Powered by Triform AI Agent Platform*
""")
