import network
import socket
import machine
import ssd1306
import dht
import time
from machine import Pin

# WiFi Credentials
SSID = "NTU FSD"
PASSWORD = ""

# Connect to WiFi
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(SSID, PASSWORD)
while not station.isconnected():
    pass
print("Connected to WiFi", station.ifconfig())

# Initialize DHT11 Sensor
dht_pin = Pin(4)
dht_sensor = dht.DHT11(dht_pin)

# Initialize OLED Display
i2c = machine.SoftI2C(scl=machine.Pin(9), sda=machine.Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Function to read sensor and determine weather condition
def get_weather_condition():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        if temp > 30:
            condition = "Hot"
        elif temp < 20:
            condition = "Cold"
        else:
            condition = "Moderate"
        
        if humidity > 70:
            condition += " & Humid"
        
        return temp, humidity, condition
    except:
        return None, None, "Sensor Error"

# Function to adjust OLED brightness based on temperature
def adjust_oled_brightness(temp):
    if temp is not None:
        contrast = min(max(int((temp / 40) * 255), 50), 255)
        oled.contrast(contrast)

# Web Page HTML with CSS
def generate_html(temp, humidity, condition):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 Weather Monitor</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                background-color: lightpink;
                color: #333;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 400px;
                margin: auto;
                background: white;
                padding: 20px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }}
            h1 {{
                color: black;
            }}
            p {{
                font-size: 18px;
                margin: 10px 0;
                color: #B266FF
            }}
            .status {{
                font-weight: bold;
                color: #FF5733;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1><i>ESP32 Weather Monitor</i></h1>
            <p>Temperature: <span class="status">{temp if temp is not None else 'N/A'}°C</span></p>
            <p>Humidity: <span class="status">{humidity if humidity is not None else 'N/A'}%</span></p>
            <p>Condition: <span class="status">{condition}</span></p>
        </div>
    </body>
    </html>
    """


# Start Web Server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow address reuse
s.bind(('', 80))
s.listen(5)

while True:
    temp, humidity, condition = get_weather_condition()
    adjust_oled_brightness(temp)
    
    # Update OLED Display
    oled.fill(0)
    oled.text(f"Temp: {temp}C", 0, 0)
    oled.text(f"Humidity: {humidity}%", 0, 10)
    oled.text(f"Condition: {condition}", 0, 20)
    oled.show()
    
    conn, addr = s.accept()
    request = conn.recv(1024).decode()
    response = generate_html(temp, humidity, condition)
    conn.sendall('HTTP/1.1 200 OK\nContent-Type: text/html\n\n' + response)
    conn.close()
    time.sleep(5)
