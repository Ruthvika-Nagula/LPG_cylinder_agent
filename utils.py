from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import smtplib
from email.mime.text import MIMEText
import os
import streamlit as st
from dotenv import load_dotenv
from tavily import TavilyClient
import re

load_dotenv()

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

geolocator = Nominatim(user_agent="lpg_finder")
tavily_api_key = get_secret("TAVILY_API_KEY")
tavily = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None

# ---------------- DISTANCE ----------------
def calculate_distance(user_loc, station_loc):
    return geodesic(user_loc, station_loc).km

# ---------------- REVERSE ----------------
def reverse_geocode(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), timeout=5)
        return location.address.split(",")[0]
    except:
        return "Unknown Location"

# ---------------- FILTER ----------------
def filter_and_sort(stations, user_loc, brand, budget):
    results = []
    for s in stations:
        if s["brand"].lower() == brand.lower() and s["price"] <= budget:
            d = calculate_distance(user_loc, (s["lat"], s["lon"]))
            new_s = s.copy()
            new_s["distance"] = round(d, 2)
            results.append(new_s)
    return sorted(results, key=lambda x: (x["price"], x["distance"], -x["quantity"]))

# ---------------- 🔥 AGENT PRODUCT SEARCH ----------------
def get_products():
    query = "buy induction stove OR gas stove price India Amazon Flipkart Zepto"

    products = []

    if tavily:
        try:
            response = tavily.search(query=query, search_depth="advanced", max_results=8)

            for r in response.get("results", []):
                url = r.get("url", "").lower()
                title = r.get("title", "")
                content = r.get("content", "")

                if "youtube" in url:
                    continue

                if not any(site in url for site in ["amazon", "flipkart", "zepto"]):
                    continue

                price_match = re.search(r"₹\s?[\d,]+", content)

                if not price_match:
                    continue

                price_str = price_match.group().replace("₹", "").replace(",", "").strip()
                if not price_str.isdigit():
                    continue
                price = int(price_str)
                
                platform = "Other"
                if "amazon" in url:
                    platform = "Amazon"
                elif "flipkart" in url:
                    platform = "Flipkart"
                elif "zepto" in url:
                    platform = "Zepto"

                products.append({
                    "name": title,
                    "price": price,
                    "link": url,
                    "platform": platform
                })

        except Exception as e:
            print("Tavily error:", e)

    # ✅ fallback (guaranteed)
    if not products:
        products = [
            {"name": "Prestige Induction Cooktop", "price": 1999, "platform": "Amazon", "link": "https://www.amazon.in/s?k=prestige+induction"},
            {"name": "Bajaj Induction Stove", "price": 1799, "platform": "Flipkart", "link": "https://www.flipkart.com/search?q=bajaj+induction"},
            {"name": "Pigeon Gas Stove", "price": 1299, "platform": "Amazon", "link": "https://www.amazon.in/s?k=pigeon+gas+stove"},
        ]

    return sorted(products, key=lambda x: x["price"])

# ---------------- EMAIL ----------------
def send_email(receiver_email, message):
    sender_email = get_secret("EMAIL")
    app_password = get_secret("APP_PASSWORD")
    
    if not sender_email or not app_password:
        print("Missing email credentials.")
        return False

    msg = MIMEText(message)
    msg["Subject"] = "Smart LPG Recommendation"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Email Error:", e)
        return False