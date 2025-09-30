import serial, csv, time, glob
from datetime import datetime

# Auto-detect Arduino port on macOS
ports = glob.glob('/dev/tty.usbmodem*') + glob.glob('/dev/tty.usbserial*')
if not ports:
    raise IOError("❌ No Arduino found. Make sure it's plugged in! Run 'ls /dev/tty.*' to check.")
PORT = ports[0]
BAUD = 9600
OUT  = "sensor_data.csv"

print(f"✅ Using port: {PORT} at {BAUD} baud")
ser = serial.Serial(PORT, BAUD, timeout=2)
time.sleep(2)  # wait for Arduino reset

with open(OUT, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp_iso", "temperature", "humidity"])
    print("📡 Logging... Press Ctrl+C to stop after 30+ minutes.")
    try:
        while True:
            line = ser.readline().decode(errors="ignore").strip()
            if not line or "temperature" in line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) == 2:
                ts = datetime.now().isoformat()
                # Save to CSV
                writer.writerow([ts, parts[0], parts[1]])
                # Print to terminal
                print(f"{ts} -> Temp: {parts[0]} °C, Humidity: {parts[1]} %")
    except KeyboardInterrupt:
        pass

ser.close()
print(f"✅ Saved full dataset to {OUT}")
