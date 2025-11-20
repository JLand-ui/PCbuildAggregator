import streamlit as st
import requests

# 1. Set this to your Triform HTTP endpoint after deploying
API_URL = "https://YOUR-TRIFORM-INSTANCE/api/execute/Build%20Price%20Aggregator/flow"

st.title("PC Build Price Aggregator 💻💸")

st.markdown("""
Paste your Prisjakt.nu links for each component below.  
Leave blank if you don't have a component.
""")

part_fields = [
    ("CPU", "cpu_url"),
    ("GPU", "gpu_url"),
    ("RAM", "ram_url"),
    ("Motherboard", "motherboard_url"),
    ("PSU", "psu_url"),
    ("Hard Drive", "hard_drive_url"),
]

user_inputs = {}
for label, field in part_fields:
    user_inputs[field] = st.text_input(f"{label} Prisjakt URL", key=field)

if st.button("Calculate Build Price"):
    # Filter out empty links
    payload = {k: v for k, v in user_inputs.items() if v.strip()}

    if not payload:
        st.warning("Please enter at least one Prisjakt link.")
    else:
        with st.spinner("Fetching prices..."):
            try:
                resp = requests.post(API_URL, json=payload, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                if "error" in data:
                    st.error(f"Error: {data['error']}")
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
            except Exception as e:
                st.error(f"Failed to get prices: {e}")

st.markdown("""
---
**How it works:**  
- Paste Prisjakt product links for each part.
- Click "Calculate Build Price".
- The app fetches the historical and current prices for each component and sums them up.

*Powered by Triform AI Agent Platform*
""")
