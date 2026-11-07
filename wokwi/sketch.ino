// Rocket Launch Weather Monitoring - ESP32 simulated sensor
// Educational demo: values are simulated, not measured.

float temperature = 27.0;  // degrees C
float humidity = 60.0;     // percent
float windSpeed = 10.0;    // km/h

// Returns a small random change between -range and +range
float randomStep(float range) {
  return ((float)random(-100, 101) / 100.0) * range;
}

// Keeps a value between a minimum and a maximum
float limitValue(float value, float minValue, float maxValue) {
  if (value < minValue) return minValue;
  if (value > maxValue) return maxValue;
  return value;
}

void setup() {
  Serial.begin(115200);
  Serial.println("timestamp_ms,temperature,humidity,wind_speed");
}

void loop() {
  temperature = limitValue(temperature + randomStep(0.5), 15.0, 45.0);
  humidity = limitValue(humidity + randomStep(2.0), 20.0, 100.0);
  windSpeed = limitValue(windSpeed + randomStep(3.0), 0.0, 60.0);

  Serial.print(millis());
  Serial.print(",");
  Serial.print(temperature, 1);
  Serial.print(",");
  Serial.print(humidity, 1);
  Serial.print(",");
  Serial.println(windSpeed, 1);

  delay(2000);
}
