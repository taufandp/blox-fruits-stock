import streamlit as st
import requests
import ast
import json

st.set_page_config(page_title="Blox Fruits Live Stock", page_icon="🏴‍☠️", layout="wide")

st.markdown("""
<style>
    .stMetric {
        background-color: #1e1e2e;
        padding: 15px;
        border-radius: 10px;
    }
    .creator-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 15px;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        color: #888888;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏴‍☠️ Blox Fruits Live Stock")
st.markdown('<div class="creator-badge">⚡ Created by a 6A student</div>', unsafe_allow_html=True)

API_URL = "https://api.parse.bot/scraper/e534d388-6640-4c19-b9b6-b2ba12930793/get_stock"
HEADERS = {
    "X-API-Key": "pmx_079c6a54d75c014fe96a4f7e655d16c8",
    "API-Snapshot-Version": "2"
}

@st.cache_data(ttl=60)
def fetch_stock():
    res = requests.get(API_URL, headers=HEADERS, timeout=10)
    res.raise_for_status()
    return res.json()

def clean_api_node(node):
    """Parses stringified lists/dicts if the API double-encoded them."""
    if isinstance(node, str):
        try:
            return ast.literal_eval(node)
        except Exception:
            try:
                return json.loads(node.replace("'", '"'))
            except Exception:
                return []
    return node

try:
    raw_data = fetch_stock()

    data = raw_data
    if isinstance(raw_data, dict):
        if "data" in raw_data:
            data = raw_data["data"]
        elif "results" in raw_data and isinstance(raw_data["results"], list) and len(raw_data["results"]) > 0:
            data = raw_data["results"][0]

    normal_stock = clean_api_node(data.get("normal", []))
    mirage_stock = clean_api_node(data.get("mirage", []))
    normal_reset = clean_api_node(data.get("normal_next_reset", {}))
    mirage_reset = clean_api_node(data.get("mirage_next_reset", {}))

    # 1. Timers section
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.metric("⏳ Normal Dealer Reset In", normal_reset.get("remaining", "Unknown") if isinstance(normal_reset, dict) else "Unknown")
    with col_t2:
        st.metric("🌙 Mirage Dealer Reset In", mirage_reset.get("remaining", "Unknown") if isinstance(mirage_reset, dict) else "Unknown")

    st.divider()

    # 2. Tabs for Normal vs Mirage Stock
    tab_normal, tab_mirage = st.tabs(["🏪 Normal Stock", "✨ Mirage Stock"])

    def display_fruits(fruit_list):
        if not fruit_list or not isinstance(fruit_list, list):
            st.warning("No fruits currently in stock!")
            return
        
        cols = st.columns(4)
        for idx, fruit in enumerate(fruit_list):
            if not isinstance(fruit, dict):
                continue
            with cols[idx % 4]:
                with st.container(border=True):
                    # Centered, compact image
                    if fruit.get("image_url"):
                        st.markdown(
                            f'<div style="text-align: center; margin-bottom: 10px;">'
                            f'<img src="{fruit["image_url"]}" width="100" style="border-radius: 8px;">'
                            f'</div>', 
                            unsafe_allow_html=True
                        )
                    
                    st.markdown(f"### {fruit.get('name', 'Fruit')}")
                    st.caption(f"Type: {fruit.get('type', 'Unknown')}")
                    
                    price_beli = fruit.get('price_beli', 0)
                    price_robux = fruit.get('price_robux', 0)
                    st.write(f"💰 **{price_beli:,} Beli**")
                    st.write(f"🪙 **{price_robux:,} Robux**")

    with tab_normal:
        st.subheader("Normal Dealer Fruits")
        display_fruits(normal_stock)

    with tab_mirage:
        st.subheader("Mirage Dealer Fruits")
        display_fruits(mirage_stock)

    # 3. Footer
    st.markdown('<div class="footer">Made with 🔥 • Created by a 6A student</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Failed to fetch data from API: {e}")