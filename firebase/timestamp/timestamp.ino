#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <time.h>

// WiFi Credentials
const char* ssid = "NTU FSD";
const char* password = "";

// Firebase Configuration
const String FIREBASE_HOST = "lab11-iot-32b5d-default-rtdb.firebaseio.com/";
const String FIREBASE_AUTH = "0bU4g0lfOWmxiXy3Zc9J3QhdizWs0LtJ7irqrfGK";
const String FIREBASE_PATH = "/sensor_data.json";

// DHT Sensor
#define DHTPIN 4       // GPIO4
#define DHTTYPE DHT11  // Change to DHT22 if needed

// Timing
const unsigned long SEND_INTERVAL = 10000;  // 10 seconds
const unsigned long SENSOR_DELAY = 2000;    // 2 seconds between reads

DHT dht(DHTPIN, DHTTYPE);
unsigned long lastSendTime = 0;
unsigned long lastReadTime = 0;

// ======= Setup ======= //
void setup() {
  Serial.begin(115200);
  Serial.println("\nESP32-S3 DHT11 Firebase Monitor");

  dht.begin();
  connectWiFi();
  setupTime();
}

// ======= Main Loop ======= //
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (millis() - lastReadTime >= SENSOR_DELAY) {
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();

    if (!isnan(temp) && !isnan(hum)) {
      Serial.printf("DHT Read: %.1f°C, %.1f%%\n", temp, hum);

      if (millis() - lastSendTime >= SEND_INTERVAL) {
        sendToFirebase(temp, hum);
        lastSendTime = millis();
      }
    } else {
      Serial.println("Failed to read from DHT sensor.");
    }

    lastReadTime = millis();
  }
}

// ======= WiFi Functions ======= //
void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.disconnect(true);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 15) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi Connection Failed!");
  }
}

// ======= NTP Time Setup ======= //
void setupTime() {
  configTime(5 * 3600, 0, "pool.ntp.org", "time.nist.gov");  // UTC+5 for Pakistan
  Serial.println("Waiting for NTP time sync...");
  time_t now = time(nullptr);
  while (now < 8 * 3600 * 2) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }
  Serial.println("\nTime synchronized");
}

// ======= Firebase Functions ======= //
void sendToFirebase(float temp, float humidity) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected. Cannot send to Firebase.");
    return;
  }

  // Get current time
  time_t now = time(nullptr);
  struct tm* timeInfo = localtime(&now);
  char timeString[30];
  strftime(timeString, sizeof(timeString), "%Y-%m-%d %H:%M:%S", timeInfo);

  // Build JSON payload
  String jsonPayload = "{\"temperature\":" + String(temp) +
                       ",\"humidity\":" + String(humidity) +
                       ",\"timestamp\":\"" + String(timeString) + "\"}";

  Serial.println("Sending to Firebase:");
  Serial.println(jsonPayload);

  HTTPClient http;
  String url = "https://" + FIREBASE_HOST + FIREBASE_PATH + "?auth=" + FIREBASE_AUTH;

  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(jsonPayload);
  if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_ACCEPTED) {
    Serial.println("Firebase update successful");
  } else {
    Serial.printf("Firebase error: %d\n", httpCode);
  }

  http.end();
}
