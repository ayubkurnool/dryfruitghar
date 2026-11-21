"""Dryfruit Ghar — online dry fruit shop (Streamlit)."""
import streamlit as st

import core

st.set_page_config(page_title="Dryfruit Ghar — Premium Dry Fruits Online", page_icon="🌰", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap" rel="stylesheet">
<style>
h1,h2,h3{font-family:'Fraunces',Georgia,serif!important;color:#3b2414!important;letter-spacing:-.01em}
.block-container{padding-top:4.2rem;max-width:1200px}
.dg-notice{background:#3b2414;color:#f3c564;text-align:center;font-size:14px;padding:7px 12px;border-radius:10px;font-weight:500;margin-bottom:6px}
.dg-hero{background:radial-gradient(900px 300px at 85% 0%,#f6dca8 0,transparent 60%),linear-gradient(135deg,#3b2414,#5a3720);
  border-radius:22px;padding:34px 34px;display:flex;gap:24px;align-items:center;color:#fff;margin:6px 0 10px}
.dg-hero h1{color:#fff!important;font-size:clamp(28px,4.2vw,46px);line-height:1.12;margin:0 0 10px;padding:0}
.dg-hero h1 em{color:#f3c564;font-style:normal}
.dg-hero p{color:#ecdcc8;font-size:16.5px;max-width:540px;margin:0}
.dg-hero .chips{display:flex;gap:16px;flex-wrap:wrap;margin-top:16px;font-size:14px;color:#ecdcc8}
.dg-hero img{width:min(320px,34vw);flex-shrink:0}
.dg-art{position:relative}
.dg-badge{position:absolute;top:8px;left:8px;background:#d89a2b;color:#3b2414;font-size:11.5px;font-weight:700;padding:2px 10px;border-radius:999px}
.dg-price{font-weight:700;font-size:19px;color:#3b2414}
.dg-muted{color:#7a6656;font-size:13px}
.dg-trust{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:8px}
.dg-trust div{background:#fff;border:1px solid #eadfce;border-radius:14px;padding:14px;font-size:14px;color:#7a6656}
.dg-trust b{display:block;color:#2b1a0e;font-size:16px;margin:4px 0 2px}
.dg-wa{position:fixed;right:20px;bottom:22px;z-index:999;width:56px;height:56px;border-radius:50%;background:#1fa855;display:grid;place-items:center;box-shadow:0 8px 24px rgba(31,168,85,.4)}
.dg-oid{font-family:ui-monospace,monospace;background:#fff;border:1px dashed #d89a2b;border-radius:8px;padding:3px 10px;font-weight:700}
div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-radius:16px}
.st-key-mobnav{display:none}
@media (max-width:700px){
  .st-key-mobnav{display:block;position:sticky;top:3.2rem;z-index:50;background:#fbf6ee;padding:4px 0}
  .st-key-mobnav [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:6px}
  .st-key-mobnav [data-testid="stColumn"]{min-width:0!important;flex:1 1 0!important}
  .st-key-mobnav a{background:#fff;border:1px solid #eadfce;border-radius:999px;justify-content:center;padding:4px 2px}
  .st-key-mobnav a p{font-size:13px!important;font-weight:600}
  .dg-hero{flex-direction:column-reverse;padding:22px}
  .dg-hero img{width:200px}
  .dg-trust{grid-template-columns:1fr 1fr}
}
</style>""", unsafe_allow_html=True)

settings = core.get_settings()
st.session_state["settings"] = settings
count = core.totals(settings)["count"]

pages = [
    st.Page("views/shop.py", title="Shop", icon="🛍️", default=True, url_path="shop"),
    st.Page("views/gifts.py", title="Gift Boxes", icon="🎁", url_path="gifts"),
    st.Page("views/cart.py", title=f"Cart ({count})" if count else "Cart", icon="🛒", url_path="cart"),
    st.Page("views/orders.py", title="Track Order", icon="📦", url_path="track"),
    st.Page("views/admin.py", title="Admin", icon="🔐", url_path="admin"),
]
nav = st.navigation(pages, position="top")

if settings.get("notice"):
    st.markdown(f"<div class='dg-notice'>{settings['notice']}</div>", unsafe_allow_html=True)

st.markdown(f"""<a class="dg-wa" href="{core.wa_link('Hi Dryfruit Ghar! I have a question.')}" target="_blank" title="Chat on WhatsApp">
<svg width="28" height="28" viewBox="0 0 24 24" fill="#fff"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.3-.7-2.8-1.1-4.5-3.9-4.7-4.1-.1-.2-1.1-1.5-1.1-2.8s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.4.6-.4.4c-.1.2-.3.3-.1.6.2.3.8 1.4 1.8 2.2 1.2 1.1 2.2 1.4 2.5 1.6.3.1.5.1.6-.1l.9-1.1c.2-.3.4-.2.7-.1l2 .9c.3.1.5.2.5.3.1.1.1.7-.1 1.3z"/></svg></a>""",
            unsafe_allow_html=True)

with st.container(key="mobnav"):
    m = st.columns(4)
    m[0].page_link(pages[0], label="Shop", icon="🛍️")
    m[1].page_link(pages[1], label="Gifts", icon="🎁")
    m[2].page_link(pages[3], label="Track", icon="📦")
    m[3].page_link(pages[2], label=f"Cart {count}" if count else "Cart", icon="🛒")

nav.run()

st.divider()
st.caption(f"© 2026 Dryfruit Ghar · Delivering across Karnataka, Tamil Nadu & Andhra Pradesh · "
           f"WhatsApp +{settings['whatsapp']} · Prices include GST")
