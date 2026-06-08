#include <WiFi.h>
#include "time.h"

// Ku qor xogta Wi-Fi-gaaga
const char* ssid     = "MAGACA_WIFI_GAAGA";
const char* password = "PASSWORD_KA_WIFI_GAAGA";

// Habaynta Waqtiga
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 10800; // EAT (East Africa Time) = +3 saac
const int   daylightOffset_sec = 0;

void setup() {
  Serial.begin(115200);
  
  // Ku xiridda Wi-Fi
  Serial.print("Ku xirmaya: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi waa ku xirmay!");

  // Bilaabidda saacadda rasmiga ah
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
}

void loop() {
  // 1. Akhrinta Waqtiga Rasmiga ah (Real-Time)
  struct tm timeinfo;
  if(!getLocalTime(&timeinfo)){
    Serial.println("Cillad: Waqtiga lama helin");
    return;
  }

  // 2. Hubinta Caafimaadka Aaladda (Device Health)
  long rssi = WiFi.RSSI(); // Xoogga internetka (dBm)
  uint32_t freeHeap = ESP.getFreeHeap(); // RAM-ka firaaqada ah
  unsigned long uptimeSec = millis() / 1000; // Waqtiga ay shidantahay

  // 3. Daabicidda Xogta oo Dhammaystiran (U dirista Dashboard-ka)
  Serial.println("=========================================");
  Serial.print("WAQTIGA: ");
  Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");
  
  Serial.println("--- STATUS-KA CAAFIMAADKA AALADDA ---");
  Serial.print("Internetka (Wi-Fi Signal): "); 
  Serial.print(rssi); Serial.println(" dBm");
  
  Serial.print("RAM-ka firaaqada ah: "); 
  Serial.print(freeHeap); Serial.println(" bytes");
  
  Serial.print("Waqtiga ay shidantahay: "); 
  Serial.print(uptimeSec); Serial.println(" ilbiriqsi");
  
  // Halkaan waxaad dhigi kartaa akhriska Solar-ka (sida Volt iyo Ampere)
  Serial.println("Nidaamka Solar-ka: Waa caafimaad qabaa [TRUE]");
  Serial.println("=========================================");

  delay(5000); // Wuxuu soo cusboonaysiigayaa 5-tii ilbiriqsigiiba
}
