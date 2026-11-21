import re
from datetime import datetime

import streamlit as st

import core

ICON = {"New": "🟡", "Confirmed": "🔵", "Packed": "🟣", "Shipped": "🚚", "Delivered": "✅", "Cancelled": "❌"}

st.title("Track your order")
st.caption("Enter the mobile number you ordered with. Add the order ID to see just one order.")

saved = st.session_state.get("customer", {})
with st.form("track"):
    c1, c2 = st.columns(2)
    phone = c1.text_input("Mobile number", value=saved.get("phone", ""), max_chars=10)
    oid = c2.text_input("Order ID (optional)", placeholder="DG261121-AB12")
    go = st.form_submit_button("Find my orders", type="primary")

if go or st.session_state.get("track_phone"):
    phone = phone.strip() if go else st.session_state["track_phone"]
    if not re.fullmatch(r"[6-9]\d{9}", phone):
        st.error("Enter a valid 10-digit mobile number.")
        st.stop()
    st.session_state["track_phone"] = phone
    found = core.find_orders(phone, oid if go and oid.strip() else None)
    if not found:
        st.warning("No orders found for that number. Check the number or message us on WhatsApp.")
    for o in found:
        with st.container(border=True):
            a, b = st.columns([3, 1])
            when = datetime.fromisoformat(o["created_at"]).strftime("%d %b %Y, %I:%M %p")
            a.markdown(f"**{o['id']}** · <span class='dg-muted'>{when}</span>", unsafe_allow_html=True)
            b.markdown(f"**{ICON.get(o['status'], '')} {o['status']}**")
            steps = core.STATUSES[:5]
            if o["status"] in steps:
                st.progress((steps.index(o["status"]) + 1) / len(steps))
            st.caption(" · ".join(f"{i['name']} ({i['variant']}) × {i['qty']}" for i in o["items"]))
            st.write(f"**{core.rs(o['total'])}** · {core.PAYMENTS[o['payment']]} · {o['pay_status']}")
            st.link_button("Ask about this order on WhatsApp", core.wa_link(f"Hi, I'd like an update on my order {o['id']}"))
