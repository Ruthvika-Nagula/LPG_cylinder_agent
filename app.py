import streamlit as st
import pandas as pd
from data import stations
from utils import filter_and_sort
from streamlit_js_eval import get_geolocation

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="LPG Finder", layout="centered")

# ----------------- TITLE -----------------
st.title("🔥 Smart LPG Cylinder Finder")

# ----------------- AUTO LOCATION -----------------
st.subheader("📍 Detecting Your Location...")

location = get_geolocation()

if location:
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]

    st.success(f"Location detected: ({round(lat,4)}, {round(lon,4)})")
    st.caption("📍 Your location detected automatically using browser GPS")

else:
    st.warning("⚠️ Location access denied. Please enter manually.")

    lat = st.number_input("Enter your Latitude", value=17.385)
    lon = st.number_input("Enter your Longitude", value=78.486)

# ----------------- USER INPUTS -----------------
st.subheader("⚙️ Preferences")

brand = st.selectbox("Select Brand", ["HP", "Indane", "Bharat"])
budget = st.slider("Select Budget (₹)", 800, 1200, 950)

# ----------------- FIND STATIONS -----------------
if st.button("Find Stations"):
    user_loc = (lat, lon)

    results = filter_and_sort(stations, user_loc, brand, budget)

    if results:
        st.success("✅ Best stations for you 👇")

        # 💡 Explanation (INTERVIEW GOLD)
        st.info("💡 Results are sorted by lowest price first, then nearest distance")

        # ----------------- DISPLAY RESULTS -----------------
        for i, r in enumerate(results):

            # 🏆 Highlight Best Choice
            if i == 0:
                st.success(f"🏆 Best Choice: {r['name']}")

            st.markdown(f"""
### 🏪 {r['name']}
- 💰 **Price:** ₹{r['price']}
- 📍 **Distance:** {r['distance']} km
- 📦 **Available Cylinders:** {r['quantity']}
""")

        # ----------------- MAP -----------------
        st.subheader("📍 Stations on Map")

        map_data = pd.DataFrame([
            {"lat": r["lat"], "lon": r["lon"]} for r in results
        ])

        st.map(map_data)

    else:
        st.error("❌ No stations found. Try increasing your budget or changing brand.")