import requests
import pickle
import os
import pandas as pd
from geopy.geocoders import Nominatim

# --- 1. SETTINGS & MODEL LOADING ---
MODEL_PATH = 'gradient_boosting_model.pkl'
SCALER_PATH = 'scaler.pkl'

def load_ml_components():
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
        print("✅ AI Model and Scaler loaded successfully!")
        return model, scaler
    except Exception as e:
        print(f"❌ Model Loading Error: {e}")
        print("Tip: Re-run your training script to generate a fresh .pkl file.")
        return None, None

# --- 2. THE DETECTIVE (Map Fetching) ---
def get_live_features(lat, lon):
    query = f"""
    [out:json];
    (
      nw["amenity"="police"](around:5000, {lat}, {lon});
      nw["amenity"="hospital"](around:5000, {lat}, {lon});
      nw["highway"="street_lamp"](around:1500, {lat}, {lon});
    );
    out tags;
    """
    url = "https://overpass-api.de/api/interpreter"
    try:
        response = requests.get(url, params={'data': query}, timeout=10)
        data = response.json()
        p, h, l = 0, 0, 0
        for element in data.get('elements', []):
            t = element.get('tags', {})
            if t.get('amenity') == 'police': p += 1
            elif t.get('amenity') == 'hospital': h += 1
            elif t.get('highway') == 'street_lamp': l += 1
        
        # Fallback for missing street light data
        if l == 0: l = 5 
        return p, h, l
    except:
        return 0, 0, 0

# --- 3. MAIN EXECUTION ---
def main():
    # Load the "Brain"
    model, scaler = load_ml_components()
    if not model: return

    # Get User Input
    place = input("\nEnter location (e.g., Chengannur): ")
    
    # Get Coordinates
    geolocator = Nominatim(user_agent="safety_app")
    location = geolocator.geocode(place)
    
    if location:
        lat, lon = location.latitude, location.longitude
        print(f"📍 Coordinates found: {lat}, {lon}")

        # Get Map Features
        p, h, l = get_live_features(lat, lon)
        print(f"📊 Map Data -> Police: {p}, Hospitals: {h}, Lights: {l}")

        # Prepare for Prediction
        # IMPORTANT: These 12 values MUST match the order of your training CSV!
        # [Lat, Lon, Police, Hospital, Lights, IsNight, BusStop, ...others]
        raw_data = [[lat, lon, p, h, l, 0, 2, 1, 0, 1, 0, 5]] 
        
        # Scale and Predict
        try:
            scaled_data = scaler.transform(raw_data)
            prediction = model.predict(scaled_data)
            probability = model.predict_proba(scaled_data)[0][1]

            print("\n" + "="*30)
            print(f"🛡️  SAFETY ANALYSIS FOR: {place.upper()}")
            print(f"SCORE: {probability * 100:.2f}%")
            print(f"RESULT: {'✅ SAFE' if prediction[0] == 1 else '⚠️  UNSAFE'}")
            print("="*30)
        except Exception as e:
            print(f"❌ Prediction Error: {e}")
            print("Check if your 'raw_data' has exactly the same number of columns as your training set.")

    else:
        print("❌ Could not find that location.")

if __name__ == "__main__":
    main()