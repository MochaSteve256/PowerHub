import time
import RPi.GPIO as GPIO # type: ignore

# Import the WS2801 module.
import Adafruit_WS2801 # type: ignore
import Adafruit_GPIO.SPI as SPI # type: ignore

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

def brightness_decrease(pixels, wait=0.01):
    for j in range(int(256 // 1)):
        for i in range(pixels.count()):
            r, g, b = pixels.get_pixel_rgb(i)
            r = int(max(0, r - 1))
            g = int(max(0, g - 1))
            b = int(max(0, b - 1))
            pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( r, g, b ))
        pixels.show()
        time.sleep(wait)

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


## Transitions

def fade_cx_cy(x, start, end, time):
    """
    Fade the pixel at position x from start color to end color over time.

    Args:
        x (int): The position of the pixel.
        start (tuple): The starting RGB color.
        end (tuple): The ending RGB color.
        time (float btwn 0 and 1): The time to interpolate over.

    Returns:
        tuple: The RGB color of the pixel at this time.
    """
    return Adafruit_WS2801.RGB_to_color(int(start[0] + (end[0] - start[0]) * time), int(start[1] + (end[1] - start[1]) * time), int(start[2] + (end[2] - start[2]) * time))

def argb_cycle(x, time):
    """
    Cycle the pixel at position x through the ARGB color wheel.

    Args:
        x (int): The position of the pixel.
        time (ever-increasing float): The time to interpolate over.

    Returns:
        tuple: The RGB color of the pixel at this time.
    """
    return wheel(((x * 256 // pixels.count()) + int(-time * 256)) % 256)

def fade_black_argb(x, time):
    """
    Fade the pixel at position x from black to its color over time.

    Args:
        x (int): The position of the pixel.
        time (float btwn 0 and 1): The time to interpolate over.

    Returns:
        tuple: The RGB color of the pixel at this time.
    """
    if x / pixels.count() < time:
        return wheel(((x * 256 // pixels.count())) % 256)
    else:
        return Adafruit_WS2801.RGB_to_color(0, 0, 0)

def fade_cx_argb(x, start, time):
    #first cx to black, then black to argb
    """
    Fade the pixel at position x from start color to its color over time.

    Args:
        x (int): The position of the pixel.
        start (tuple): The starting RGB color.
        time (float btwn 0 and 2): The time to interpolate over.

    Returns:
        tuple: The RGB color of the pixel at this time.
    """
    #cx to black
    if time < 1:
        return fade_cx_cy(x, start, (0, 0, 0), time)
    #black to argb
    else:
        return fade_black_argb(x, time - 1)

def rgb_cycle(x, time):
    """
    Cycle the pixel at position x through the RGB color wheel.

    Args:
        x (int): The position of the pixel.
        time (ever-increasing float): The time to interpolate over.

    Returns:
        tuple: The RGB color of the pixel at this time.
    """
    return wheel(((1 * 256 // pixels.count()) + int(time * 256)) % 256)

def fade_black_rgb(x, time):
    """
    Fade the pixel at position x from black to the start color of the RGB color wheel.
    
    Args:
        x (int): The position of the pixel.
        time (float btwn 0 and 1): The time to interpolate over.

    Returns:
        tuple: The RGB color of the pixel at this time.
    """
    return fade_cx_cy(x, (0, 0, 0), wheel(((1 * 256 // pixels.count())) % 256), time)

def fade_cx_rgb(x, start, time):
    #first cx to black, then black to rgb
    """
    Fade the pixel at position x from start color to the start color of the RGB color wheel over time.

    Args:
        x (int): The position of the pixel.
        start (tuple): The starting RGB color.
        time (float btwn 0 and 2): The time to interpolate over.

    Returns:
        tuple: The RGB color of the pixel at this time.
    """
    #cx to black
    if time < 1:
        return fade_cx_cy(x, start, (0, 0, 0), time)
    #black to rgb
    else:
        return fade_black_rgb(x, time - 1)

if __name__ == '__main__':
    set_all((0, 0, 0))
    time.sleep(2)
    t = time.time()
    while time.time() - t < 20:
        if time.time() - t < 1:
            arr = [fade_cx_cy(i, (0, 0, 0), (255, 255, 220), (time.time() - t)) for i in range(pixels.count())]
            set_array(arr)
        elif time.time() - t < 3 and time.time() - t > 1:
            arr = [fade_cx_argb(i, (255, 255, 220), (time.time() - t - 1)) for i in range(pixels.count())]
            set_array(arr)
        elif time.time() - t < 10 and time.time() - t > 3:
            arr = [argb_cycle(i, time.time() - t - 3) for i in range(pixels.count())]
            set_array(arr)
        elif time.time() - t < 12 and time.time() - t > 10:
            arr = [fade_cx_rgb(i, pixels.get_pixel_rgb(i), (time.time() - t - 10)) for i in range(pixels.count())]
            set_array(arr)
        elif time.time() - t < 19 and time.time() - t > 12:
            arr = [rgb_cycle(i, time.time() - t - 12) for i in range(pixels.count())]
            set_array(arr)
        elif time.time() - t > 19:
            arr = [fade_cx_cy(i, pixels.get_pixel_rgb(i), (0, 0, 0), (time.time() - t - 19)) for i in range(pixels.count())]
        time.sleep(0.01)