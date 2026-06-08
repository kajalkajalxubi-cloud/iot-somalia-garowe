#include <WiFi.h>
#include "time.h"

const char* ssid     = "MAGACA_WIFI-GAAGA";
const char* password = "PASSWORD-KA_WIFI-GAAGA";

const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 10800; // Ku habbee saacadda deegaankaaga (+3 GMT)
const int   daylightOffset_sec = 0;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
}

void loop() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Waqtiga lama helin");
    return;
  }
  Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");
  delay(1000);
}
