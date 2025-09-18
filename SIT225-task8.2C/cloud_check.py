import time
import logging
from arduino_iot_cloud import ArduinoCloudClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DEVICE_ID  = "152a2d2e-f56d-48a8-9d24-d9c4138d6cfd"
SECRET_KEY = "5e7EyM7RmDP6v5y2YGLjgDAHk"
VAR_X, VAR_Y, VAR_Z = "py_x", "py_y", "py_z"

last = {"x": None, "y": None, "z": None}

def on_x(_c, v): last["x"] = v; print("x:", v)
def on_y(_c, v): last["y"] = v; print("y:", v)
def on_z(_c, v): last["z"] = v; print("z:", v)

if __name__ == "__main__":
    client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY)
    client.register(VAR_X, value=None, on_write=on_x)
    client.register(VAR_Y, value=None, on_write=on_y)
    client.register(VAR_Z, value=None, on_write=on_z)

    logging.info("Connecting to Arduino IoT Cloud…")
    client.start()
    logging.info("Connected. Move your phone (accelerometer widget visible). Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        client.stop()
        logging.info("Disconnected.")
