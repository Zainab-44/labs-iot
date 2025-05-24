#include <Adafruit_NeoPixel.h>

#define NEOPIXEL_PIN 48  // Use 38 for v1.1 of your board
#define NUMPIXELS 1      // Number of NeoPixels

Adafruit_NeoPixel pixels(NUMPIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  pixels.begin();         // Initialize NeoPixel
  pixels.setBrightness(50); // Optional: Set brightness (0-255)
}

void loop() {
  // Red
  pixels.setPixelColor(0, pixels.Color(255, 0, 0));
  pixels.show();
  delay(1000);
  
  // Green
  pixels.setPixelColor(0, pixels.Color(0, 255, 0));
  pixels.show();
  delay(1000);
  
  // Blue
  pixels.setPixelColor(0, pixels.Color(0, 0, 255));
  pixels.show();
  delay(1000);
}