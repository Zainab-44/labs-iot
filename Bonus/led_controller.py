import network
import time
import BlynkLib
from machine import Pin, PWM

# WiFi Credentials
WIFI_SSID = "HUAWEI-D2B5"
WIFI_PASS = "bRN348z8"

# Blynk Auth Token
BLYNK_AUTH = "9tAzfCRBhROR4n6Q-jc4NIF8qi_lgkWm"

# Connect to WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

while not wifi.isconnected():
    time.sleep(1)
print("Connected to WiFi:", wifi.ifconfig())

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# Define GPIO pins for RGB LED (with duty cycle initialized to 0)
red = PWM(Pin(14), freq=1000, duty=0)  # D5
green = PWM(Pin(12), freq=1000, duty=0)  # D6
blue = PWM(Pin(13), freq=1000, duty=0)  # D7

# For Common Anode: Convert values (255 = OFF, 0 = ON)
COMMON_ANODE = False  # Change to True if using a common anode LED

# Function to set RGB LED brightness
def set_rgb(r, g, b):
    if COMMON_ANODE:
        r, g, b = 255 - r, 255 - g, 255 - b  # Invert values for common anode LED

    # Ensure values are within 0-255 before scaling
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    # Scale to 0-1023 for ESP8266/ESP32 (Fixing your error)
    red.duty(int(r * 4.012))  # 255 * 4.012 = 1023
    green.duty(int(g * 4.012))
    blue.duty(int(b * 4.012))

# Blynk Virtual Pin Handlers for Switches
@blynk.on("V0")  # Red Switch
def v0_handler(value):
    print("Received from V0 (Red Switch):", value)
    
@blynk.on("V0")  # Red Switch
def v1_handler(value):
    print("Received from V1 (green Switch):", value)  # Debugging
    if int(value[0]) == 1:
        red.duty(1023)  # ON
    else:
        red.duty(0)  # OFF
@blynk.on("V2")  # Red Switch
def v2_handler(value):
    print("Received from V2 (blue Switch):", value)  # Debugging
    if int(value[0]) == 1:
        blue.duty(1023)  # ON
    else:
        blue.duty(0)  # OFF
# Main loop
while True:
    blynk.run()