import serial
import time
import random
from datetime import datetime

ser = serial.Serial('COM4', 9600, timeout=1)


time.sleep(2)  # Wait for Arduino to get ready

while True:
    send_number = random.randint(1, 5)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sending: {send_number}")
    ser.write(f"{send_number}\n".encode())

    while True:
        if ser.in_waiting:
            received = ser.readline().decode().strip()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Received: {received}")
            try:
                delay = int(received)
                print(f"Sleeping for {delay} seconds...\n")
                time.sleep(delay)
                break
            except ValueError:
                print("Invalid data received")
