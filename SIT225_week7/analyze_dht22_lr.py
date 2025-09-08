import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
import plotly.io as pio

# Force charts to open in browser
pio.renderers.default = "browser"

# Load your data
df = pd.read_csv("sensor_data.csv")

# Normalize column names
df.columns = [c.strip().lower() for c in df.columns]

# Check required columns
if "temperature" not in df.columns or "humidity" not in df.columns:
    raise ValueError(f"CSV must have 'temperature' and 'humidity' columns. Found: {df.columns}")

results = []

def run_regression(data, title, filename):
    X = data[["temperature"]].values
    y = data["humidity"].values

    model = LinearRegression()
    model.fit(X, y)

    slope = model.coef_[0]
    intercept = model.intercept_
    r2 = model.score(X, y)

    print(f"--- {title} ---")
    print(f"Slope: {slope:.4f}")
    print(f"Intercept: {intercept:.4f}")
    print(f"R²: {r2:.4f}\n")

    results.append([title, slope, intercept, r2])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=X.flatten(), y=y, mode="markers", name="Data"))
    fig.add_trace(go.Scatter(x=X.flatten(), y=model.predict(X), mode="lines", name="Trend"))
    fig.update_layout(title=title, xaxis_title="Temperature (°C)", yaxis_title="Humidity (%)")

    # Save plots
    fig.write_image(f"{filename}.png")
    fig.write_html(f"{filename}.html")
    # Show in browser
    fig.show()

# Scenario 1 – Original Data
run_regression(df, "Temperature vs Humidity (Original Data)", "scenario1")

# Scenario 2 – Filtered Data (20–35 °C)
filtered_df = df[(df["temperature"] >= 20) & (df["temperature"] <= 35)]
run_regression(filtered_df, "Temperature vs Humidity (Filtered Data: 20–35 °C)", "scenario2")

# Scenario 3 – More Filtered Data (22–32 °C)
more_filtered_df = df[(df["temperature"] >= 22) & (df["temperature"] <= 32)]
run_regression(more_filtered_df, "Temperature vs Humidity (More Filtered Data: 22–32 °C)", "scenario3")

# Print summary table
summary_df = pd.DataFrame(results, columns=["Scenario", "Slope", "Intercept", "R²"])
print("\nSummary of results:")
print(summary_df.to_string(index=False))
