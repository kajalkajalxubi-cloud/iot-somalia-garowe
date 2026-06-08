#include <Wire.h>
#include "RTClib.h"
#include <WiFi.h>

RTC_DS3231 rtc;

// Xogta Wi-Fi-ga si markii ugu horreysay looga qaado waqtiga internet-ka
const char* ssid     = "MAGACA_WIFI_GAAGA";
const char* password = "PASSWORD_KA_WIFI_GAAGA";

void setup() {
  Serial.begin(115200);

  // Bilaabidda Hardware-ka RTC
  if (!rtc.begin()) {
    Serial.println("Cillad: Ma helin qalabka DS3231 RTC!");
    while (1);
  }

  // Ku xirmaya Wi-Fi si saacadda loo saxo markii ugu horreysay
  WiFi.begin(ssid, password);
  int isku_day = 0;
  while (WiFi.status() != WL_CONNECTED && isku_day < 20) {
    delay(500);
    Serial.print(".");
    isku_day++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi waa ku xirmay! Waxaan dhowraynaa waqtiga internetka...");
    // Waxay si otomaatig ah ugu dhex kaydinaysaa saacadda rasmiga ah gudaha DS3231 RTC
    configTime(10800, 0, "pool.ntp.org"); // +3 GMT East Africa
    struct tm timeinfo;
    if (getLocalTime(&timeinfo)) {
      rtc.adjust(DateTime(timeinfo.tm_year + 1900, timeinfo.tm_mon + 1, timeinfo.tm_mday, timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec));
      Serial.println("RTC Hardware-ka waa la saxay oo la isku waafajiyay internetka!");
    }
  } else {
    Serial.println("\nWi-Fi lama helin. RTC wuxuu isticmaalayaa waqtigii hore ugu keydsanaa.");
  }
}

void loop() {
  // Akhrinta waqtiga rasmiga ah ee ka imaanaya Hardware-ka RTC (Xataa haddii Wi-Fi ka maqan yahay)
  DateTime now = rtc.now();

  Serial.println("=========================================");
  Serial.print("REAL TIMER (RTC): ");
  Serial.print(now.year(), DEC);   Serial.print('/');
  Serial.print(now.month(), DEC);  Serial.print('/');
  Serial.print(now.day(), DEC);    Serial.print("   ");
  Serial.print(now.hour(), DEC);   Serial.print(':');
  Serial.print(now.minute(), DEC); Serial.print(':');
  Serial.print(now.second(), DEC); Serial.println();
  
  // Hubinta Heerkulka Chip-ka RTC (Wuxuu muujiyaa caafimaadka aaladda)
  Serial.print("Heerkulka RTC Chip: ");
  Serial.print(rtc.getTemperature());
  Serial.println(" C");
  Serial.println("=========================================");

  delay(1000); // Wuxuu soo cusboonaysiigayaa ilbiriqsi kasta
}
