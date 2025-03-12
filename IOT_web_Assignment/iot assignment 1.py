import network
import socket
import time
from machine import Pin, SoftI2C
from neopixel import NeoPixel
import ssd1306
import dht

# WiFi Credentials (Modify as needed)
SSID = "NTU FSD"
PASSWORD = ""

# Set up AP Mode Credentials
AP_SSID = "ESP32_AP"
AP_PASSWORD = "12345678"

# Initialize Station Mode
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(SSID, PASSWORD)

# Initialize AP Mode
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=network.AUTH_WPA2_PSK)

# Wait for WiFi connection
for i in range(10):
    if sta.isconnected():
        break
    time.sleep(1)

# Get IP addresses
sta_ip = sta.ifconfig()[0] if sta.isconnected() else "Not Connected"
ap_ip = ap.ifconfig()[0]

print(f"STA IP: {sta_ip}")
print(f"AP IP: {ap_ip}")

# Setup NeoPixel (RGB LED) on GPIO48
rgb_pin = Pin(48, Pin.OUT)
neo = NeoPixel(rgb_pin, 1)

# Setup DHT11 on GPIO4
dht_sensor = dht.DHT11(Pin(4))

# Setup OLED on I2C (GPIO8 = SDA, GPIO9 = SCL)
i2c = SoftI2C(scl=Pin(9), sda=Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

def update_oled(msg):
    oled.fill(0)
    oled.text(msg, 0, 0)
    oled.show()

def web_page():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
    except:
        temp, humidity = "--", "--"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Webserver</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; background-color: #e3f2fd; }}
        h1 {{ color: #1565c0; }}
        .container {{ max-width: 400px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); }}
        .btn {{ display: inline-block; padding: 15px; margin: 10px; background: #007BFF; color: white; text-decoration: none; border-radius: 5px; border: none; cursor: pointer; font-size: 16px; }}
        .btn:hover {{ background: #0056b3; }}
        input[type="text"] {{ padding: 10px; width: 80%; margin-top: 10px; border-radius: 5px; border: 1px solid #ddd; }}
        input[type="submit"] {{ padding: 10px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32 RGB LED & Sensor Control</h1>
        <p><strong>Temperature:</strong> {temp}&deg;C</p>
        <p><strong>Humidity:</strong> {humidity}%</p>
        <button class="btn" onclick="window.location.href='/?RGB=red'">Red</button>
        <button class="btn" onclick="window.location.href='/?RGB=green'">Green</button>
        <button class="btn" onclick="window.location.href='/?RGB=blue'">Blue</button>
        <form action="/msg">
            <input type="text" name="message" placeholder="Enter OLED Message">
            <input type="submit" value="Send">
        </form>
    </div>
</body>
</html>"""

    return html

# Start Web Server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 80))  # Listen on all available interfaces
s.listen(5)

while True:
    conn, addr = s.accept()
    print(f"Connection from {addr}")
    
    request = conn.recv(1024).decode()
    print("Request:", request)

    if "/?RGB=red" in request:
        neo[0] = (255, 0, 0)
        neo.write()
    elif "/?RGB=green" in request:
        neo[0] = (0, 255, 0)
        neo.write()
    elif "/?RGB=blue" in request:
        neo[0] = (0, 0, 255)
        neo.write()
    elif "/msg?message=" in request:
        msg_start = request.find("message=") + 8
        msg_end = request.find(" ", msg_start)
        message = request[msg_start:msg_end].replace("+", " ")
        update_oled(message)

    response = web_page()
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n")
    conn.send(response)
    conn.close()
