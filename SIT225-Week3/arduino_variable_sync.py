from arduino_iot_client import ArduinoCloudClient
from arduino_iot_client.configuration import Configuration
from arduino_iot_client.models import Devicev2Propertyvalue
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Replace these with your credentials
DEVICE_ID = "your-device-id-here"
SECRET_KEY = "your-secret-key-here"

# Create empty list to store data
timestamps = []
distances = []

# Callback function for on_write
def on_distance_changed(value):
    print(f"New distance: {value}")
    timestamps.append(datetime.now().strftime("%H:%M:%S"))
    distances.append(value)
    
    # Save to CSV file
    df = pd.DataFrame({"Time": timestamps, "Distance": distances})
    df.to_csv("ultrasonic_data.csv", index=False)

# Setup client
client = ArduinoCloudClient(device_id=DEVICE_ID, secret_key=SECRET_KEY)
thing = client.get_thing()

# Register callback
thing["distance"].on_write = on_distance_changed

# Start listening
print("Listening for updates...")
thing.start()

# Run for 2 minutes (or stop manually)
time.sleep(120)

# Stop connection
thing.stop()
