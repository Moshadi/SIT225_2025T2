"""
    Requirement: arduino_iot_cloud
    Install: pip install arduino-iot-cloud plotly pandas kaleido
    
    Accelerometer data collection from Arduino IoT Cloud
"""

import sys
import traceback
import time
import csv
from datetime import datetime
from arduino_iot_cloud import ArduinoCloudClient
import pandas as pd
import plotly.express as px

# === Credentials ===
DEVICE_ID = "152a2d2e-f56d-48a8-9d24-d9c4138d6cfd"
SECRET_KEY = "5e7EyM7RmDP6v5y2YGLjgDAHk"

# === CSV setup ===
filename = f"accelerometer_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
csvfile = None
writer = None

# === Buffers (latest values) ===
latest_x, latest_y, latest_z = None, None, None


# === Callback functions ===
def on_py_x(client, value):
    global latest_x
    latest_x = value
    write_row()


def on_py_y(client, value):
    global latest_y
    latest_y = value
    write_row()


def on_py_z(client, value):
    global latest_z
    latest_z = value
    write_row()


def write_row():
    """Write a full row only when all 3 values are available."""
    global latest_x, latest_y, latest_z, writer
    if writer and latest_x is not None and latest_y is not None and latest_z is not None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([ts, latest_x, latest_y, latest_z])
        csvfile.flush()
        print(f"[{ts}] Accelerometer - x={latest_x}, y={latest_y}, z={latest_z}")


def generate_graph(csv_path, png_path):
    """Generate a line graph of accelerometer data."""
    try:
        df = pd.read_csv(csv_path)
        fig = px.line(df, x="timestamp", y=["x", "y", "z"],
                      title="Accelerometer Data",
                      labels={"value": "Acceleration", "timestamp": "Time"})
        fig.write_image(png_path)
        print(f"✅ Graph saved as {png_path}")
    except Exception as e:
        print(f"⚠️ Could not generate graph: {e}")


def main():
    global csvfile, writer

    print("Starting Arduino IoT Cloud accelerometer data collection...")

    # Setup CSV file
    csvfile = open(filename, "w", newline="")
    writer = csv.writer(csvfile)
    writer.writerow(["timestamp", "x", "y", "z"])   # CSV header

    # Instantiate Arduino cloud client
    client = ArduinoCloudClient(
        device_id=DEVICE_ID,
        username=DEVICE_ID,
        password=SECRET_KEY
    )

    # Register with cloud variables and listen on their value changes
    client.register("py_x", value=None, on_write=on_py_x)
    client.register("py_y", value=None, on_write=on_py_y)
    client.register("py_z", value=None, on_write=on_py_z)

    # Start cloud client
    print("📡 Connecting to Arduino IoT Cloud... Press Ctrl+C to stop.")
    client.start()

    try:
        while True:
            time.sleep(1)   # keep loop alive
    except KeyboardInterrupt:
        print("\n✅ Stopping data collection...")
        client.stop()
        # Generate graph at the end
        png_file = filename.replace(".csv", ".png")
        generate_graph(filename, png_file)
    finally:
        if csvfile:
            csvfile.close()
        print("Data collection stopped successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"❌ Error occurred: {e}")
        traceback.print_exc()
    finally:
        if csvfile:
            csvfile.close()
