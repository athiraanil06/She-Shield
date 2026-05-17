from geopy.geocoders import Nominatim

# 1. Initialize the tool
# 'user_agent' can be any name you like
locator = Nominatim(user_agent="my_safety_app")

# 2. Ask for a location
place_name = input("Enter a place (e.g., Marine Drive, Kochi): ")

# 3. Get the location data
location = locator.geocode(place_name)

if location:
    print(f"Location Found: {location.address}")
    print(f"Latitude: {location.latitude}")
    print(f"Longitude: {location.longitude}")
else:
    print("Sorry, I couldn't find that place on the map.")