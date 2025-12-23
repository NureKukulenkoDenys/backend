#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

// Wokwi WiFi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// 🔥 Render backend + sensor_id
const char* serverUrl =
  "https://backend-0ngr.onrender.com/iot/sensors/1/data";

WiFiClientSecure client;
HTTPClient http;

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");

  // ⚠️ Wokwi / ESP32 — відключаємо перевірку SSL сертифіката
  client.setInsecure();
}

void loop() {
  // 1️⃣ Вимірювання газу (емуляція)
  int gasValue = random(1, 2000);

  Serial.print("CO2 value: ");
  Serial.println(gasValue);

  // 2️⃣ Надсилання на бек
  if (WiFi.status() == WL_CONNECTED) {
    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");

    String body = "{\"value\": " + String(gasValue) + "}";

    int responseCode = http.POST(body);

    Serial.print("Server response: ");
    Serial.println(responseCode);

    http.end();
  } else {
    Serial.println("WiFi disconnected");
  }

  delay(5000);
}
