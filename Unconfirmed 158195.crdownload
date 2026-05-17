import requests
import math
from datetime import datetime

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


# -------------------------
# Convert Location → Lat/Lon
# -------------------------
def get_coordinates(location_name):
    try:
        params = {
            "q": location_name,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "women-safety-index"}
        response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            return None, None
        return float(data[0]["lat"]), float(data[0]["lon"])
    except requests.exceptions.RequestException as e:
        print("❌ Geocoding Error:", e)
        return None, None


# -------------------------
# Distance Function
# -------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# -------------------------
# Separate nearest police/hospital finder
# -------------------------
def get_nearest_amenity(lat, lon, amenity, radius=5000):
    query = f"""
    [out:json][timeout:25];
    node["amenity"="{amenity}"](around:{radius},{lat},{lon});
    out;
    """
    try:
        response = requests.post(OVERPASS_URL, data=query, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Overpass API Error for {amenity}:", e)
        return "Not Available"

    min_distance = float("inf")
    for el in data.get("elements", []):
        lat2 = el.get("lat")
        lon2 = el.get("lon")
        if lat2 and lon2:
            dist = haversine(lat, lon, lat2, lon2)
            min_distance = min(min_distance, dist)

    return round(min_distance, 2) if min_distance != float("inf") else "Not Available"


# -------------------------
# General Safety Features
# -------------------------
def get_safety_features(lat, lon, travel_hour, is_night, is_weekend):
    radius_general = 1500
    query = f"""
    [out:json][timeout:25];
    (
      node(around:{radius_general},{lat},{lon})["shop"];
      node(around:{radius_general},{lat},{lon})["highway"="street_lamp"];
      node(around:{radius_general},{lat},{lon})["highway"="bus_stop"];
      way(around:{radius_general},{lat},{lon})["highway"~"primary|secondary|tertiary|residential"];
      node(around:{radius_general},{lat},{lon})["amenity"="hospital"];
    );
    out center;
    """
    try:
        response = requests.post(OVERPASS_URL, data=query, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print("❌ Overpass API Error:", e)
        return None

    street_lighting = 0
    nearby_shops = 0
    bus_stop_count = 0
    hospital_distance = float("inf")
    poi_count = 0
    road_type_score = 1

    for el in data.get("elements", []):
        tags = el.get("tags", {})
        lat2 = el.get("lat") or el.get("center", {}).get("lat")
        lon2 = el.get("lon") or el.get("center", {}).get("lon")
        if lat2 is None or lon2 is None:
            continue
        dist = haversine(lat, lon, lat2, lon2)

        if tags.get("highway") == "street_lamp":
            street_lighting += 1
        if tags.get("shop"):
            nearby_shops += 1
        if tags.get("highway") == "bus_stop":
            bus_stop_count += 1
        if tags.get("amenity") == "hospital":
            hospital_distance = min(hospital_distance, dist)
        if tags.get("amenity"):
            poi_count += 1
        if tags.get("highway"):
            hw = tags["highway"]
            if hw in ["primary", "secondary"]:
                road_type_score = 3
            elif hw in ["tertiary", "residential"]:
                road_type_score = 2

    emergency_count = 0
    commercial_density = nearby_shops / 10

    return {
        "travel_hour": travel_hour,
        "is_night": is_night,
        "is_weekend": is_weekend,
        "street_lighting": street_lighting,
        "road_type_score": road_type_score,
        "nearby_shops": nearby_shops,
        "bus_stop_count": bus_stop_count,
        "poi_count": poi_count,
        "commercial_density": commercial_density,
        "hospital_distance": round(hospital_distance, 2) if hospital_distance != float("inf") else "Not Available"
    }


# -------------------------
# MAIN PROGRAM
# -------------------------
if __name__ == "__main__":
    print("Women Travel Safety Index System")
    print("----------------------------------")

    location = input("Enter Location Name: ")
    date_input = input("Enter Date (YYYY-MM-DD): ")
    time_input = input("Enter Time (Example: 9 AM or 6 PM): ")

    # Validate date
    try:
        user_date = datetime.strptime(date_input, "%Y-%m-%d")
        today = datetime.today().date()
        if user_date.date() < today:
            print("❌ Invalid date. Date cannot be in the past.")
            exit()
    except ValueError:
        print("❌ Invalid date format.")
        exit()

    # Validate time
    try:
        parsed_time = datetime.strptime(time_input.strip().upper(), "%I %p")
        travel_hour = parsed_time.hour
    except ValueError:
        print("❌ Invalid time format. Use like '9 AM' or '6 PM'")
        exit()

    is_night = 1 if travel_hour >= 19 or travel_hour <= 6 else 0
    is_weekend = 1 if user_date.weekday() >= 5 else 0

    print("\nGetting coordinates...")
    lat, lon = get_coordinates(location)

    if lat is None:
        print("❌ Location not found.")
        exit()
    else:
        print(f"Location Found: {lat}, {lon}\n")
        print("Fetching nearest police station...")
        police_distance = get_nearest_amenity(lat, lon, "police")
        print("Fetching safety features...")
        features = get_safety_features(lat, lon, travel_hour, is_night, is_weekend)
        if features:
            features["police_distance"] = police_distance
            print("\n------ SAFETY FEATURES ------")
            for key, value in features.items():
                print(f"{key}: {value}")
        else:
            print("❌ Could not fetch safety data.")
