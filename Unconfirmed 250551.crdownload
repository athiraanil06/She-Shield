import pandas as pd
import numpy as np

# Load your dataset
df = pd.read_csv("women_travel_safety_dataset.csv")

# Recalculate safety score
def calculate_safety(row):
    score = 50  # base score

    # Time-related
    if row["is_night"] == 1:
        score -= 15
    if row["is_weekend"] == 1:
        score -= 5

    # Infrastructure
    if row["street_lighting"] == 1:
        score += 10
    else:
        score -= 10

    # Distances (higher distance = less safe)
    score -= row["police_distance"] * 3
    score -= row["hospital_distance"] * 2

    # Activity & crowd
    score += row["poi_count"] * 0.8
    score += row["commercial_density"] * 20
    score += row["bus_stop_count"] * 1.5

    # Road quality
    score += row["road_type_score"] * 10

    # Random noise for realism
    score += np.random.uniform(-5, 5)

    return max(0, min(100, round(score, 2)))

# Apply new safety score
df["safety_probability"] = df.apply(calculate_safety, axis=1)

# Save updated dataset
df.to_csv("safety_dataset_fixed.csv", index=False)

print("Dataset updated successfully!")
