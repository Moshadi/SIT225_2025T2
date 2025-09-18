import time
import threading
import logging
import webbrowser
from collections import deque
from dataclasses import dataclass
from typing import List

from dash import Dash, html, dcc, Input, Output, no_update
import plotly.graph_objects as go
from arduino_iot_cloud import ArduinoCloudClient

# ----- Logging -----
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ----- Your Arduino IoT Cloud creds/variables -----
DEVICE_ID  = "152a2d2e-f56d-48a8-9d24-d9c4138d6cfd"
SECRET_KEY = "5e7EyM7RmDP6v5y2YGLjgDAHk"
VAR_X, VAR_Y, VAR_Z = "py_x", "py_y", "py_z"

# ----- Tunables -----
WINDOW_SECONDS   = 12
UI_FPS           = 10
TARGET_SAMPLE_HZ = 30
SMOOTH_ALPHA     = 0.20
MAX_POINTS       = int(WINDOW_SECONDS * TARGET_SAMPLE_HZ)

# ----- Latest reading cache from cloud callbacks -----
_last_x = None; _last_y = None; _last_z = None
_last_lock = threading.Lock()

def _on_x(_c, v):
    global _last_x
    with _last_lock:
        _last_x = float(v)

def _on_y(_c, v):
    global _last_y
    with _last_lock:
        _last_y = float(v)

def _on_z(_c, v):
    global _last_z
    with _last_lock:
        _last_z = float(v)

# ----- Smooth streaming buffer (optional EWMA smoothing) -----
@dataclass
class Sample:
    t: float
    x: float
    y: float
    z: float

class DataPipe:
    def __init__(self, alpha: float):
        self._pending: deque[Sample] = deque()
        self._lock = threading.Lock()
        self._sx = self._sy = self._sz = None
        self._alpha = float(alpha)

    def push(self, s: Sample):
        if self._alpha > 0:
            if self._sx is None:
                self._sx, self._sy, self._sz = s.x, s.y, s.z
            else:
                a = self._alpha
                self._sx = a*s.x + (1-a)*self._sx
                self._sy = a*s.y + (1-a)*self._sy
                self._sz = a*s.z + (1-a)*self._sz
            s = Sample(s.t, self._sx, self._sy, self._sz)
        with self._lock:
            self._pending.append(s)

    def drain(self) -> List[Sample]:
        with self._lock:
            if not self._pending:
                return []
            items = list(self._pending)
            self._pending.clear()
            return items

pipe = DataPipe(SMOOTH_ALPHA)

# ----- Cloud reader (NON-BLOCKING) -----
def start_cloud_reader_nonblocking():
    """
    Start Arduino IoT Cloud in a background thread so it can't block Dash.
    Also start a sampler thread that feeds the UI at a steady rate.
    """
    client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY)
    client.register(VAR_X, value=None, on_write=_on_x)
    client.register(VAR_Y, value=None, on_write=_on_y)
    client.register(VAR_Z, value=None, on_write=_on_z)

    def _run_cloud():
        logging.info("Connecting to Arduino IoT Cloud…")
        try:
            client.start()  # blocks in this thread
        except Exception as e:
            logging.error("Cloud thread crashed: %s", e)

    threading.Thread(target=_run_cloud, daemon=True).start()

    def sampler():
        period = 1.0 / max(1, TARGET_SAMPLE_HZ)
        while True:
            time.sleep(period)
            with _last_lock:
                if _last_x is None or _last_y is None or _last_z is None:
                    continue
                x, y, z = _last_x, _last_y, _last_z
            pipe.push(Sample(time.time(), x, y, z))

    threading.Thread(target=sampler, daemon=True).start()
    return client

# ----- Dash app -----
app = Dash(__name__)
_t0 = time.time()

app.layout = html.Div([
    html.H2("SIT225 — Smooth Live Accelerometer (x/y/z)"),
    dcc.Graph(
        id="g",
        figure=go.Figure(
            data=[
                go.Scatter(name="x", x=[], y=[], mode="lines"),
                go.Scatter(name="y", x=[], y=[], mode="lines"),
                go.Scatter(name="z", x=[], y=[], mode="lines"),
            ],
            layout=go.Layout(
                xaxis=dict(title="Time (s, relative)"),
                yaxis=dict(title="Acceleration (relative)"),
                margin=dict(l=40, r=10, t=40, b=40),
                uirevision="keep",
            ),
        ),
        animate=False
    ),
    dcc.Interval(id="tick", interval=int(1000/UI_FPS), n_intervals=0),
], style={"maxWidth": "900px", "margin": "24px auto", "fontFamily": "system-ui"})

@app.callback(Output("g", "extendData"), Input("tick", "n_intervals"))
def on_tick(_):
    samples = pipe.drain()
    if not samples:
        return no_update
    ts = [s.t - _t0 for s in samples]
    xs = [s.x for s in samples]
    ys = [s.y for s in samples]
    zs = [s.z for s in samples]
    return ({"x": [ts, ts, ts], "y": [xs, ys, zs]}, [0, 1, 2], MAX_POINTS)

# ----- Main (Dash 3.x uses app.run) -----
if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 8051
    URL  = f"http://{HOST}:{PORT}"

    _client = start_cloud_reader_nonblocking()

    print("\n===================================")
    print(" RUNNING Dash UI (app.py)")
    print(" Open this exact URL:", URL)     # MUST include http://
    print("===================================\n")

    # Auto-open after a short delay
    threading.Timer(1.0, lambda: webbrowser.open(URL)).start()

    try:
        # Dash 3.x: use app.run (NOT app.run_server)
        app.run(debug=False, use_reloader=False, host=HOST, port=PORT)
    finally:
        try:
            _client.stop()
        except Exception:
            pass
