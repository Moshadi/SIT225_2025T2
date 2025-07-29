const int ledPin = 13;

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  while (!Serial);  // Wait for serial connection
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    int blinkTimes = input.toInt();

    // Blink LED
    for (int i = 0; i < blinkTimes; i++) {
      digitalWrite(ledPin, HIGH);
      delay(500);
      digitalWrite(ledPin, LOW);
      delay(500);
    }

    // Send back random number between 1–5
    int randomDelay = random(1, 6);
    Serial.println(randomDelay);
  }
}
