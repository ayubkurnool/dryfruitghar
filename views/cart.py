import io
import urllib.parse
from datetime import datetime

import qrcode
import streamlit as st

import core

settings = st.session_state["settings"]


def change_qty(idx: int, delta: int):
    c = core.cart()
    c[idx]["qty"] += delta
    if c[idx]["qty"] < 1:
        c.pop(idx)


def upi_uri(o):
    return (f"upi://pay?pa={urllib.parse.quote(settings['upi'])}&pn={urllib.parse.quote('Dryfruit Ghar')}"
            f"&am={int(o['total'])}&cu=INR&tn={urllib.parse.quote(o['id'])}")


def qr_png(text: str) -> bytes:
    img = qrcode.make(text, box_size=7, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------- confirmation
if "last_order" in st.session_state:
    o = st.session_state["last_order"]
    st.success("Order placed! Thank you for shopping with Dryfruit Ghar.", icon="✅")
    st.markdown(f"### Order ID <span class='dg-oid'>{o['id']}</span>", unsafe_allow_html=True)
    st.write(f"Total **{core.rs(o['total'])}** · {core.PAYMENTS[o['payment']]}")
    if o["payment"] == "UPI":
        c1, c2 = st.columns([1, 2], vertical_alignment="center")
        c1.image(qr_png(upi_uri(o)), caption=f"Scan to pay {core.rs(o['total'])}", width=220)
        c2.markdown(f"Pay with any UPI app to **{settings['upi']}** and add **{o['id']}** as the note.\n\n"
                    "On your phone? Tap below to open your UPI app directly.")
        c2.markdown(f"<a href='{upi_uri(o)}'>Open UPI app →</a>", unsafe_allow_html=True)
    elif o["payment"] == "Online":
        if settings.get("pay_link"):
            st.link_button(f"💳 Pay {core.rs(o['total'])} securely (card / netbanking / wallet)", settings["pay_link"], type="primary")
            st.caption(f"Enter {o['id']} as the reference on the payment page.")
        else:
            st.info("💳 We'll send you a secure payment link on WhatsApp after confirming your order. "
                    "Your order ships once payment is received.")
    else:
        st.info("💵 Pay cash (or UPI) to the delivery partner when your order arrives.")
    st.write("Send your order to us on WhatsApp so we can confirm it quickly"
             + (" — attach your payment screenshot." if o["payment"] == "UPI" else "."))
    c1, c2 = st.columns(2)
    c1.link_button("Send order on WhatsApp", core.wa_link(core.order_text(o)), type="primary", width="stretch")
    if c2.button("Continue shopping", width="stretch"):
        del st.session_state["last_order"]
        st.switch_page("views/shop.py")
    st.caption("Track this order anytime on the **Track Order** page with your mobile number.")
    st.stop()

# ---------------------------------------------------------------- cart
st.title("Your cart")
items = core.cart()
if not items:
    st.info("Your cart is empty.")
    st.page_link("views/shop.py", label="Start shopping →", icon="🛍️")
    st.stop()

for idx, i in enumerate(items):
    with st.container(border=True):
        a, b, c, d = st.columns([1, 4, 2, 1.4], vertical_alignment="center")
        a.markdown(core.art_img(i["kind"], i.get("color"), height=60), unsafe_allow_html=True)
        b.markdown(f"**{i['name']}**  \n<span class='dg-muted'>{i['variant']}"
                   f"{' · ' + i['detail'] if i.get('detail') else ''}</span>", unsafe_allow_html=True)
        q1, q2, q3 = c.columns(3, vertical_alignment="center")
        q1.button("−", key=f"m{idx}", on_click=change_qty, args=(idx, -1))
        q2.markdown(f"<div style='text-align:center;font-weight:700'>{i['qty']}</div>", unsafe_allow_html=True)
        q3.button("+", key=f"p{idx}", on_click=change_qty, args=(idx, 1))
        d.markdown(f"**{core.rs(i['price'] * i['qty'])}**")

t = core.totals(settings)
left = settings["free_ship"] - t["sub"]
if left > 0:
    st.info(f"Add {core.rs(left)} more for FREE delivery 🚚")
else:
    st.success("🎉 You've unlocked free delivery")

m1, m2, m3 = st.columns(3)
m1.metric("Subtotal", core.rs(t["sub"]))
m2.metric("Delivery", core.rs(t["ship"]) if t["ship"] else "FREE")
m3.metric("Total", core.rs(t["total"]))

wa_text = ("Hi Dryfruit Ghar! I'd like to order:\n"
           + "\n".join(f"• {i['name']} ({i['variant']}) × {i['qty']} = {core.rs(i['price'] * i['qty'])}" for i in items)
           + f"\nTotal: {core.rs(t['total'])}\n\nName:\nAddress:\nPincode:")
st.link_button("Prefer WhatsApp? Order there instead", core.wa_link(wa_text))

# ---------------------------------------------------------------- checkout
st.header("Checkout")
saved = st.session_state.get("customer", {})
states = list(core.STATES)
with st.form("checkout"):
    c1, c2 = st.columns(2)
    name = c1.text_input("Full name *", value=saved.get("name", ""))
    phone = c2.text_input("Mobile (WhatsApp) *", value=saved.get("phone", ""), max_chars=10, placeholder="10-digit number")
    address = st.text_area("Address (house, street, area) *", value=saved.get("address", ""), height=80)
    c1, c2, c3 = st.columns(3)
    city = c1.text_input("City *", value=saved.get("city", ""))
    state = c2.selectbox("State *", states, index=states.index(saved["state"]) if saved.get("state") in states else None,
                         placeholder="Select state")
    pincode = c3.text_input("Pincode *", value=saved.get("pincode", ""), max_chars=6)
    note = st.text_input("Delivery note (optional)", placeholder="Landmark, preferred time…")
    pay_opts = ["UPI", "Online"] + (["COD"] if t["total"] <= settings["cod_max"] else [])
    payment = st.radio("Payment method", pay_opts, format_func=core.PAYMENTS.get, horizontal=True)
    if t["total"] > settings["cod_max"]:
        st.caption(f"Cash on Delivery is available for orders up to {core.rs(settings['cod_max'])}.")
    submit = st.form_submit_button(f"Place order · {core.rs(t['total'])}", type="primary", width="stretch")

st.caption("We deliver only to Karnataka, Tamil Nadu and Andhra Pradesh. Delivery in 2–5 working days.")

if submit:
    form = dict(name=name, phone=phone, address=address, city=city, state=state or "", pincode=pincode)
    err = core.validate_checkout(form)
    if err:
        st.error(err)
    else:
        cust = {k: v.strip() for k, v in form.items()}
        st.session_state["customer"] = cust
        order = dict(id=core.new_order_id(), created_at=datetime.now(core.IST).isoformat(timespec="seconds"), **cust,
                     note=note.strip(), items=[{k: i.get(k, "") for k in ("name", "variant", "detail", "qty", "price")} for i in items],
                     subtotal=t["sub"], shipping=t["ship"], total=t["total"], payment=payment,
                     pay_status="Pay on delivery" if payment == "COD" else "Awaiting payment", status="New")
        try:
            core.save_order(order)
        except Exception as e:  # noqa: BLE001
            st.error(f"Sorry, we couldn't save your order. Please send it on WhatsApp instead. ({type(e).__name__})")
            st.stop()
        st.session_state["cart"] = []
        st.session_state["last_order"] = order
        st.rerun()
