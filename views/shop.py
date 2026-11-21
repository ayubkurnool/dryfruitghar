import streamlit as st

import core

st.markdown(f"""<div class="dg-hero"><div>
<h1>Handpicked dry fruits,<br><em>delivered fresh</em> to your door.</h1>
<p>Premium almonds, cashews, dates, figs and festive gift boxes — packed fresh in small batches and delivered across
Karnataka, Tamil Nadu and Andhra Pradesh.</p>
<div class="chips"><span>✓ Cash on Delivery</span><span>✓ UPI</span><span>✓ Cards &amp; Netbanking</span><span>✓ Order on WhatsApp</span></div>
</div><img src="{core.hero_svg()}" alt=""></div>""", unsafe_allow_html=True)

st.subheader("Shop by category")
c1, c2 = st.columns([3, 2], vertical_alignment="bottom")
with c1:
    cat = st.pills("Category", ["All"] + list(core.CATEGORIES.values()), default="All", label_visibility="collapsed") or "All"
with c2:
    q = st.text_input("Search", placeholder="🔍 Search almonds, dates, figs…", label_visibility="collapsed")

items = core.products(core.CATALOG)
if cat != "All":
    key = next(k for k, v in core.CATEGORIES.items() if v == cat)
    items = [p for p in items if p["cat"] == key]
if q.strip():
    ql = q.strip().lower()
    items = [p for p in core.products() if ql in p["name"].lower() or ql in p["desc"].lower()]

if not items:
    st.info(f"No products match “{q}”. Try “almonds” or “dates”.")
else:
    ncol = 4
    for i in range(0, len(items), ncol):
        cols = st.columns(ncol)
        for col, p in zip(cols, items[i:i + ncol]):
            with col:
                core.product_card(p, "shop")

st.markdown("""<div class="dg-trust">
<div>🌰<b>Premium grades</b>W320 cashews, Nonpareil almonds, Mamra &amp; Ajwa.</div>
<div>📦<b>Packed fresh</b>Small-batch, nitrogen-flushed zip pouches.</div>
<div>🚚<b>3 states, 2–5 days</b>Karnataka, Tamil Nadu, Andhra Pradesh.</div>
<div>💬<b>WhatsApp support</b>Order, track and ask — all on WhatsApp.</div></div>""", unsafe_allow_html=True)
st.page_link("views/gifts.py", label="Looking for festive gifts? See our gift boxes →", icon="🎁")
