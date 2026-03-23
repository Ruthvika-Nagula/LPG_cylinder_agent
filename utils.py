# from geopy.distance import geodesic

# def calculate_distance(user_loc, station_loc):
#     return geodesic(user_loc, station_loc).km

# def filter_and_sort(stations, user_loc, brand, budget):
#     results = []

#     for s in stations:
#         if s["brand"].lower() == brand.lower() and s["price"] <= budget:
#             distance = calculate_distance(
#                 user_loc, (s["lat"], s["lon"])
#             )
#             s["distance"] = round(distance, 2)
#             results.append(s)

#     # 🔥 MAIN LOGIC: Price first, then distance
#     results = sorted(results, key=lambda x: (x["price"], x["distance"]))

#     return results



from geopy.distance import geodesic
from geopy.geocoders import Nominatim

# Initialize geolocator
geolocator = Nominatim(user_agent="lpg_finder")

# ----------------- DISTANCE -----------------
def calculate_distance(user_loc, station_loc):
    return geodesic(user_loc, station_loc).km


# ----------------- REVERSE GEOCODING -----------------
def reverse_geocode(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), timeout=5)
        return location.address.split(",")[0]
    except:
        return "Unknown Location"


# ----------------- FILTER + SORT -----------------
def filter_and_sort(stations, user_loc, brand, budget):
    results = []

    for s in stations:
        if s["brand"].lower() == brand.lower() and s["price"] <= budget:
            distance = calculate_distance(user_loc, (s["lat"], s["lon"]))
            s["distance"] = round(distance, 2)
            results.append(s)

    # 🔥 Smart logic: Price → Distance → Quantity
    results = sorted(
        results,
        key=lambda x: (x["price"], x["distance"], -x["quantity"])
    )

    return results