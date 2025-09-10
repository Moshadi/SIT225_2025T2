#include <Arduino_LSM6DS3.h>

const unsigned long SAMPLE_INTERVAL_MS = 40; // ~25 Hz: balances detail vs. serial bandwidth
unsigned long lastSample = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }
  if (!IMU.begin()) {
    Serial.println("IMU init failed");
    while (1);
  }
  // Optional: set gyro range/ODR via underlying driver if needed; default is fine for this task
  Serial.println("x,y,z"); // CSV header (optional)
}

void loop() {
  if (millis() - lastSample >= SAMPLE_INTERVAL_MS) {
    lastSample = millis();
    float x, y, z;
    if (IMU.gyroscopeAvailable() && IMU.readGyroscope(x, y, z)) {
      // Print CSV line: x,y,z (computer will add timestamp)
      Serial.print(x, 6); Serial.print(",");
      Serial.print(y, 6); Serial.print(",");
      Serial.println(z, 6);
    }
  }
}
