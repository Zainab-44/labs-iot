# setup static ip for esp32

import network
import utime as time

WIFI_SSID = 'NTU FSD'
WIFI_PASS = ''

# Static IP configuration
STATIC_IP = "10.13.40.10"  # Replace with your desired static IP/
SUBNET_MASK = "255.255.248.0"
GATEWAY = "10.13.40.1"  # Replace with your router's IP/hotspot
DNS_SERVER = "8.8.8.8"  # Google DNS



print("Connecting to WiFi network '{}'".format(WIFI_SSID))
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

wifi.ifconfig((STATIC_IP, SUBNET_MASK, GATEWAY, DNS_SERVER))

wifi.connect(WIFI_SSID, WIFI_PASS)
while not wifi.isconnected():
    time.sleep(1)
    print('WiFi connect retry ...')
print('WiFi IP:', wifi.ifconfig()[0])