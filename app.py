import streamlit as st
import pandas as pd
import plotly.express as px
from data import stations
from utils import filter_and_sort, reverse_geocode
from streamlit_js_eval import get_geolocation

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Smart LPG Finder", layout="wide")

# ----------------- TITLE -----------------
st.title("🔥 Smart LPG Cylinder Finder (AI Powered)")

# ----------------- LOCATION -----------------
st.subheader("📍 Your Location")

location = get_geolocation()

if location:
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]
    place = reverse_geocode(lat, lon)
    st.success(f"Detected Location: {place}")
else:
    st.warning("⚠️ Location access denied. Using default Hyderabad.")
    lat, lon = 17.385, 78.486
    place = "Hyderabad"

# ----------------- USER INPUTS -----------------
st.sidebar.header("⚙️ Preferences")

brand = st.sidebar.selectbox("Select Brand", ["HP", "Indane", "Bharat"])
budget = st.sidebar.slider("Budget (₹)", 800, 1200, 950)

# ----------------- FIND STATIONS -----------------
if st.sidebar.button("Find Stations"):
    user_loc = (lat, lon)

    results = filter_and_sort(stations, user_loc, brand, budget)

    if results:
        st.success("✅ Best Stations Found")

        df = pd.DataFrame(results)

        # ================== 🧠 AI INSIGHTS ==================
        st.subheader("🧠 Smart Insights")

        cheapest = df.loc[df["price"].idxmin()]
        nearest = df.loc[df["distance"].idxmin()]
        highest_stock = df.loc[df["quantity"].idxmax()]

        st.info(f"""
💡 Insights:
- Cheapest: {cheapest['name']} (₹{cheapest['price']})
- Nearest: {nearest['name']} ({nearest['distance']} km)
- Highest Stock: {highest_stock['name']} ({highest_stock['quantity']} cylinders)
""")

        # ================== 📊 METRICS ==================
        col1, col2, col3 = st.columns(3)

        col1.metric("🏪 Total Stations", len(df))
        col2.metric("📦 Total Cylinders", int(df["quantity"].sum()))
        col3.metric("💰 Avg Price", f"₹{int(df['price'].mean())}")

        st.divider()

        # ================== 📊 BAR CHART ==================
        st.subheader("📊 Cylinder Availability Comparison")

        fig_bar = px.bar(
            df,
            x="name",
            y="quantity",
            text="quantity"
        )

        st.plotly_chart(fig_bar, use_container_width=True)

        # ================== 📊 SCATTER ==================
        st.subheader("📊 Price vs Distance vs Availability")

        fig_scatter = px.scatter(
            df,
            x="distance",
            y="price",
            size="quantity",
            color="brand",
            hover_name="name"
        )

        st.plotly_chart(fig_scatter, use_container_width=True)

        st.divider()

        # ================== 📋 DETAILS ==================
        st.subheader("📋 Station Details")

        for i, r in enumerate(results):
            if i == 0:
                st.success(f"🏆 Best Choice: {r['name']}")

            st.markdown(f"""
### 🏪 {r['name']}
- 💰 Price: ₹{r['price']}
- 📍 Distance: {r['distance']} km
- 📦 Cylinders: {r['quantity']}
""")

        st.divider()

        # ================== 🗺️ MAP ==================
        st.subheader("🗺️ Live Map View")

        map_df = pd.DataFrame(results)
        map_df["type"] = "Station"

        user_df = pd.DataFrame([
            {"lat": lat, "lon": lon, "type": "You", "quantity": 60, "name": "You"}
        ])

        full_df = pd.concat([map_df, user_df])

        fig_map = px.scatter_mapbox(
            full_df,
            lat="lat",
            lon="lon",
            color="type",
            size="quantity",
            hover_name="name",
            zoom=12,
            height=600,
            color_discrete_map={
                "You": "blue",        # 🔵 User
                "Station": "red"      # 🔴 Stations
            }
        )

        fig_map.update_layout(
            mapbox_style="open-street-map",
            legend_title="Legend",
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

        st.plotly_chart(fig_map, use_container_width=True)

    else:
        st.error("❌ No stations found")