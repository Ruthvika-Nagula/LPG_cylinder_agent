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

# ----------------- SIDEBAR -----------------
st.sidebar.header("⚙️ Preferences")
brand = st.sidebar.selectbox("Select Brand", ["HP", "Indane", "Bharat"])
budget = st.sidebar.slider("Budget (₹)", 800, 1200, 950)

# ----------------- SESSION STATE FOR CHART -----------------
if "chart_type" not in st.session_state:
    st.session_state.chart_type = "Bar"

# ----------------- FIND STATIONS -----------------
if st.sidebar.button("Find Stations"):
    st.session_state.results = filter_and_sort(stations, (lat, lon), brand, budget)

# ----------------- DISPLAY RESULTS -----------------
if "results" in st.session_state and st.session_state.results:
    results = st.session_state.results
    df = pd.DataFrame(results)

    st.success("✅ Best Stations Found")

    # ================== 🧠 INSIGHTS ==================
    st.subheader("🧠 Smart Insights")

    cheapest = df.loc[df["price"].idxmin()]
    nearest = df.loc[df["distance"].idxmin()]
    highest_stock = df.loc[df["quantity"].idxmax()]

    st.info(f"""
- Cheapest: {cheapest['name']} (₹{cheapest['price']})
- Nearest: {nearest['name']} ({nearest['distance']} km)
- Highest Stock: {highest_stock['name']} ({highest_stock['quantity']})
""")

    # ================== 📊 METRICS ==================
    col1, col2, col3 = st.columns(3)
    col1.metric("🏪 Stations", len(df))
    col2.metric("📦 Cylinders", int(df["quantity"].sum()))
    col3.metric("💰 Avg Price", f"₹{int(df['price'].mean())}")

    st.divider()

    # ================== 📊 CHART SWITCH (NO RELOAD FEEL) ==================
    st.subheader("📊 Analysis")

    colA, colB = st.columns(2)

    with colA:
        if st.button("📊 Bar Chart"):
            st.session_state.chart_type = "Bar"

    with colB:
        if st.button("📍 Scatter Plot"):
            st.session_state.chart_type = "Scatter"

    # ----------------- DISPLAY SELECTED CHART -----------------
    if st.session_state.chart_type == "Bar":
        fig = px.bar(
            df,
            x="name",
            y="quantity",
            text="quantity",
            title="Cylinder Availability per Station"
        )
    else:
        fig = px.scatter(
            df,
            x="distance",
            y="price",
            size="quantity",
            color="brand",
            hover_name="name",
            title="Price vs Distance vs Availability"
        )

    st.plotly_chart(fig, use_container_width=True)

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
            "You": "blue",
            "Station": "red"
        }
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
        legend_title="Legend",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    st.plotly_chart(fig_map, use_container_width=True)

elif "results" in st.session_state:
    st.error("❌ No stations found")