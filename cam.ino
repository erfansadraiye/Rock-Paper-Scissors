#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>
#include <HTTPClient.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

#define SOUND_SPEED 0.034
#define CM_TO_INCH 0.393701


const char* WIFI_SSID = "Erfan’s iPhone";
const char* WIFI_PASS = "erferferf";
const char* serverName = "http://172.20.10.4:5000/start_countdown";
const int sendDelay = 3000; // Send delay in milliseconds (3 seconds)

WebServer server(80);

static auto loRes = esp32cam::Resolution::find(320, 240);
static auto hiRes = esp32cam::Resolution::find(800, 600);

const int trigPin = 13;
const int echoPin = 15;
const float minDist = 2;
const float maxDist = 10;

long duration;
float distanceCm;
float distanceInch;

unsigned long lastSendTime = 0; // Store the time of the last request

void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}


void handleJpgLo()
{
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("SET-LO-RES FAIL");
  }
  serveJpg();
}

void handleJpgHi()
{
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}



void setup(){
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); //disable brownout detector
  Serial.begin(19200);
  Serial.println();
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input

  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Cannot Connect to Wi-Fi!");
  }
  Serial.println("Wi-Fi Connected!");
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /cam-hi.jpg");
  Serial.println("  /cam-lo.jpg");

  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-hi.jpg", handleJpgHi);

  server.begin();
}

void loop()
{
  server.handleClient();

  // Distance measurement
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distanceCm = duration * SOUND_SPEED / 2;

  unsigned long currentTime = millis(); // Get current time
  if (currentTime - lastSendTime >= sendDelay) { // Check if 3 seconds have passed since last send
    if (distanceCm > minDist && distanceCm < maxDist) {
      HTTPClient http;
      http.begin(serverName);
      http.addHeader("Content-Type", "application/json");

      String httpPayload = "{\"sensor\":\"distance\", \"value\":";
      httpPayload += distanceCm;
      httpPayload += "}";

      int httpResponseCode = http.POST(httpPayload);
      if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println(httpResponseCode);
        Serial.println(response);
      } else {
        Serial.print("Error on sending POST: ");
        Serial.println(httpResponseCode);
      }
      http.end();

      Serial.println(distanceCm);
      lastSendTime = currentTime; // Update last send time
    }
  }
}