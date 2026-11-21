import streamlit as st

import core

st.title("Festive gift boxes")
st.caption("Diwali, weddings, Eid, corporate gifting — ready to send.")

gifts = core.products(core.GIFTS)
cols = st.columns(4)
for col, p in zip(cols, gifts):
    with col:
        core.product_card(p, "gift")

st.divider()
st.header("Build your own gift box")
st.caption("Pick any 4 dry fruits (100g each), choose a box and add a message.")

options = [core.product(pid) for pid in core.BOX_ITEMS]
options = [p for p in options if p["stock"]]
labels = {p["id"]: f"{p['name']} — {core.rs(core.box_price(p['id']))} / 100g" for p in options}

left, right = st.columns([3, 2], gap="large")
with left:
    chosen = st.multiselect("1. Choose exactly 4 dry fruits", list(labels), format_func=labels.get,
                            max_selections=4, key="box_items", placeholder="Pick 4 items")
    if chosen:
        pc = st.columns(4)
        for c, pid in zip(pc, chosen):
            p = core.product(pid)
            c.markdown(core.art_img(p["kind"]), unsafe_allow_html=True)
            c.caption(p["name"])
    style = st.radio("2. Box style", list(core.BOX_STYLES), horizontal=True, key="box_style",
                     format_func=lambda s: f"{s} (+{core.rs(core.BOX_STYLES[s])})")
    msg = st.text_area("3. Gift message (optional)", max_chars=140, key="box_msg",
                       placeholder="Happy Diwali from the Sharma family!")

with right:
    with st.container(border=True):
        st.markdown(core.art_img("gift", "#d89a2b", height=120), unsafe_allow_html=True)
        total = sum(core.box_price(p) for p in chosen) + core.BOX_STYLES[style]
        st.markdown(f"**Your box:** {len(chosen)}/4 items · {style} box")
        st.markdown(f"<span class='dg-price'>{core.rs(total if chosen else 0)}</span>", unsafe_allow_html=True)

        def add_box():
            items = st.session_state.box_items
            m = st.session_state.box_msg.strip()
            detail = ", ".join(core.product(i)["name"] for i in items) + (f' · Msg: "{m}"' if m else "")
            price = sum(core.box_price(i) for i in items) + core.BOX_STYLES[st.session_state.box_style]
            core.add_to_cart(dict(key=f"box|{len(core.cart())}|{detail}", id="custom-box",
                                  name=f"Custom Gift Box ({st.session_state.box_style})", variant="4 × 100g",
                                  detail=detail, price=price, kind="gift", color="#d89a2b"))
            st.session_state.box_items = []
            st.session_state.box_msg = ""

        st.button("Add gift box to cart" if len(chosen) == 4 else f"Pick {4 - len(chosen)} more",
                  type="primary", width="stretch", disabled=len(chosen) != 4, on_click=add_box)

st.info("🏢 Corporate or bulk orders (25+ boxes)? Message us on WhatsApp for custom branding and bulk rates.")
st.link_button("Ask about bulk gifting on WhatsApp",
               core.wa_link("Hi Dryfruit Ghar! I'm interested in bulk / corporate gift boxes."))
