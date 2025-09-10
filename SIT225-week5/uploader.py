import serial
import time
import firebase_admin
from firebase_admin import credentials, db

# Load Firebase service account key 
cred = credentials.Certificate("serviceAccountKey.json")

# Initialize Firebase app with your Realtime Database URL
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://projectweek5-df103-default-rtdb.firebaseio.com/'
})

# Setup Arduino serial connection (COM4 and 115200 baud from Arduino IDE)
ser = serial.Serial('COM4', 115200)  
time.sleep(2)  # wait for Arduino to reset

print("Starting data upload to Firebase... (Press Ctrl+C to stop)")

while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        if line:
            timestamp = int(time.time())
            ref = db.reference('gyro_data')
            ref.push({
                'timestamp': timestamp,
                'values': line
            })
            print(f"Uploaded: {line}")
    except KeyboardInterrupt:
        print("\nStopped by user")
        break
    except Exception as e:
        print("Error:", e)
        break
