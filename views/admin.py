import hmac
import json
from datetime import datetime

import pandas as pd
import streamlit as st

import core

DEFAULT_PW = "change-me-now"
password = core._secret("ADMIN_PASSWORD", DEFAULT_PW)

st.title("Shop admin")

if not st.session_state.get("is_admin"):
    with st.form("login"):
        pw = st.text_input("Admin password", type="password")
        if st.form_submit_button("Log in", type="primary"):
            if hmac.compare_digest(pw, password):
                st.session_state["is_admin"] = True
                st.rerun()
            else:
                st.error("Wrong password.")
    if password == DEFAULT_PW:
        st.caption("First run: the password is `change-me-now`. Set ADMIN_PASSWORD in your app's Secrets before sharing the link.")
    st.stop()

top = st.columns([4, 1])
if top[1].button("Log out", width="stretch"):
    st.session_state["is_admin"] = False
    st.rerun()
if password == DEFAULT_PW:
    st.warning("You're using the default admin password. Set **ADMIN_PASSWORD** in Secrets (see README).", icon="⚠️")
if core.using_sqlite():
    st.warning("Orders are saved in a local SQLite file. On Streamlit Community Cloud this file is wiped whenever the "
               "app restarts or sleeps. Add a free Postgres **DATABASE_URL** in Secrets before taking real orders "
               "(see README).", icon="💾")

settings = st.session_state["settings"]
orders = core.all_orders()
today = datetime.now(core.IST).date()
live = [o for o in orders if o["status"] != "Cancelled"]
todays = [o for o in live if datetime.fromisoformat(o["created_at"]).date() == today]

m = st.columns(4)
m[0].metric("Orders today", len(todays))
m[1].metric("Sales today", core.rs(sum(o["total"] for o in todays)))
m[2].metric("To pack / ship", sum(o["status"] in ("New", "Confirmed", "Packed") for o in orders))
m[3].metric("All-time sales", core.rs(sum(o["total"] for o in live)))

tab_o, tab_p, tab_s = st.tabs(["📦 Orders", "🌰 Products & stock", "⚙️ Settings"])

# ------------------------------------------------------------------ orders
with tab_o:
    c1, c2, c3 = st.columns([2, 2, 1], vertical_alignment="bottom")
    flt = c1.selectbox("Status", ["All"] + core.STATUSES)
    search = c2.text_input("Search name, phone or order ID")
    c3.button("🔄 Refresh", width="stretch")
    shown = [o for o in orders if (flt == "All" or o["status"] == flt)]
    if search.strip():
        s = search.strip().lower()
        shown = [o for o in shown if s in o["name"].lower() or s in o["phone"] or s in o["id"].lower()]
    if orders:
        df = pd.DataFrame([{**{k: o[k] for k in ("id", "created_at", "name", "phone", "address", "city", "state", "pincode",
                                                   "total", "payment", "pay_status", "status", "note")},
                            "items": "; ".join(f"{i['name']} {i['variant']} x{i['qty']}" for i in o["items"])} for o in orders])
        st.download_button("⬇️ Download all orders (CSV)", df.to_csv(index=False).encode(), "dryfruit-ghar-orders.csv", "text/csv")
    if not shown:
        st.info("No orders here yet. New orders appear when you refresh.")
    for o in shown:
        when = datetime.fromisoformat(o["created_at"]).strftime("%d %b, %I:%M %p")
        with st.expander(f"{o['id']} · {o['name']} · {core.rs(o['total'])} · {o['status']} · {when}", expanded=o["status"] == "New"):
            a, b = st.columns([3, 2])
            a.markdown(f"**{o['name']}** · 📞 {o['phone']}  \n{o['address']}, {o['city']}, {o['state']} – {o['pincode']}"
                       + (f"  \n📝 {o['note']}" if o["note"] else ""))
            a.markdown("\n".join(f"- {i['name']} ({i['variant']}{', ' + i['detail'] if i.get('detail') else ''}) × {i['qty']} — "
                                 f"{core.rs(i['price'] * i['qty'])}" for i in o["items"]))
            a.markdown(f"Subtotal {core.rs(o['subtotal'])} · Delivery {core.rs(o['shipping'])} · **Total {core.rs(o['total'])}**")
            b.markdown(f"**Payment:** {core.PAYMENTS[o['payment']]}  \n**Payment status:** {o['pay_status']}")
            new_status = b.selectbox("Order status", core.STATUSES, index=core.STATUSES.index(o["status"]), key=f"st-{o['id']}")
            if new_status != o["status"]:
                core.update_order(o["id"], status=new_status)
                st.toast(f"{o['id']} → {new_status}")
                st.rerun()
            if o["payment"] != "COD" and o["pay_status"] != "Paid":
                if b.button("✅ Mark as paid", key=f"paid-{o['id']}"):
                    core.update_order(o["id"], pay_status="Paid")
                    st.rerun()
            cust = core.customer_wa(o["phone"])
            b.link_button("💬 WhatsApp status update", core.wa_link(core.status_message(o), cust), width="stretch")
            if o["payment"] == "Online" and o["pay_status"] != "Paid":
                link = settings.get("pay_link") or "<paste your payment link>"
                b.link_button("💳 Send payment link", core.wa_link(
                    f"Hi {o['name']}, here is your secure payment link for Dryfruit Ghar order {o['id']} "
                    f"({core.rs(o['total'])}): {link}", cust), width="stretch")

# ------------------------------------------------------------------ products
with tab_p:
    st.caption("Edit prices (₹) and stock, then press Save. Blank cells mean that pack size isn't sold.")
    sizes = ["100g", "250g", "500g", "1kg", "Box", "Hamper"]
    prods = core.products()
    rows = [{"id": p["id"], "Product": p["name"], **{s: p["prices"].get(s) for s in sizes}, "In stock": p["stock"]} for p in prods]
    df = pd.DataFrame(rows).set_index("id")
    edited = st.data_editor(df, width="stretch", disabled=["Product"], key="prod_editor",
                            column_config={s: st.column_config.NumberColumn(s, min_value=1, step=1, format="₹%d") for s in sizes})
    if st.button("💾 Save products", type="primary"):
        base = {p["id"]: p for p in core.CATALOG + core.GIFTS}
        n = 0
        for pid, r in edited.iterrows():
            prices = {s: int(r[s]) for s in sizes if s in base[pid]["prices"] and pd.notna(r[s])}
            cur = next(p for p in prods if p["id"] == pid)
            if prices != cur["prices"] or bool(r["In stock"]) != cur["stock"]:
                core.save_override(pid, prices, bool(r["In stock"]))
                n += 1
        if n:
            st.success(f"Saved {n} product(s).")
        else:
            st.info("No changes to save.")

# ------------------------------------------------------------------ settings
with tab_s:
    with st.form("settings_form"):
        c1, c2 = st.columns(2)
        wa = c1.text_input("Shop WhatsApp number (with 91)", settings["whatsapp"])
        upi = c2.text_input("UPI ID", settings["upi"])
        pay_link = st.text_input("Card / netbanking payment page link (Razorpay or Cashfree)", settings.get("pay_link", ""),
                                 placeholder="https://rzp.io/l/yourshop")
        c1, c2, c3 = st.columns(3)
        free = c1.number_input("Free delivery above (₹)", value=int(settings["free_ship"]), min_value=0, step=50)
        fee = c2.number_input("Delivery fee (₹)", value=int(settings["ship_fee"]), min_value=0, step=5)
        cod = c3.number_input("COD limit (₹)", value=int(settings["cod_max"]), min_value=0, step=500)
        notice = st.text_input("Top banner message", settings["notice"])
        if st.form_submit_button("Save settings", type="primary"):
            core.save_settings(dict(whatsapp="".join(ch for ch in wa if ch.isdigit()), upi=upi.strip(), pay_link=pay_link.strip(),
                                    free_ship=int(free), ship_fee=int(fee), cod_max=int(cod), notice=notice.strip()))
            st.success("Settings saved.")
            st.rerun()
