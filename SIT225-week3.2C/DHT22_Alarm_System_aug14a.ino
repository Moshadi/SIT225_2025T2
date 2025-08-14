#include "arduino_secrets.h"
#include "thingProperties.h"
#include <DHT.h>

// ----- DHT22 wiring/config -----
#define DHTPIN 2          // DHT22 data pin -> D2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// ----- Alarm policy (edit if you want) -----
const float MIN_TEMP = 15.0;                // safe lower bound (°C)
const float MAX_TEMP = 35.0;                // safe upper bound (°C)
const unsigned long ALARM_HOLD_MS = 5000;   // must be bad for 5s

// ----- Internal state -----
unsigned long outOfRangeSince = 0;

void setup() {
  Serial.begin(9600);
  delay(1500);

  // Start sensor
  dht.begin();

  // Init IoT Cloud properties (from thingProperties.h)
  initProperties();

  // Connect to Arduino IoT Cloud
  ArduinoCloud.begin(ArduinoIoTPreferredConnection);
  setDebugMessageLevel(2);
  ArduinoCloud.printDebugInfo();

  // Initial values (these are the variables declared in thingProperties.h)
  alarmState = false;
  resetAlarm = false;
  alarmText  = "SAFE";
}

void loop() {
  // Keep cloud connection alive & sync variables
  ArduinoCloud.update();

  // Read temperature (°C)
  float t = dht.readTemperature();
  if (isnan(t)) {
    Serial.println("DHT read failed");
    delay(500);
    return;
  }

  // Publish live value to the cloud gauge
  temperature = t;

  // Check policy
  bool outOfRange = (t < MIN_TEMP) || (t > MAX_TEMP);
  unsigned long now = millis();

  if (outOfRange) {
    if (outOfRangeSince == 0) outOfRangeSince = now;

    // Only trip the alarm if the violation is sustained for ALARM_HOLD_MS
    if (!alarmState && (now - outOfRangeSince >= ALARM_HOLD_MS)) {
      alarmState = true;  // LED goes red on dashboard
      alarmText  = String("ALERT: ") + String(t, 1) + "°C";
      Serial.println("Alarm latched");
    }
  } else {
    // Back in safe range; clear timer
    outOfRangeSince = 0;
    // Only show SAFE if not latched
    if (!alarmState) alarmText = "SAFE";
  }

  // (Optional) small pacing delay
  delay(1000);
}

/* ========= Cloud callbacks required by your thingProperties.h =========
   Your header declares these four. We only need to *use* resetAlarm
   to clear the latched alarm; the rest can be empty stubs.
*/

// Called when alarmText is changed *from the dashboard* (RW in your header)
void onAlarmTextChange() {
  // Normally we wouldn't let users edit alarmText; leave empty.
}

// Called when temperature is changed *from the dashboard* (RW in your header)
void onTemperatureChange() {
  // temperature should be device-driven; leave empty.
}

// Called when alarmState is changed *from the dashboard* (RW in your header)
void onAlarmStateChange() {
  // If you want manual override from dashboard, you could honor it:
  // e.g., if (!alarmState) { alarmText = "SAFE"; outOfRangeSince = 0; }
}

// Called when resetAlarm is toggled in the dashboard
void onResetAlarmChange() {
  if (resetAlarm) {           // only act when switched on
    alarmState = false;       // clear the latch
    alarmText  = "SAFE";
    outOfRangeSince = 0;
    resetAlarm = false;       // auto-return the switch to off
    Serial.println("Alarm reset from dashboard");
  }
}
