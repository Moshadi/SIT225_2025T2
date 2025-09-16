import pandas as pd
import plotly.express as px

csv_file = "accelerometer_data_20250916_220115.csv"   
png_file = csv_file.replace(".csv", ".png")

df = pd.read_csv(csv_file)

fig = px.line(df, x="timestamp", y=["x", "y", "z"],
              title="Accelerometer Data",
              labels={"value": "Acceleration", "timestamp": "Time"})

fig.write_image(png_file)
print(f"✅ Graph saved as {png_file}")
fig.show()
