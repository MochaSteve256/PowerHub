import time
import RPi.GPIO as GPIO

# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

# Configure the count of pixels:
PIXEL_COUNT = 96

# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0
pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)


# Define the wheel function to interpolate between different hues.
def wheel(pos):
    if pos < 85:
        return Adafruit_WS2801.RGB_to_color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Adafruit_WS2801.RGB_to_color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Adafruit_WS2801.RGB_to_color(0, pos * 3, 255 - pos * 3)

def set_all(color):
    for i in range(pixels.count()):
        pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
    pixels.show()

def set_pixel(i, color):
    pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
    pixels.show()

def set_array(arr):
    for i in arr:
        pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( arr[i][0], arr[i][1], arr[i][2] ))
    pixels.show()

def clear():
    for i in range(pixels.count()):
        pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( 0, 0, 0 ))
    pixels.show()

if __name__ == '__main__':
    try:
        for i in range(pixels.count()):
            pixels.set_pixel(i, wheel(((i * 256 // pixels.count())) % 256) )
            pixels.show()
            time.sleep(0.03)

        while 1:
            for j in range(256):
                for i in range(pixels.count()):
                    pixels.set_pixel(i, wheel(((i * 256 // pixels.count()) + j) % 256) )
                pixels.show()
                time.sleep(0.0001)

    except KeyboardInterrupt:
        for j in range(int(256 // 1)):
            for i in range(pixels.count()):
                r, g, b = pixels.get_pixel_rgb(i)
                r = int(max(0, r - 1))
                g = int(max(0, g - 1))
                b = int(max(0, b - 1))
                pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( r, g, b ))
            pixels.show()
            time.sleep(0.01)
