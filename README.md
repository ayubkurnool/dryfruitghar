# Dryfruit Ghar — Online Shop (Streamlit)

An online dry fruit shop for customers in Karnataka, Tamil Nadu and Andhra Pradesh.

**Customers can:** browse 16 products and 4 festive gift boxes, build a custom 4-item gift box, check out with
**UPI (QR code)**, **Card / Netbanking (payment link)** or **Cash on Delivery**, order on WhatsApp, and track orders
by mobile number.

**You (the owner) can:** log in at the **Admin** page to see orders and sales, change order status, mark payments
as paid, send WhatsApp updates with one tap, download orders as CSV, edit prices and stock, and change your
WhatsApp number, UPI ID, payment link, delivery charges and banner message.

---

## Put it online (about 15 minutes, free)

### Step 1 — Create a free database (so orders are never lost)
Streamlit Community Cloud wipes local files whenever the app restarts, so orders must live in an online database.

1. Go to **https://neon.com** → sign up (free, no card).
2. Create a project (choose region **AWS Asia Pacific (Singapore)** or the closest to India).
3. Click **Connect** and copy the connection string. It looks like
   `postgresql://user:password@ep-xxxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`

### Step 2 — Put the code on GitHub
1. Sign up at **https://github.com** if you don't have an account.
2. Click **New repository** → name it `dryfruit-ghar` → **Create repository**.
3. Click **uploading an existing file**, drag in *everything inside this folder*
   (including the `.streamlit` and `views` folders), then **Commit changes**.
   > Tip: the `.streamlit` folder may be hidden on your computer. On Mac press Cmd+Shift+. in Finder;
   > on Windows turn on *View → Hidden items*. If it doesn't upload, the app still works — just with default colours.
4. **Do not** upload `secrets.toml` or the `.db` file.

### Step 3 — Deploy on Streamlit Community Cloud
1. Go to **https://share.streamlit.io** → **Continue with GitHub**.
2. Click **Create app** → **Deploy a public app from GitHub**.
3. Repository: `your-username/dryfruit-ghar` · Branch: `main` · Main file: `streamlit_app.py`.
4. App URL: choose something like `dryfruitghar` → your shop will be at `https://dryfruitghar.streamlit.app`.
5. Open **Advanced settings → Secrets** and paste (with your own values):
   ```toml
   ADMIN_PASSWORD = "choose-a-strong-password"
   DATABASE_URL = "postgresql://user:password@ep-xxxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
   ```
6. Click **Deploy**. First start takes 2–3 minutes.

### Step 4 — Set up your shop
1. Open your app → **Admin** → log in with your password.
2. **Settings tab:** enter your real WhatsApp number (with 91), UPI ID, and your Razorpay/Cashfree
   payment page link (for card & netbanking).
3. **Products tab:** adjust prices and stock → **Save products**.
4. Place one test order yourself, then check it appears in **Orders**.

---

## Good to know
- **Sleeping:** free Streamlit apps go to sleep after a period with no visitors. The next visitor sees a
  "wake up" button and waits ~30 seconds. Your orders are safe in Neon. If this becomes a problem as you
  grow, move to a paid host (Render, Railway, or a VPS) — the code runs unchanged.
- **Card / netbanking:** create a free *Payment Page* on Razorpay or Cashfree (needs business KYC) and paste
  its link in Settings. Customers pay there and enter their order ID as the reference.
- **Order alerts:** check the Admin page regularly, or ask customers to tap **Send order on WhatsApp** after
  ordering (the confirmation screen prompts them), so every order also reaches your WhatsApp.
- **Licences:** an online food business needs an FSSAI licence/registration and GST registration;
  add refund, shipping and privacy policy text before promoting the site.

## Run on your own computer
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Without `DATABASE_URL` it uses a local `dryfruit_ghar.db` file. Default admin password: `change-me-now`.

## Files
| File | What it is |
|---|---|
| `streamlit_app.py` | App entry: theme, top menu, WhatsApp button |
| `core.py` | Product list, prices, database, helpers |
| `views/shop.py` | Home & product catalogue |
| `views/gifts.py` | Gift boxes & build-your-own box |
| `views/cart.py` | Cart, checkout, payment & confirmation |
| `views/orders.py` | Customer order tracking |
| `views/admin.py` | Owner dashboard |
| `.streamlit/config.toml` | Brand colours |
| `requirements.txt` | Python packages |

To add a new product permanently, add a line to `CATALOG` (or `GIFTS`) in `core.py` and push to GitHub —
the app redeploys automatically.
