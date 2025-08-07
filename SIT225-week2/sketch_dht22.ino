/*
    Ahsan Habib (habib@deakin.edu.au),
    School of Information Technology,
    Deakin University, Australia.
*/

// Add "DHT sensor library"
// from Arduino IDE Library Manager.
#include <DHT.h>

#define DHTPIN 2  // digital pin number
#define DHTTYPE DHT22  // DHT type 11 or 22
DHT dht(DHTPIN, DHTTYPE);

// variables to store data.
float hum, temp;

void setup() {
  // Set baud rate for serial communication
  Serial.begin(9600);

  // initialise DHT libarary
  dht.begin();
}

void loop() {
  // read data
  hum = dht.readHumidity();
  temp = dht.readTemperature();

  // Print data to serial port - a long way
  // 
  // Serial.print("Humid: ");
  // Serial.print(hum);
  // Serial.print(" %, Temp: ");
  // Serial.print(temp);
  // Serial.println(" Celsius");

  // Print data to serial port - a compact way
  Serial.println(String(hum) + "," + String(temp));
  
  // wait a while
  delay(15*1000);
}
