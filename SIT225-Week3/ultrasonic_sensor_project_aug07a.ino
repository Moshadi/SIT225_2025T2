#include "arduino_secrets.h"
#include "thingProperties.h"

#define trigPin 2
#define echoPin 3

long duration;
float distance;

void setup() {
  Serial.begin(9600);
  delay(1500); 

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  initProperties();
  ArduinoCloud.begin(ArduinoIoTPreferredConnection);
  setDebugMessageLevel(2);
  ArduinoCloud.printDebugInfo();
}

void loop() {
  ArduinoCloud.update();

  // Trigger the ultrasonic burst
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read echo duration
  duration = pulseIn(echoPin, HIGH);

  // Convert to distance in cm
  distance = duration * 0.034 / 2;

  // Assign to cloud variable
  ultrasonicDistance = distance;

  Serial.println("Distance: " + String(distance) + " cm");

  delay(5000);  // every 5 seconds
}
