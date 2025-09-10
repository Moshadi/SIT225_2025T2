import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import matplotlib.pyplot as plt
import time

# --- Firebase setup ---
cred = credentials.Certificate("serviceAccountKey.json")  # your key file
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://projectweek5-df103-default-rtdb.firebaseio.com/"   # << update if yours is different
})

# --- Download data ---
ref = db.reference("/gyro_data")
data = ref.get()

# Convert to DataFrame
rows = []
for key, value in data.items():
    ts = value.get("timestamp", None)
    vals = value.get("values", "")
    try:
        gx, gy, gz = [float(v) for v in vals.split(",")]
        rows.append([ts, gx, gy, gz])
    except:
        continue

df = pd.DataFrame(rows, columns=["timestamp", "gyro_x", "gyro_y", "gyro_z"])

# Convert timestamp to readable time
df["time"] = pd.to_datetime(df["timestamp"], unit="s")

# Save to CSV
df.to_csv("gyro_data.csv", index=False)
print("✅ Data exported to gyro_data.csv")

# --- Plot graphs ---
plt.figure(figsize=(12,6))
plt.plot(df["time"], df["gyro_x"], label="Gyro X")
plt.plot(df["time"], df["gyro_y"], label="Gyro Y")
plt.plot(df["time"], df["gyro_z"], label="Gyro Z")
plt.xlabel("Time")
plt.ylabel("Gyroscope values")
plt.title("Gyroscope Data Over Time")
plt.legend()
plt.tight_layout()
plt.savefig("gyro_plot.png")
plt.show()

print("✅ Graph saved as gyro_plot.png")
