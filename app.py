import streamlit as st
import pandas as pd
import plotly.express as px
from data import stations
from utils import *
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="Smart LPG Finder", layout="wide")

st.title("🔥 Smart LPG Cylinder Finder (AI Agent)")

# ---------------- LOCATION ----------------
location = get_geolocation()

if location:
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]
else:
    lat, lon = 17.385, 78.486

# ---------------- ANALYTICS ----------------
st.subheader("📊 Overall LPG Analytics")

df_all = pd.DataFrame(stations)
brand_counts = df_all.groupby("brand")["quantity"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("HP Cylinders", int(brand_counts.get("HP", 0)))
col2.metric("Indane Cylinders", int(brand_counts.get("Indane", 0)))
col3.metric("Bharat Cylinders", int(brand_counts.get("Bharat", 0)))

fig = px.pie(df_all, names="brand", values="quantity")
st.plotly_chart(fig)

st.divider()

# ---------------- SESSION STATE ----------------
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Preferences")
brand = st.sidebar.selectbox("Brand", ["HP", "Indane", "Bharat"])
budget = st.sidebar.slider("Budget", 800, 1200, 950)

# ---------------- RUN ----------------
if st.sidebar.button("Find Best Option"):
    st.session_state.search_clicked = True

if st.session_state.search_clicked:

    results = filter_and_sort(stations, (lat, lon), brand, budget)

    if results:
        best = results[0]

        st.markdown("### 🎯 Personalized Recommendation")

        st.success(f"""
🏆 Best Choice: {best['name']}

💰 Price: ₹{best['price']}
📍 Distance: {best['distance']} km
📦 Stock: {best['quantity']}

💡 Recommendation based on price, distance, and availability
""")

        df = pd.DataFrame(results)

        fig = px.scatter(df, x="distance", y="price", size="quantity", color="brand")
        st.plotly_chart(fig)

        st.subheader("📋 Available Stations")

        for r in results:
            st.markdown(f"""
🏪 {r['name']}  
💰 Price: ₹{r['price']}  
📍 Distance: {r['distance']} km  
📦 Stock: {r['quantity']}  
---
""")

    # ---------------- PRODUCTS ----------------
    st.divider()
    st.subheader("🛒 Smart Alternatives")

    products = get_products()
    cheapest = products[0] if products else None

    if cheapest:
        st.success(f"💡 Cheapest Option: {cheapest['name']} (₹{cheapest['price']})")

        for p in products:
            st.markdown(f"""
🛒 {p['name']}  
💰 ₹{p['price']}  
🛍 {p['platform']}  
🔗 [Buy Now]({p['link']})
---
""")
    else:
        st.warning("⚠️ No valid products found from apps")

    # ---------------- EMAIL ----------------
    st.subheader("📨 Share Recommendation")
    with st.form("email_form", clear_on_submit=True):
        email_to_send = st.text_input("📧 Enter your email to receive this recommendation")
        submit_mail = st.form_submit_button("Send Email")
        
        if submit_mail:
            if not email_to_send:
                st.warning("⚠️ Please enter an email address.")
            else:
                lpg_msg = f"Name: {best['name']}\nPrice: ₹{best['price']}\nDistance: {best['distance']} km\nStock: {best['quantity']}" if results else "Not Available Near You"
                alt_msg = f"Name: {cheapest['name']}\nPrice: ₹{cheapest['price']}\nPlatform: {cheapest['platform']}\nLink to Buy: {cheapest['link']}" if cheapest else "No alternatives found"
                
                msg = f"""
Hello from Smart LPG Finder!

Here is your personalized LPG and alternative recommendation summary:

🔥 Best LPG Direct Option:
{lpg_msg}

🛒 Recommended Alternative (Best Value):
{alt_msg}
"""
                if send_email(email_to_send, msg):
                    st.success("✅ Email sent successfully!")
                else:
                    st.error("❌ Email failed to send. Check configuration or app password.")