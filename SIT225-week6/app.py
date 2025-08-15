# app.py — SIT225 Week 6 (forgiving loader that cleans your raw Serial log)
import os, re, io
print("RUNNING FILE:", os.path.abspath(__file__))  # ✅ Show full path of this file

import pandas as pd
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output, State
from dash import ctx
import plotly.express as px

CSV_PATH = "gyro.csv"  # your raw file (as copied from Serial Monitor)

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError("Put gyro.csv in the SAME folder as app.py.")

# ---------- Load & Clean ----------
def load_and_clean(path: str) -> pd.DataFrame:
    text = open(path, "r", encoding="utf-8", errors="ignore").read().strip()
    if not text:
        raise ValueError("gyro.csv is empty.")

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    cleaned = []

    re_arrow = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s*->\s*")
    re_timec = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3},")

    maybe_header = lines[0].lower()
    has_header = any(h in maybe_header for h in ["timestamp", "x,y,z"])

    for ln in lines:
        s = ln
        if not has_header:
            s = re_arrow.sub("", s)
            s = re_timec.sub("", s)
        cleaned.append(s)

    if not has_header:
        cleaned.insert(0, "timestamp_ms,x,y,z")

    df = pd.read_csv(io.StringIO("\n".join(cleaned)))
    df.columns = [c.strip().lower() for c in df.columns]

    if "timestamp_ms" in df.columns:
        ts = df["timestamp_ms"]
    elif "timestamp(ms)" in df.columns:
        ts = df["timestamp(ms)"]
    elif "timestamp" in df.columns:
        ts = df["timestamp"]
    else:
        ts = df.iloc[:, 0]
        df = df.rename(columns={df.columns[0]: "timestamp_ms",
                                df.columns[1]: "x",
                                df.columns[2]: "y",
                                df.columns[3]: "z"})

    for ax in ("x", "y", "z"):
        if ax not in df.columns:
            raise ValueError("CSV must contain x, y, z columns after cleaning.")

    out = pd.DataFrame({
        "timestamp_ms": pd.to_numeric(ts, errors="coerce"),
        "x": pd.to_numeric(df["x"], errors="coerce"),
        "y": pd.to_numeric(df["y"], errors="coerce"),
        "z": pd.to_numeric(df["z"], errors="coerce"),
    }).dropna()

    if pd.api.types.is_numeric_dtype(out["timestamp_ms"]):
        out["time"] = pd.to_datetime(out["timestamp_ms"], unit="ms", errors="coerce")
    else:
        out["time"] = pd.NaT

    return out.reset_index(drop=True)

df = load_and_clean(CSV_PATH)
N = len(df)
if N == 0:
    raise ValueError("No valid rows after cleaning. Check gyro.csv content.")

# ---------- Dash UI ----------
app = Dash(__name__)
app.title = "SIT225 Week 6 — Gyroscope Dashboard"

app.layout = html.Div(style={"padding": 16, "fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Arial"}, children=[
    html.H2("Gyroscope Data Dashboard"),

    html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(4, minmax(220px, 1fr))", "gap": 12}, children=[
        html.Div([
            html.Label("Chart type"),
            dcc.Dropdown(
                id="chart-type",
                options=[
                    {"label": "Line", "value": "line"},
                    {"label": "Scatter", "value": "scatter"},
                    {"label": "Histogram (distribution)", "value": "hist"},
                ],
                value="line", clearable=False
            )
        ]),
        html.Div([
            html.Label("Variables"),
            dcc.Dropdown(
                id="vars", multi=True, clearable=False,
                options=[{"label": v.upper(), "value": v} for v in ["x", "y", "z"]],
                value=["x", "y", "z"]
            )
        ]),
        html.Div([
            html.Label("Samples per view"),
            dcc.Input(id="samples", type="number", min=10, step=10,
                      value=min(1000, N if N else 1000), style={"width": "100%"})
        ]),
        html.Div([
            html.Label("Navigate"),
            html.Div(style={"display": "flex", "gap": 8}, children=[
                html.Button("◀ Prev", id="prev", n_clicks=0, style={"width": "100%"}),
                html.Button("Next ▶", id="next", n_clicks=0, style={"width": "100%"}),
            ])
        ]),
    ]),

    html.Div(id="window-info", style={"marginTop": 6, "opacity": 0.8}),
    dcc.Graph(id="main-graph", style={"height": 520, "marginTop": 8}),

    html.H4("Summary (current window)"),
    dash_table.DataTable(
        id="stats-table",
        style_table={"overflowX": "auto"},
        style_cell={"padding": "6px", "textAlign": "center"},
        style_header={"fontWeight": "bold"},
    ),

    dcc.Store(id="start", data=0),
])

# ---------- Paging ----------
@app.callback(
    Output("start", "data"),
    Input("prev", "n_clicks"), Input("next", "n_clicks"),
    State("start", "data"), State("samples", "value"),
    prevent_initial_call=False
)
def update_start(prev_clicks, next_clicks, start, samples):
    if not samples or samples <= 0:
        samples = 100
    if start is None:
        start = 0
    trig = ctx.triggered_id
    if trig == "prev":
        start = max(0, start - samples)
    elif trig == "next":
        start = min(max(0, N - samples), start + samples)
    else:
        start = min(start, max(0, N - samples))
    return int(start)

# ---------- Update graph + table ----------
@app.callback(
    Output("main-graph", "figure"),
    Output("stats-table", "data"),
    Output("stats-table", "columns"),
    Output("window-info", "children"),
    Input("chart-type", "value"),
    Input("vars", "value"),
    Input("samples", "value"),
    Input("start", "data"),
)
def update_view(chart_type, vars_selected, samples, start):
    if not vars_selected:
        vars_selected = ["x", "y", "z"]
    if not samples or samples <= 0:
        samples = 100
    if start is None:
        start = 0

    end = min(N, start + samples)
    window = df.iloc[start:end].copy()

    plot_vars = [v for v in vars_selected if v in ["x", "y", "z"]]

    use_time = "time" in window.columns and window["time"].notna().any()
    x_axis = "time" if use_time else window.index

    if chart_type == "line":
        fig = px.line(window, x=x_axis, y=plot_vars)
    elif chart_type == "scatter":
        fig = px.scatter(window, x=x_axis, y=plot_vars)
    else:
        melt = window[plot_vars].melt(var_name="axis", value_name="value")
        fig = px.histogram(melt, x="value", color="axis", barmode="overlay", opacity=0.6)

    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode="x unified" if chart_type in ("line", "scatter") else "closest",
        legend_title_text="Axis"
    )

    summary = []
    for v in plot_vars:
        s = window[v].dropna()
        row = dict(
            variable=v.upper(),
            count=int(s.count()),
            mean=float(s.mean()) if not s.empty else None,
            std=float(s.std(ddof=0)) if not s.empty else None,
            min=float(s.min()) if not s.empty else None,
            max=float(s.max()) if not s.empty else None,
        )
        summary.append(row)
    columns = [{"name": c.capitalize(), "id": c} for c in ["variable", "count", "mean", "std", "min", "max"]]

    info = f"Showing rows {start}–{end-1} of {N} (window size: {end-start})"
    return fig, summary, columns, info

# ✅ Run on a different port so it doesn't use cached old version
if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
