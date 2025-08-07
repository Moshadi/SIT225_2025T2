#include "DHT.h"

#define DHTPIN 2       // Digital pin where data line is connected
#define DHTTYPE DHT22  // Use DHT22 (AM2302)

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  float temp = dht.readTemperature();    // Read temperature in Celsius
  float humidity = dht.readHumidity();   // Read humidity %

  if (isnan(temp) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  Serial.print(temp);
  Serial.print(",");
  Serial.println(humidity);

  delay(2000);  // Sampling every 2 seconds
}