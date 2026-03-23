from geopy.distance import geodesic

def calculate_distance(user_loc, station_loc):
    return geodesic(user_loc, station_loc).km

def filter_and_sort(stations, user_loc, brand, budget):
    results = []

    for s in stations:
        if s["brand"].lower() == brand.lower() and s["price"] <= budget:
            distance = calculate_distance(
                user_loc, (s["lat"], s["lon"])
            )
            s["distance"] = round(distance, 2)
            results.append(s)

    # 🔥 MAIN LOGIC: Price first, then distance
    results = sorted(results, key=lambda x: (x["price"], x["distance"]))

    return results
