import streamlit as st
import streamlit.components.v1 as components
import requests
import ast
import json

st.set_page_config(page_title="Blox Fruits Live Stock", page_icon="🏴‍☠️", layout="wide")

st.markdown("""
<style>
    .creator-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        color: #888888;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("🏴‍☠️ Blox Fruits Live Stock")
    st.markdown('<div class="creator-badge">⚡ Created by a 6A student • Powered by Argon</div>', unsafe_allow_html=True)
with col_btn:
    st.write("")
    if st.button("🔄 Force Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with st.expander("⚙️ Customize Layout", expanded=True):
    set_col1, set_col2 = st.columns(2)
    with set_col1:
        img_size = st.slider("Fruit Image Size (px)", min_value=50, max_value=150, value=80, step=5)
    with set_col2:
        num_columns = st.slider("Columns per Row", min_value=2, max_value=6, value=4, step=1)

API_URL = "https://api.parse.bot/scraper/e534d388-6640-4c19-b9b6-b2ba12930793/get_stock"
HEADERS = {
    "X-API-Key": "pmx_079c6a54d75c014fe96a4f7e655d16c8",
    "API-Snapshot-Version": "2"
}

def deep_parse(val):
    if isinstance(val, str):
        val_str = val.strip()
        if (val_str.startswith("[") and val_str.endswith("]")) or (val_str.startswith("{") and val_str.endswith("}")):
            try:
                return deep_parse(json.loads(val_str))
            except Exception:
                try:
                    return deep_parse(ast.literal_eval(val_str))
                except Exception:
                    return val
    elif isinstance(val, dict):
        return {k: deep_parse(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [deep_parse(x) for x in val]
    return val

def find_key(obj, target_key):
    if isinstance(obj, dict):
        if target_key in obj:
            return obj[target_key]
        for v in obj.values():
            res = find_key(v, target_key)
            if res is not None:
                return res
    elif isinstance(obj, list):
        for item in obj:
            res = find_key(item, target_key)
            if res is not None:
                return res
    return None

@st.cache_data(ttl=60)
def fetch_stock():
    res = requests.get(API_URL, headers=HEADERS, timeout=15)
    res.raise_for_status()
    return deep_parse(res.json())

try:
    raw_data = fetch_stock()

    normal_stock = find_key(raw_data, "normal") or []
    mirage_stock = find_key(raw_data, "mirage") or []
    normal_reset = find_key(raw_data, "normal_next_reset") or {}
    mirage_reset = find_key(raw_data, "mirage_next_reset") or {}

    if not isinstance(normal_stock, list): normal_stock = []
    if not isinstance(mirage_stock, list): mirage_stock = []

    normal_iso = normal_reset.get("reset_at", "") if isinstance(normal_reset, dict) else ""
    mirage_iso = mirage_reset.get("reset_at", "") if isinstance(mirage_reset, dict) else ""
    normal_rem_sec = normal_reset.get("remaining_seconds", 0) if isinstance(normal_reset, dict) else 0
    mirage_rem_sec = mirage_reset.get("remaining_seconds", 0) if isinstance(mirage_reset, dict) else 0

    timer_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; padding: 0; background: transparent; font-family: -apple-system, sans-serif; color: white; }}
        .timer-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
        .card {{ background: #1e1e2e; border: 1px solid #313244; border-radius: 12px; padding: 14px 20px; }}
        .title {{ font-size: 0.85rem; color: #a6adc8; font-weight: 600; margin-bottom: 4px; }}
        .digits {{ font-size: 2rem; font-weight: 800; font-family: monospace; letter-spacing: 2px; }}
        .normal-glow {{ color: #89b4fa; }}
        .mirage-glow {{ color: #f5c2e7; }}
    </style>
    </head>
    <body>
        <div class="timer-grid">
            <div class="card">
                <div class="title">⏳ NORMAL DEALER RESET IN</div>
                <div id="n-clock" class="digits normal-glow">Loading...</div>
            </div>
            <div class="card">
                <div class="title">🌙 MIRAGE DEALER RESET IN</div>
                <div id="m-clock" class="digits mirage-glow">Loading...</div>
            </div>
        </div>
        <script>
            const startT = Date.now();
            function getRem(iso, sec, intvHours) {{
                if (iso && iso.length > 5) {{
                    const target = new Date(iso).getTime();
                    if (!isNaN(target)) {{
                        const d = Math.floor((target - Date.now()) / 1000);
                        if (d > 0) return d;
                    }}
                }}
                if (sec > 0) {{
                    const r = sec - Math.floor((Date.now() - startT) / 1000);
                    if (r > 0) return r;
                }}
                const now = new Date();
                const h = now.getUTCHours();
                const nextH = (Math.floor(h / intvHours) + 1) * intvHours;
                const nextR = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), nextH, 0, 0, 0));
                return Math.max(0, Math.floor((nextR.getTime() - now.getTime()) / 1000));
            }}
            function fmt(s) {{
                const hr = Math.floor(s / 3600);
                const mn = Math.floor((s % 3600) / 60);
                const sc = s % 60;
                return [hr, mn, sc].map(v => String(v).padStart(2, '0')).join(':');
            }}
            function tick() {{
                document.getElementById('n-clock').innerText = fmt(getRem("{normal_iso}", Number("{normal_rem_sec}") || 0, 4));
                document.getElementById('m-clock').innerText = fmt(getRem("{mirage_iso}", Number("{mirage_rem_sec}") || 0, 2));
            }}
            tick(); setInterval(tick, 1000);
        </script>
    </body>
    </html>
    """
    components.html(timer_html, height=105)

    st.divider()

    tab_normal, tab_mirage, tab_debug = st.tabs([f"🏪 Normal Stock ({len(normal_stock)})", f"✨ Mirage Stock ({len(mirage_stock)})", "🛠️ Raw API Inspector"])

    def display_fruits(fruit_list):
        if not fruit_list:
            st.warning("No fruits currently listed.")
            return
        
        cols = st.columns(num_columns)
        for idx, fruit in enumerate(fruit_list):
            if not isinstance(fruit, dict): continue
            with cols[idx % num_columns]:
                with st.container(border=True):
                    img = fruit.get("image_url") or fruit.get("image")
                    if img:
                        st.markdown(
                            f'<div style="text-align: center; margin-bottom: 8px;">'
                            f'<img src="{img}" width="{img_size}" style="border-radius: 8px;">'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    st.markdown(f"#### {fruit.get('name', 'Fruit')}")
                    st.caption(f"Type: **{fruit.get('type', 'Natural')}**")
                    
                    beli = fruit.get("price_beli", 0)
                    robux = fruit.get("price_robux", 0)
                    st.write(f"💰 **{beli:,} Beli**")
                    st.write(f"🪙 **{robux:,} Robux**")

    with tab_normal:
        display_fruits(normal_stock)
    with tab_mirage:
        display_fruits(mirage_stock)
    with tab_debug:
        st.json(raw_data)

    st.markdown('<div class="footer">Made with 🔥 • Created by a 6A student • Powered by Argon</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"API Error: {e}")
