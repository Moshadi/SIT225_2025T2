#include <Arduino_LSM6DS3.h>
#include <DHT.h>

// === Soil calibration ===
int SOIL_DRY_MIN = 850;   // dry soil / in air
int SOIL_WET_MAX = 320;   // fully wet soil

#define DHTPIN 2
#define DHTTYPE DHT22
#define SOIL_PIN A1

DHT dht(DHTPIN, DHTTYPE);

// Thresholds
float MOISTURE_LOW = 30.0;   // % moisture for "water now"
float TEMP_LOW = 15.0;       // °C
float TEMP_HIGH = 35.0;      // °C
float MOVE_THRESH = 0.6;     // change in |accel| (g) for disturbance

float clampf(float v, float lo, float hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}

void setup() {
  Serial.begin(9600);
  while (!Serial) {}

  dht.begin();
  if (!IMU.begin()) {
    Serial.println("ERR_IMU_INIT_FAILED");
    while (1) {}
  }
}

void loop() {
  // --- Soil moisture ---
  int soilRaw = analogRead(SOIL_PIN);
  float soilPercent = map(soilRaw, SOIL_DRY_MIN, SOIL_WET_MAX, 0, 100);
  soilPercent = clampf(soilPercent, 0, 100);

  // --- Temperature & Humidity ---
  float t = dht.readTemperature();
  float h = dht.readHumidity();

  // --- Accelerometer ---
  float ax, ay, az;
  int moveFlag = 0;
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(ax, ay, az);
    float magnitude = sqrt(ax * ax + ay * ay + az * az);
    if (abs(magnitude - 1.0) > MOVE_THRESH) {
      moveFlag = 1;
    }
  }

  // --- Status based on thresholds ---
  String status = (soilPercent < MOISTURE_LOW) ? "WATER NOW" : "OK";

  // === CSV output (for logging in Jupyter/CSV) ===
  Serial.print(soilRaw); Serial.print(",");
  Serial.print(t); Serial.print(",");
  Serial.print(h); Serial.print(",");
  Serial.print(soilPercent); Serial.print(",");
  Serial.print(ax, 3); Serial.print(",");
  Serial.print(ay, 3); Serial.print(",");
  Serial.print(az, 3); Serial.print(",");
  Serial.print(moveFlag); Serial.print(",");
  Serial.println(status);

  // === Human-readable output (for screenshots) ===
  Serial.print("Soil Moisture: "); Serial.print(soilPercent); Serial.print("%  ");
  Serial.print("Temp: "); Serial.print(t); Serial.print("°C  ");
  Serial.print("Humidity: "); Serial.print(h); Serial.print("%  ");
  Serial.print("Disturbance: "); Serial.print(moveFlag); Serial.print("  ");
  Serial.print("Status: "); Serial.println(status);

  delay(5000); // sample every 5s
}