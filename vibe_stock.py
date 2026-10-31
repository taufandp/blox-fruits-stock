import streamlit as st
import streamlit.components.v1 as components
import requests
import ast
import json
import time

st.set_page_config(page_title="Blox Fruits Live Stock", page_icon="🏴‍☠️", layout="wide")

st.markdown("""
<style>
    .creator-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
    }
    .status-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .pill-live {
        background-color: rgba(34, 197, 94, 0.2);
        color: #4ade80;
        border: 1px solid #22c55e;
    }
    .pill-history {
        background-color: rgba(244, 63, 94, 0.2);
        color: #fb7185;
        border: 1px solid #f43f5e;
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

with st.expander("⚙️ Customize Display & Layout", expanded=False):
    set_col1, set_col2 = st.columns(2)
    with set_col1:
        img_size = st.slider("Fruit Image Size (px)", min_value=50, max_value=160, value=85, step=5)
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

    # --- HISTORICAL / LAST STOCK CACHE ENGINE ---
    if "last_normal_stock" not in st.session_state:
        st.session_state.last_normal_stock = []
        st.session_state.last_normal_time = "Initial Load"
    if "last_mirage_stock" not in st.session_state:
        st.session_state.last_mirage_stock = []
        st.session_state.last_mirage_time = "Initial Load"

    if "current_normal_fingerprint" not in st.session_state:
        st.session_state.current_normal_fingerprint = ""
    if "current_mirage_fingerprint" not in st.session_state:
        st.session_state.current_mirage_fingerprint = ""

    norm_fp = json.dumps([f.get("name") for f in normal_stock if isinstance(f, dict)])
    mir_fp = json.dumps([f.get("name") for f in mirage_stock if isinstance(f, dict)])

    # Stock rotation detection
    if st.session_state.current_normal_fingerprint and st.session_state.current_normal_fingerprint != norm_fp:
        st.session_state.last_normal_stock = st.session_state.current_normal_cache
        st.session_state.last_normal_time = time.strftime("%H:%M UTC")

    if st.session_state.current_mirage_fingerprint and st.session_state.current_mirage_fingerprint != mir_fp:
        st.session_state.last_mirage_stock = st.session_state.current_mirage_cache
        st.session_state.last_mirage_time = time.strftime("%H:%M UTC")

    st.session_state.current_normal_fingerprint = norm_fp
    st.session_state.current_normal_cache = normal_stock
    st.session_state.current_mirage_fingerprint = mir_fp
    st.session_state.current_mirage_cache = mirage_stock

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
        .card {{ background: #1e1e2e; border: 1px solid #313244; border-radius: 12px; padding: 14px 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }}
        .title {{ font-size: 0.85rem; color: #a6adc8; font-weight: 600; margin-bottom: 4px; }}
        .digits {{ font-size: 2rem; font-weight: 800; font-family: monospace; letter-spacing: 2px; }}
        .normal-glow {{ color: #89b4fa; text-shadow: 0 0 10px rgba(137, 180, 250, 0.4); }}
        .mirage-glow {{ color: #f5c2e7; text-shadow: 0 0 10px rgba(245, 194, 231, 0.4); }}
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

    # 4 Dynamic Tabs: Live vs Last Stock
    tab_norm, tab_mir, tab_last_norm, tab_last_mir, tab_raw = st.tabs([
        f"🏪 Current Normal ({len(normal_stock)})",
        f"✨ Current Mirage ({len(mirage_stock)})",
        f"📜 Last Normal Stock ({len(st.session_state.last_normal_stock)})",
        f"📜 Last Mirage Stock ({len(st.session_state.last_mirage_stock)})",
        "🛠️ API Inspector"
    ])

    def display_fruits(fruit_list, is_history=False):
        if not fruit_list:
            if is_history:
                st.info("🕒 History will populate automatically as soon as the dealer stock updates!")
            else:
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
                            f'<img src="{img}" width="{img_size}" style="border-radius: 8px; filter: {"grayscale(40%)" if is_history else "none"};">'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    
                    pill_class = "pill-history" if is_history else "pill-live"
                    pill_text = "Previous Stock" if is_history else "In Stock"
                    st.markdown(f'<span class="status-pill {pill_class}">{pill_text}</span>', unsafe_allow_html=True)
                    
                    st.markdown(f"#### {fruit.get('name', 'Fruit')}")
                    st.caption(f"Type: **{fruit.get('type', 'Natural')}**")
                    
                    beli = fruit.get("price_beli", 0)
                    robux = fruit.get("price_robux", 0)
                    st.write(f"💰 **{beli:,} Beli**")
                    st.write(f"🪙 **{robux:,} Robux**")

    with tab_norm:
        display_fruits(normal_stock, is_history=False)

    with tab_mir:
        display_fruits(mirage_stock, is_history=False)

    with tab_last_norm:
        st.caption(f"Recorded rotation timestamp: `{st.session_state.last_normal_time}`")
        display_fruits(st.session_state.last_normal_stock, is_history=True)

    with tab_last_mir:
        st.caption(f"Recorded rotation timestamp: `{st.session_state.last_mirage_time}`")
        display_fruits(st.session_state.last_mirage_stock, is_history=True)

    with tab_raw:
        st.json(raw_data)

    st.markdown('<div class="footer">Made with 🔥 • Created by a 6A student • Powered by Argon</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"API Error: {e}")
