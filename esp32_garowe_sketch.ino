#include <Wire.h>
#include "RTClib.h"
#include <WiFi.h>
#include <HTTPClient.h>

RTC_DS3231 rtc;

// Ku xir internetka shirkadaha Garowe (Golis / Somtel)
const char* ssid     = "DHAXAL_WIFI_GAROWE"; // <- beddel magaca WiFi
const char* password = "PASSWORD_KA_WIFI_GAAGA"; // <- beddel password

// Habaynta Waqtiga Rasmiga ah ee Soomaaliya (+3 GMT)
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 10800; // +3 hours
const int   daylightOffset_sec = 0;

// Set this to the machine running flask_ingest.py (example below)
// Replace 192.168.1.100 with your PC or server IP
const char* telemetryServer = "http://192.168.1.100:5000/api/ingest";

// Garowe coordinates
const float GAROWE_LATITUDE = 8.4064;
const float GAROWE_LONGITUDE = 48.4813;

// battery ADC pin
const int batteryPin = 34;

unsigned long lastSendMs = 0;
const unsigned long sendIntervalMs = 5000; // send every 5s

void connectWiFi() {
  Serial.print("Connecting to WiFi ");
  Serial.print(ssid);
  WiFi.begin(ssid, password);
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 30) {
    delay(500);
    Serial.print('.');
    tries++;
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Connected, IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi connect failed");
  }
}

void sendTelemetryArray(String jsonArray) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Skipping telemetry POST: no WiFi");
    return;
  }
  HTTPClient http;
  http.begin(telemetryServer);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(jsonArray);
  if (httpCode > 0) {
    String resp = http.getString();
    Serial.print("POST code: "); Serial.print(httpCode);
    Serial.print(" resp: "); Serial.println(resp);
  } else {
    Serial.print("POST failed, err: "); Serial.println(httpCode);
  }
  http.end();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Wire.begin();
  pinMode(batteryPin, INPUT);

  if (!rtc.begin()) {
    Serial.println("RTC not found");
    while (1) delay(10);
  }

  connectWiFi();

  if (WiFi.status() == WL_CONNECTED) {
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    Serial.println("Waiting for NTP time...");
    struct tm timeinfo;
    if (getLocalTime(&timeinfo)) {
      rtc.adjust(DateTime(timeinfo.tm_year + 1900,
                          timeinfo.tm_mon + 1,
                          timeinfo.tm_mday,
                          timeinfo.tm_hour,
                          timeinfo.tm_min,
                          timeinfo.tm_sec));
      Serial.println("RTC updated from NTP.");
    } else {
      Serial.println("NTP time not available yet.");
    }
  } else {
    Serial.println("Using RTC offline mode.");
  }
}

void loop() {
  DateTime now = rtc.now();

  int analogValue = analogRead(batteryPin);
  float voltage = (analogValue * 3.3 / 4095.0) * 2.0; // voltage divider factor
  int batteryPercentage = map(analogValue, 2048, 4095, 0, 100);
  batteryPercentage = constrain(batteryPercentage, 0, 100);

  long rssi = (WiFi.status() == WL_CONNECTED) ? WiFi.RSSI() : -127;
  uint32_t freeHeap = ESP.getFreeHeap();

  uint32_t epoch = now.unixtime();
  String ts = String(epoch);

  // Build telemetry array compatible with flask_ingest / iot_system
  String rows = "[";
  rows += "{\"device_id\":\"GAROWE_NODE_01\",\"timestamp\":\"" + ts + "\",\"metric\":\"battery_voltage\",\"value\":" + String(voltage,3) + ",\"unit\":\"V\",\"status\":\"\"},";
  rows += "{\"device_id\":\"GAROWE_NODE_01\",\"timestamp\":\"" + ts + "\",\"metric\":\"battery_percent\",\"value\":" + String(batteryPercentage) + ",\"unit\":\"%\",\"status\":\"\"},";
  rows += "{\"device_id\":\"GAROWE_NODE_01\",\"timestamp\":\"" + ts + "\",\"metric\":\"rssi\",\"value\":" + String(rssi) + ",\"unit\":\"dBm\",\"status\":\"\"},";
  rows += "{\"device_id\":\"GAROWE_NODE_01\",\"timestamp\":\"" + ts + "\",\"metric\":\"free_heap\",\"value\":" + String(freeHeap) + ",\"unit\":\"bytes\",\"status\":\"\"}";
  rows += "]";

  Serial.println(rows);

  unsigned long nowMs = millis();
  if (nowMs - lastSendMs >= sendIntervalMs) {
    lastSendMs = nowMs;
    sendTelemetryArray(rows);
  }

  delay(1000);
}
