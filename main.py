from machine import Pin, SPI
from time import sleep
import max7219
import network
import socket
import re

msg = ''

# Code (mostly) from FideliusFalcon
# Simple text scrolling for max7219 display
# https://github.com/FideliusFalcon/rpi_pico_max7219/blob/main/main.py
class matrix():
    def __init__(self):
        self.MAX7219_NUM = 4
        self.MAX7219_INVERT = False
        self.MAX7219_SCROLL_DELAY = 0.02
        cs_pin = 5

        spi = SPI(0)
        self.display = max7219.Matrix8x8(spi=spi, cs=Pin(cs_pin), num=self.MAX7219_NUM)
        self.display.brightness(1)
    
    def text_scroll(self, text, scroll_delay=None):
        if scroll_delay != None:
            self.MAX7219_SCROLL_DELAY = scroll_delay
        
        p = self.MAX7219_NUM * 8
        for p in range(self.MAX7219_NUM * 8, len(text) * -8 - 1, -1):
            self.display.fill(self.MAX7219_INVERT)
            self.display.text(text, p, 0, not self.MAX7219_INVERT)
            self.display.show()
            sleep(self.MAX7219_SCROLL_DELAY)

    def alert(self):
        self.display.fill(True)
        self.display.show()
        sleep(0.3)
        self.display.fill(False)
        self.display.show()
        sleep(0.3)

led = matrix()
led.alert()

# Code (mostly) from RPi News
# Create webserver
# https://www.raspberrypi.com/news/how-to-run-a-webserver-on-raspberry-pi-pico-w/

# Your WiFi name and password
ssid = ''
password = ''

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('hawkins lab', 'bart2608')

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    sleep(1)

if wlan.status() != 3:
    led.text_scroll('CONN FAIL')
    raise RuntimeError('network connection failed')
else:
    led.text_scroll('CONN SUCCESS')
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

addr = socket.getaddrinfo('0.0.0.0', 8777)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(4096)
       
        print(request.decode())
        # Certain characters like '<' and '>' will still be represented by their url encoded counterparts ('%3c' and '%3e' in this case)
        # The only character I account for here is space
        msg = re.search("\/\?message='.+'", request.decode()).group(0).replace("/?message='", '').replace('%20', ' ')[:-1]
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.close()

        led.alert()
        led.alert()
        led.text_scroll(msg) # Char lim 34 (spaces count as three)

    except Exception as e:
        print(e)
        cl.close()
