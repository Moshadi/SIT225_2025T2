#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install pyserial pandas matplotlib')


# In[6]:


import serial, time

PORT = "COM4"   
BAUD = 9600    

# Open the connection
ser = serial.Serial(PORT, BAUD, timeout=2)
time.sleep(2)   # wait for Arduino reset

print("Connected to", PORT)

# Test: read 10 lines
for i in range(10):
    line = ser.readline().decode(errors="ignore").strip()
    print(line)

ser.close()


# In[7]:


import pandas as pd

PORT = "COM4"
BAUD = 9600
CAPTURE_SECONDS = 1800   
INTERVAL = 5            

ser = serial.Serial(PORT, BAUD, timeout=2)
time.sleep(2)

rows = []
print("Logging for", CAPTURE_SECONDS, "seconds...")

start = time.time()
while time.time() - start < CAPTURE_SECONDS:
    line = ser.readline().decode(errors="ignore").strip()
    if "," in line and "Soil Moisture" not in line:  
        rows.append(line.split(","))
        print(line)  

ser.close()
print("Logging finished")

# Convert to DataFrame
columns = ["soil_raw","temp_c","humidity_pct","soil_pct",
           "ax","ay","az","move_flag","status"]
df = pd.DataFrame(rows, columns=columns)

# Save CSV
df.to_csv("plant_log.csv", index=False)
print("Saved plant_log.csv")


# In[11]:


import pandas as pd

header = [
    "soilRaw", 
    "temperature_C", 
    "humidity_pct", 
    "soilMoisture_pct", 
    "accelX", 
    "accelY", 
    "accelZ", 
    "movementFlag", 
    "status"
]

# Make DataFrame from rows you captured
df = pd.DataFrame(rows, columns=header)

# Save to CSV
df.to_csv("plant_log.csv", index=False)

print(len(df), "rows saved to plant_log.csv")


# In[12]:


df = pd.read_csv("plant_log.csv")
df.head()


# In[13]:


import matplotlib.pyplot as plt

# 1. Soil Moisture over time
plt.figure(figsize=(10,5))
plt.plot(df["soilMoisture_pct"], label="Soil Moisture (%)", color="blue")
plt.axhline(y=30, color="red", linestyle="--", label="Water Threshold (30%)")
plt.xlabel("Sample Index")
plt.ylabel("Moisture (%)")
plt.title("Soil Moisture Monitoring")
plt.legend()
plt.grid(True)
plt.show()

# 2. Temperature over time
plt.figure(figsize=(10,5))
plt.plot(df["temperature_C"], label="Temperature (°C)", color="orange")
plt.axhline(y=15, color="blue", linestyle="--", label="Low Temp (15°C)")
plt.axhline(y=35, color="red", linestyle="--", label="High Temp (35°C)")
plt.xlabel("Sample Index")
plt.ylabel("Temperature (°C)")
plt.title("Temperature Monitoring")
plt.legend()
plt.grid(True)
plt.show()

# 3. Humidity over time
plt.figure(figsize=(10,5))
plt.plot(df["humidity_pct"], label="Humidity (%)", color="green")
plt.xlabel("Sample Index")
plt.ylabel("Humidity (%)")
plt.title("Humidity Monitoring")
plt.legend()
plt.grid(True)
plt.show()

# 4. Disturbance events
plt.figure(figsize=(10,5))
plt.plot(df["movementFlag"], label="Disturbance Flag", color="red")
plt.xlabel("Sample Index")
plt.ylabel("Movement (0 = None, 1 = Disturbance)")
plt.title("Disturbance Detection (Accelerometer)")
plt.legend()
plt.grid(True)
plt.show()


# In[17]:


import matplotlib.pyplot as plt

# 1. Soil Moisture
plt.figure(figsize=(10,5))
plt.plot(df["soilMoisture_pct"], label="Soil Moisture (%)", color="blue")
plt.axhline(30, color="red", linestyle="--", label="Water Threshold (30%)")
plt.xlabel("Sample Index")
plt.ylabel("Moisture (%)")
plt.title("Soil Moisture Monitoring")
plt.legend()
plt.grid(True)
plt.savefig("soil_moisture_plot.png")
plt.show()

# 2. Temperature
plt.figure(figsize=(10,5))
plt.plot(df["temperature_C"], label="Temperature (°C)", color="orange")
plt.axhline(15, color="blue", linestyle="--", label="Low Temp (15°C)")
plt.axhline(35, color="red", linestyle="--", label="High Temp (35°C)")
plt.xlabel("Sample Index")
plt.ylabel("Temperature (°C)")
plt.title("Temperature Monitoring")
plt.legend()
plt.grid(True)
plt.savefig("temperature_plot.png")
plt.show()

# 3. Humidity
plt.figure(figsize=(10,5))
plt.plot(df["humidity_pct"], label="Humidity (%)", color="green")
plt.xlabel("Sample Index")
plt.ylabel("Humidity (%)")
plt.title("Humidity Monitoring")
plt.legend()
plt.grid(True)
plt.savefig("humidity_plot.png")
plt.show()

# 4. Disturbance
plt.figure(figsize=(10,5))
plt.plot(df["movementFlag"], label="Disturbance Flag", color="red")
plt.xlabel("Sample Index")
plt.ylabel("Movement (0=None, 1=Disturbance)")
plt.title("Disturbance Detection (Accelerometer)")
plt.legend()
plt.grid(True)
plt.savefig("disturbance_plot.png")
plt.show()



# In[ ]:




