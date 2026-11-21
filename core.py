"""Shared catalog, database and helpers for Dryfruit Ghar."""
from __future__ import annotations

import base64
import json
import random
import re
import string
import urllib.parse
from datetime import datetime, timezone, timedelta

import streamlit as st
from sqlalchemy import (Boolean, Column, Float, MetaData, String, Table, Text,
                        create_engine, select, update, insert, delete)

IST = timezone(timedelta(hours=5, minutes=30))

# ----------------------------------------------------------------- catalog
CATEGORIES = {"nuts": "Nuts", "dried": "Dried Fruits", "dates": "Dates", "snacks": "Seeds & Snacks"}

CATALOG = [
    dict(id="almond", name="California Almonds", cat="nuts", kind="almond", desc="Crunchy, sweet Nonpareil grade almonds.", prices={"250g": 299, "500g": 579, "1kg": 1099}, badge="Bestseller"),
    dict(id="mamra", name="Mamra Almonds", cat="nuts", kind="almond", desc="Iranian Mamra — rich, oily, the king of almonds.", prices={"250g": 749, "500g": 1449, "1kg": 2799}, badge="Premium"),
    dict(id="cashew", name="Cashews W320", cat="nuts", kind="cashew", desc="Whole, creamy cashews from Goa & Mangaluru.", prices={"250g": 329, "500g": 639, "1kg": 1249}, badge="Bestseller"),
    dict(id="pista", name="Roasted Pistachios", cat="nuts", kind="pista", desc="Lightly salted, in-shell Iranian pistachios.", prices={"250g": 449, "500g": 869, "1kg": 1699}),
    dict(id="walnut", name="Walnut Kernels", cat="nuts", kind="walnut", desc="Light-halves Kashmiri walnut kernels.", prices={"250g": 399, "500g": 769, "1kg": 1499}),
    dict(id="blackraisin", name="Afghan Black Raisins", cat="dried", kind="raisin", desc="Seedless, iron-rich and naturally sweet.", prices={"250g": 199, "500g": 379, "1kg": 729}),
    dict(id="goldraisin", name="Golden Raisins", cat="dried", kind="graisin", desc="Plump Nashik golden kishmish.", prices={"250g": 149, "500g": 279, "1kg": 539}),
    dict(id="anjeer", name="Anjeer (Dried Figs)", cat="dried", kind="fig", desc="Soft, jumbo Afghan anjeer.", prices={"250g": 449, "500g": 869, "1kg": 1699}),
    dict(id="apricot", name="Turkish Apricots", cat="dried", kind="apricot", desc="Sun-dried, pitted, honey-sweet.", prices={"250g": 299, "500g": 579, "1kg": 1119}),
    dict(id="cranberry", name="Dried Cranberries", cat="dried", kind="cranberry", desc="Tangy-sweet, great for baking & trail mix.", prices={"250g": 279, "500g": 539, "1kg": 1049}),
    dict(id="medjool", name="Medjool Dates", cat="dates", kind="date", desc="Large, soft, caramel-like Jordanian Medjool.", prices={"500g": 699, "1kg": 1349}, badge="Popular"),
    dict(id="kimia", name="Kimia Dates", cat="dates", kind="datedark", desc="Soft, juicy Iranian black dates.", prices={"500g": 349, "1kg": 679}),
    dict(id="ajwa", name="Ajwa Dates", cat="dates", kind="datedark", desc="Premium Madinah Ajwa dates.", prices={"250g": 549, "500g": 1049}),
    dict(id="makhana", name="Peri-Peri Makhana", cat="snacks", kind="makhana", desc="Roasted fox nuts, light and crunchy.", prices={"100g": 149, "250g": 349}),
    dict(id="seeds", name="Super Seeds Mix", cat="snacks", kind="seeds", desc="Pumpkin, sunflower, flax & chia seeds.", prices={"250g": 249, "500g": 479}),
    dict(id="trailmix", name="Classic Trail Mix", cat="snacks", kind="mix", desc="Nuts, berries and seeds — the perfect snack.", prices={"250g": 249, "500g": 479}),
]
GIFTS = [
    dict(id="g-diwali", name="Diwali Delight Box", cat="gifts", kind="gift", color="#b3392f", desc="Almonds, cashews, pistachios & raisins in a 4-jar festive box.", prices={"Box": 999}, badge="Festive"),
    dict(id="g-royal", name="Royal Wedding Hamper", cat="gifts", kind="gift", color="#7a1f4b", desc="9 premium dry fruits on a wooden tray with brass lid.", prices={"Hamper": 2499}, badge="Premium"),
    dict(id="g-eid", name="Eid Dates Collection", cat="gifts", kind="gift", color="#1f6b4f", desc="Ajwa, Medjool & Kimia dates with roasted almonds.", prices={"Box": 1299}),
    dict(id="g-corp", name="Corporate Gift Box", cat="gifts", kind="gift", color="#1d3f6e", desc="3 nuts, greeting card, custom sleeve. Bulk rates from 25 boxes.", prices={"Box": 799}),
]
BOX_ITEMS = ["almond", "cashew", "pista", "walnut", "blackraisin", "goldraisin", "anjeer", "apricot", "cranberry", "kimia", "makhana", "seeds"]
BOX_STYLES = {"Kraft": 99, "Velvet": 249, "Wooden": 449}
STATES = {"Karnataka": ("56", "57", "58", "59"), "Tamil Nadu": ("60", "61", "62", "63", "64"), "Andhra Pradesh": ("51", "52", "53")}
STATUSES = ["New", "Confirmed", "Packed", "Shipped", "Delivered", "Cancelled"]
PAYMENTS = {"UPI": "UPI (GPay / PhonePe / Paytm)", "Online": "Card / Netbanking / Wallet", "COD": "Cash on Delivery"}
DEFAULT_SETTINGS = {
    "whatsapp": "919999999999", "upi": "dryfruitghar@upi", "pay_link": "",
    "free_ship": 999, "ship_fee": 49, "cod_max": 5000,
    "notice": "🪔 Festive offer: Free delivery above ₹999 across Karnataka, Tamil Nadu & Andhra Pradesh",
}

# ----------------------------------------------------------------- database
meta = MetaData()
orders_t = Table("orders", meta,
    Column("id", String(32), primary_key=True), Column("created_at", String(40)),
    Column("name", String(120)), Column("phone", String(20)), Column("address", Text),
    Column("city", String(80)), Column("state", String(40)), Column("pincode", String(10)),
    Column("note", Text), Column("items", Text), Column("subtotal", Float), Column("shipping", Float),
    Column("total", Float), Column("payment", String(20)), Column("pay_status", String(30)), Column("status", String(20)))
products_t = Table("product_overrides", meta,
    Column("id", String(40), primary_key=True), Column("prices", Text), Column("stock", Boolean))
settings_t = Table("settings", meta, Column("key", String(40), primary_key=True), Column("value", Text))


def _secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


@st.cache_resource
def engine():
    url = _secret("DATABASE_URL", "sqlite:///dryfruit_ghar.db")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    eng = create_engine(url, pool_pre_ping=True)
    meta.create_all(eng)
    return eng


def using_sqlite() -> bool:
    return engine().url.get_backend_name() == "sqlite"


def get_settings() -> dict:
    s = dict(DEFAULT_SETTINGS)
    with engine().connect() as c:
        for k, v in c.execute(select(settings_t)):
            try:
                s[k] = json.loads(v)
            except Exception:
                s[k] = v
    return s


def save_settings(new: dict):
    with engine().begin() as c:
        for k, v in new.items():
            c.execute(delete(settings_t).where(settings_t.c.key == k))
            c.execute(insert(settings_t).values(key=k, value=json.dumps(v)))


def overrides() -> dict:
    with engine().connect() as c:
        return {r.id: {"prices": json.loads(r.prices or "{}"), "stock": bool(r.stock)} for r in c.execute(select(products_t))}


def save_override(pid: str, prices: dict, stock: bool):
    with engine().begin() as c:
        c.execute(delete(products_t).where(products_t.c.id == pid))
        c.execute(insert(products_t).values(id=pid, prices=json.dumps(prices), stock=stock))


def products(base=None) -> list[dict]:
    ov = overrides()
    out = []
    for p in (base if base is not None else CATALOG + GIFTS):
        o = ov.get(p["id"], {})
        q = dict(p)
        q["prices"] = {**p["prices"], **{k: v for k, v in o.get("prices", {}).items() if k in p["prices"]}}
        q["stock"] = o.get("stock", True)
        out.append(q)
    return out


def product(pid: str) -> dict | None:
    return next((p for p in products() if p["id"] == pid), None)


def new_order_id() -> str:
    return "DG" + datetime.now(IST).strftime("%y%m%d") + "-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))


def save_order(o: dict):
    row = {k: o[k] for k in ("id", "created_at", "name", "phone", "address", "city", "state", "pincode", "note",
                             "subtotal", "shipping", "total", "payment", "pay_status", "status")}
    row["items"] = json.dumps(o["items"])
    with engine().begin() as c:
        c.execute(insert(orders_t).values(**row))


def _row(r) -> dict:
    d = dict(r._mapping)
    d["items"] = json.loads(d["items"] or "[]")
    return d


def all_orders() -> list[dict]:
    with engine().connect() as c:
        return [_row(r) for r in c.execute(select(orders_t).order_by(orders_t.c.created_at.desc()))]


def find_orders(phone: str, order_id: str | None = None) -> list[dict]:
    q = select(orders_t).where(orders_t.c.phone == phone)
    if order_id:
        q = q.where(orders_t.c.id == order_id.strip().upper())
    with engine().connect() as c:
        return [_row(r) for r in c.execute(q.order_by(orders_t.c.created_at.desc()))]


def update_order(oid: str, **vals):
    with engine().begin() as c:
        c.execute(update(orders_t).where(orders_t.c.id == oid).values(**vals))


# ----------------------------------------------------------------- helpers
def rs(n) -> str:
    n = int(round(n or 0))
    s = str(n)
    if len(s) > 3:  # Indian grouping 1,23,456
        head, tail = s[:-3], s[-3:]
        head = re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", head)
        s = head + "," + tail
    return "₹" + s


def wa_link(text: str = "", number: str | None = None) -> str:
    num = re.sub(r"\D", "", number or get_settings()["whatsapp"])
    return f"https://wa.me/{num}" + (f"?text={urllib.parse.quote(text)}" if text else "")


def customer_wa(phone: str) -> str:
    return "91" + re.sub(r"\D", "", phone)[-10:]


def box_price(pid: str) -> int:
    p = product(pid)
    w, v = next(iter(p["prices"].items()))
    grams = float(re.sub(r"[^\d.]", "", w)) * (1000 if "kg" in w else 1)
    return int(round(v / grams * 100 * 1.1 / 5) * 5)


def validate_checkout(f: dict) -> str | None:
    if not f["name"].strip():
        return "Please enter your name."
    if not re.fullmatch(r"[6-9]\d{9}", f["phone"].strip()):
        return "Enter a valid 10-digit Indian mobile number."
    if len(f["address"].strip()) < 8:
        return "Please enter your full address."
    if not f["city"].strip():
        return "Please enter your city."
    if f["state"] not in STATES:
        return "Please select your state."
    if not re.fullmatch(r"\d{6}", f["pincode"].strip()):
        return "Pincode must be 6 digits."
    if not f["pincode"].strip().startswith(STATES[f["state"]]):
        return f"Pincode {f['pincode']} doesn't look like {f['state']}. Please check it."
    return None


def cart() -> list[dict]:
    return st.session_state.setdefault("cart", [])


def add_to_cart(item: dict):
    c = cart()
    for i in c:
        if i["key"] == item["key"]:
            i["qty"] += 1
            break
    else:
        c.append({**item, "qty": 1})
    st.toast(f"Added: {item['name']} ({item['variant']})", icon="🛒")


def totals(settings: dict) -> dict:
    sub = sum(i["price"] * i["qty"] for i in cart())
    ship = 0 if sub == 0 or sub >= settings["free_ship"] else settings["ship_fee"]
    return {"sub": sub, "ship": ship, "total": sub + ship, "count": sum(i["qty"] for i in cart())}


def order_text(o: dict) -> str:
    lines = "\n".join(f"• {i['name']} ({i['variant']}{', ' + i['detail'] if i.get('detail') else ''}) × {i['qty']}" for i in o["items"])
    return (f"New order {o['id']}\n{lines}\nTotal: {rs(o['total'])} · {PAYMENTS[o['payment']]}\n\n"
            f"{o['name']}, {o['phone']}\n{o['address']}, {o['city']}, {o['state']} - {o['pincode']}"
            + (f"\nNote: {o['note']}" if o.get("note") else ""))


def status_message(o: dict) -> str:
    n = o["name"]
    return {
        "New": f"Hi {n}, we've received your Dryfruit Ghar order {o['id']} ({rs(o['total'])}). We'll confirm it shortly.",
        "Confirmed": f"Hi {n}, your order {o['id']} is confirmed! We're packing it fresh for you.",
        "Packed": f"Hi {n}, your order {o['id']} is packed and will ship soon.",
        "Shipped": f"Hi {n}, your order {o['id']} has been shipped! It should reach you in 2–5 days.",
        "Delivered": f"Hi {n}, your order {o['id']} has been delivered. Thank you for shopping with Dryfruit Ghar! 🌰",
        "Cancelled": f"Hi {n}, your order {o['id']} has been cancelled. Please reply if you have any questions.",
    }.get(o["status"], "")


# ----------------------------------------------------------------- artwork
PAL = {"almond": ("#f6e3c8", "#b9773e", "#8a5426"), "cashew": ("#fbefd9", "#f1d9a8", "#d6b57a"),
       "pista": ("#e6f0d8", "#c9a77a", "#86b04a"), "walnut": ("#f1e4d0", "#b88b5a", "#8c6239"),
       "raisin": ("#ece1e6", "#4a2a3a", "#2e1824"), "graisin": ("#fbf0d4", "#d4a03a", "#a97618"),
       "fig": ("#f3e3da", "#9a6a4a", "#7a4a30"), "apricot": ("#fde8d2", "#f0973a", "#d1731c"),
       "cranberry": ("#fbe2e4", "#c22f45", "#8e1d2f"), "date": ("#f2e2d2", "#7a3e1d", "#5a2a10"),
       "datedark": ("#ebdcd4", "#4a2412", "#2e150a"), "makhana": ("#f6efe4", "#fffaf0", "#e5d6bd"),
       "seeds": ("#eef0dc", "#6f8a3a", "#3a3a2a"), "mix": ("#f5e8d6", "#b9773e", "#c22f45")}


def _shape(kind, x, y, r, rot, c1, c2):
    t = f'transform="translate({x} {y}) rotate({rot}) scale({r / 20})"'
    if kind == "almond":
        return f'<g {t}><path d="M0-24C12-14 14 6 0 24-14 6-12-14 0-24z" fill="{c1}"/><path d="M0-18C6-8 6 8 0 18" stroke="{c2}" stroke-width="1.5" fill="none" opacity=".6"/></g>'
    if kind == "cashew":
        return f'<g {t}><path d="M-14-16C-24 0-14 22 6 22c10 0 16-6 14-12-1-5-8-5-12-4-6 1-10-4-8-12 2-8-10-14-14-10z" fill="{c1}" stroke="{c2}" stroke-width="1.5"/></g>'
    if kind == "pista":
        return f'<g {t}><ellipse rx="16" ry="22" fill="{c1}"/><ellipse rx="9" ry="16" fill="{c2}"/><path d="M0-22V22" stroke="#7a5a35" stroke-width="1.2"/></g>'
    if kind == "walnut":
        return f'<g {t}><circle r="20" fill="{c1}"/><path d="M0-20V20M-12-12c6 4 6 8 0 12s-6 8 0 10M12-12c-6 4-6 8 0 12s6 8 0 10" stroke="{c2}" stroke-width="2" fill="none"/></g>'
    if kind in ("raisin", "graisin", "cranberry"):
        return f'<g {t}><ellipse rx="14" ry="18" fill="{c1}"/><path d="M-6-8c4 3 4 10 0 14M5-10c-3 5-2 12 1 16" stroke="{c2}" stroke-width="1.5" fill="none" opacity=".7"/></g>'
    if kind == "fig":
        return f'<g {t}><path d="M0-24c4 0 4 4 4 6 10 4 16 12 16 22 0 12-9 20-20 20s-20-8-20-20c0-10 6-18 16-22 0-2 0-6 4-6z" fill="{c1}"/><circle cx="-6" cy="6" r="1.6" fill="{c2}"/><circle cx="5" cy="10" r="1.6" fill="{c2}"/><circle cx="2" cy="0" r="1.6" fill="{c2}"/></g>'
    if kind == "apricot":
        return f'<g {t}><circle r="20" fill="{c1}"/><path d="M0-18C-6-6-6 6 0 18" stroke="{c2}" stroke-width="2" fill="none"/></g>'
    if kind in ("date", "datedark"):
        return f'<g {t}><ellipse rx="12" ry="24" fill="{c1}"/><path d="M-4-16c3 8 3 22-1 30M5-14c2 6 2 14 0 22" stroke="{c2}" stroke-width="1.5" fill="none" opacity=".7"/></g>'
    if kind == "makhana":
        return f'<g {t}><circle r="18" fill="{c1}" stroke="{c2}" stroke-width="2"/><circle cx="-5" cy="-4" r="5" fill="#c97b4a" opacity=".55"/><circle cx="6" cy="6" r="3" fill="#c97b4a" opacity=".4"/></g>'
    if kind == "seeds":
        return f'<g {t}><ellipse rx="8" ry="16" fill="{c1}"/><ellipse cx="14" cy="6" rx="5" ry="10" fill="{c2}"/><ellipse cx="-13" cy="8" rx="5" ry="9" fill="#8a7a50"/></g>'
    return ""


def art_svg(kind: str, color: str | None = None) -> str:
    if kind == "gift":
        c = color or "#b3392f"
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150"><rect width="200" height="150" fill="#fbeedd"/><circle cx="100" cy="80" r="62" fill="#f6dfbf"/>'
                f'<rect x="52" y="62" width="96" height="62" rx="6" fill="{c}"/><rect x="46" y="48" width="108" height="20" rx="4" fill="{c}" opacity=".85"/>'
                f'<rect x="94" y="48" width="12" height="76" fill="#f3c564"/><rect x="46" y="54" width="108" height="8" fill="#f3c564"/>'
                f'<path d="M100 48c-10-18-30-16-26-4 3 8 26 4 26 4zM100 48c10-18 30-16 26-4-3 8-26 4-26 4z" fill="#f3c564"/></svg>')
    bg, c1, c2 = PAL.get(kind, PAL["mix"])
    if kind == "mix":
        shapes = (_shape("almond", 70, 70, 15, -30, "#b9773e", "#8a5426") + _shape("cashew", 125, 62, 15, 20, "#f1d9a8", "#d6b57a")
                  + _shape("cranberry", 100, 100, 11, 0, "#c22f45", "#8e1d2f") + _shape("pista", 140, 105, 12, 30, "#c9a77a", "#86b04a")
                  + _shape("raisin", 62, 108, 10, 15, "#4a2a3a", "#2e1824"))
    else:
        pos = [(100, 78, 22, -12), (62, 60, 16, 25), (140, 60, 16, -35), (70, 110, 14, 40), (134, 108, 15, -10)]
        shapes = "".join(_shape(kind, *p, c1, c2) for p in pos)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150"><rect width="200" height="150" fill="{bg}"/>'
            f'<circle cx="100" cy="82" r="64" fill="#fff" opacity=".45"/>{shapes}</svg>')


def art_img(kind: str, color: str | None = None, badge: str | None = None, height: int | None = None) -> str:
    b64 = base64.b64encode(art_svg(kind, color).encode()).decode()
    style = f"height:{height}px;width:auto;" if height else "width:100%;"
    badge_html = f'<span class="dg-badge">{badge}</span>' if badge else ""
    return f'<div class="dg-art">{badge_html}<img src="data:image/svg+xml;base64,{b64}" style="{style}border-radius:12px;display:block" alt=""></div>'


def hero_svg() -> str:
    s = _shape
    inner = (s("almond", 140, 225, 24, -30, "#b9773e", "#8a5426") + s("cashew", 210, 205, 26, 15, "#f1d9a8", "#d6b57a")
             + s("pista", 270, 230, 20, 25, "#c9a77a", "#86b04a") + s("date", 175, 190, 20, 60, "#7a3e1d", "#5a2a10")
             + s("apricot", 245, 175, 18, 0, "#f0973a", "#d1731c") + s("walnut", 120, 180, 18, 0, "#b88b5a", "#8c6239")
             + s("cranberry", 295, 190, 12, 10, "#c22f45", "#8e1d2f") + s("raisin", 200, 240, 11, 0, "#4a2a3a", "#2e1824"))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="40 120 320 240"><ellipse cx="200" cy="300" rx="150" ry="34" fill="#2b1a0e" opacity=".35"/>'
           f'<path d="M60 250c0 60 60 90 140 90s140-30 140-90z" fill="#c98a3c"/><path d="M60 250h280" stroke="#8a5426" stroke-width="6"/>{inner}</svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def product_card(p: dict, key_prefix: str):
    """Render one product card with pack-size picker and add button."""
    with st.container(border=True):
        st.markdown(art_img(p["kind"], p.get("color"), "Out of stock" if not p["stock"] else p.get("badge")), unsafe_allow_html=True)
        st.markdown(f"**{p['name']}**")
        st.caption(p["desc"])
        sizes = list(p["prices"].keys())
        size = sizes[0]
        if len(sizes) > 1:
            size = st.pills("Pack", sizes, default=sizes[0], key=f"{key_prefix}-w-{p['id']}", label_visibility="collapsed") or sizes[0]
        c1, c2 = st.columns([1, 1], vertical_alignment="center")
        c1.markdown(f"<span class='dg-price'>{rs(p['prices'][size])}</span> <span class='dg-muted'>/ {size}</span>", unsafe_allow_html=True)
        item = dict(key=f"{p['id']}|{size}", id=p["id"], name=p["name"], variant=size,
                    price=p["prices"][size], kind=p["kind"], color=p.get("color"))
        c2.button("Add" if p["stock"] else "Sold out", key=f"{key_prefix}-add-{p['id']}", disabled=not p["stock"],
                  type="primary", width="stretch", on_click=add_to_cart, args=(item,))
