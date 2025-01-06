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
        for i in range(PIXEL_COUNT):
            r, g, b = pixels.get_pixel_rgb(i)
            r = int(max(0, r - 1))
            g = int(max(0, g - 1))
            b = int(max(0, b - 1))
            pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( r, g, b ))
        pixels.show()
        time.sleep(wait)

def set_all(color):
    for i in range(PIXEL_COUNT):
        pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
    pixels.show()

def set_pixel(i, rgb):
    pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( rgb[0], rgb[1], rgb[2] ))
    pixels.show()

def set_pixel_color(i, color):
    pixels.set_pixel(i, color)
    pixels.show()

def get_pixel_rgb(i):
    return pixels.get_pixel_rgb(i)

def set_array(arr):
    for i in range(min(PIXEL_COUNT, len(arr))):
        pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( arr[i][0], arr[i][1], arr[i][2] ))
    pixels.show()

def set_array_color(arr):
    for i in range(min(PIXEL_COUNT, len(arr))):
        if arr[i] is not None:
            pixels.set_pixel(i, arr[i])
    pixels.show()

def clear():
    for i in range(PIXEL_COUNT):
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
        color: Int Formatted color
    """
    if time > 0 and time < 1:
        return Adafruit_WS2801.RGB_to_color(int(start[0] + (end[0] - start[0]) * time), int(start[1] + (end[1] - start[1]) * time), int(start[2] + (end[2] - start[2]) * time))
    else:
        return Adafruit_WS2801.RGB_to_color(end[0], end[1], end[2])

def argb_cycle(x, time):
    """
    Cycle the pixel at position x through the ARGB color wheel.

    Args:
        x (int): The position of the pixel.
        time (ever-increasing float): The time to interpolate over.

    Returns:
        color: Int Formatted color
    """
    return wheel(((x * 256 // PIXEL_COUNT) + int(-(time / 3) * 256)) % 256)

def fade_black_argb(x, time):
    """
    Fade the pixel at position x from black to its color over time.

    Args:
        x (int): The position of the pixel.
        time (float btwn 0 and 1): The time to interpolate over.

    Returns:
        color: Int Formatted color
    """
    if x / PIXEL_COUNT < time:
        return wheel(((x * 256 // PIXEL_COUNT)) % 256)
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
        color: Int Formatted color
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
        color: Int Formatted color
    """
    return wheel(((1 * 256 // PIXEL_COUNT) + int(time / 3 * 256)) % 256)

def fade_black_rgb(x, time):
    """
    Fade the pixel at position x from black to the start color of the RGB color wheel.
    
    Args:
        x (int): The position of the pixel.
        time (float btwn 0 and 1): The time to interpolate over.

    Returns:
        color: Int Formatted color
    """
    return fade_cx_cy(x, (0, 0, 0), Adafruit_WS2801.color_to_RGB(wheel(((1 * 256 // PIXEL_COUNT)) % 256)), time)

def fade_cx_rgb(x, start, time):
    #first cx to black, then black to rgb
    """
    Fade the pixel at position x from start color to the start color of the RGB color wheel over time.

    Args:
        x (int): The position of the pixel.
        start (tuple): The starting RGB color.
        time (float btwn 0 and 2): The time to interpolate over.

    Returns:
        color: Int Formatted color
    """
    #cx to black
    if time < 1:
        return fade_cx_cy(x, start, (0, 0, 0), time)
    #black to rgb
    else:
        return fade_black_rgb(x, time - 1)

def sunrise(x, time):
    """
    Simulate colors of a sunrise, starting from black.

    Args:
        x (int): The position of the pixel.
        time: The time to interpolate over.

    Returns:
        color: Int Formatted color
    """
    time /= 2
    
    if time < 6 and time > 0:
        return fade_cx_cy(x, (0, 0, 0), (150, 15, 0), time / 6)
    elif time < 12 and time > 6:
        return fade_cx_cy(x, (150, 15, 0), (255, 90, 0), (time - 6) / 6)
    elif time < 24 and time > 12:
        return fade_cx_cy(x, (255, 90, 0), (255, 255, 128), (time - 12) / 12)
    elif time > 24:
        return fade_cx_cy(x, (255, 255, 128), (255, 255, 255), (time - 24) / 6)
    else:
        return Adafruit_WS2801.RGB_to_color(0, 0, 0)

def sunset(x, start, time):
    """
    Simulate colors of a sunset, starting from start color.

    Args:
        x (int): The position of the pixel.
        start (tuple): The starting RGB color.
        time: The time to interpolate over.

    Returns:
        color: Int Formatted color
    """
    result = Adafruit_WS2801.color_to_RGB(sunrise(x, -time + 60))
    if start[0] < result[0]:
        result[0] = start[0]
    if start[1] < result[1]:
        result[1] = start[1]
    if start[2] < result[2]:
        result[2] = start[2]
    return Adafruit_WS2801.RGB_to_color(result[0], result[1], result[2])

def alarm_cycle(x, time):
    """
    Alarm blinking pattern to wake someone up.

    Args:
        x (int): The position of the pixel.
        time: The time to interpolate over.

    Returns:
        color: Int Formatted color
    """
    time = time % 4
    if time < .5:
        return Adafruit_WS2801.RGB_to_color(255, 255, 255)
    elif time < 1 and time > .5:
        return Adafruit_WS2801.RGB_to_color(0, 0, 0)
    elif time < 1.5 and time > 1:
        return Adafruit_WS2801.RGB_to_color(255, 0, 0)
    elif time < 2 and time > 1.5:
        return Adafruit_WS2801.RGB_to_color(0, 0, 0)
    elif time < 2.5 and time > 2:
        return Adafruit_WS2801.RGB_to_color(0, 255, 0)
    elif time < 3 and time > 2.5:
        return Adafruit_WS2801.RGB_to_color(0, 0, 0)
    elif time < 3.5 and time > 3:
        return Adafruit_WS2801.RGB_to_color(0, 0, 255)
    else:
        return Adafruit_WS2801.RGB_to_color(0, 0, 0)
    
if __name__ == '__main__':
    set_all((0, 0, 0))
    time.sleep(1)
    t = time.time()
    """
    while time.time() - t < 20:
        if time.time() - t < 1:
            arr = [fade_cx_cy(i, (0, 0, 0), (255, 255, 220), (time.time() - t)) for i in range(PIXEL_COUNT)]
            set_array_color(arr)
        elif time.time() - t < 3 and time.time() - t > 1:
            arr = [fade_cx_argb(i, (255, 255, 220), (time.time() - t - 1)) for i in range(PIXEL_COUNT)]
            set_array_color(arr)
        elif time.time() - t < 10 and time.time() - t > 3:
            arr = [argb_cycle(i, time.time() - t - 3) for i in range(PIXEL_COUNT)]
            set_array_color(arr)
        elif time.time() - t < 12 and time.time() - t > 10:
            arr = [fade_cx_rgb(i, pixels.get_pixel_rgb(i), (time.time() - t - 10)) for i in range(PIXEL_COUNT)]
            set_array_color(arr)
        elif time.time() - t < 19 and time.time() - t > 12:
            arr = [rgb_cycle(i, time.time() - t - 12) for i in range(PIXEL_COUNT)]
            set_array_color(arr)
        elif time.time() - t > 19:
            arr = [fade_cx_cy(i, pixels.get_pixel_rgb(i), (0, 0, 0), (time.time() - t - 19)) for i in range(PIXEL_COUNT)]
            set_array_color(arr)
        time.sleep(0.01)
    """
    #"""
    while time.time() - t < 120:
        if time.time() - t < 60:
            arr = [sunrise(i, time.time() - t) for i in range(PIXEL_COUNT)]
            set_array_color(arr)
        elif time.time() - t < 60 and time.time() - t > 60:
            arr = [sunset(i,(255, 255, 255), time.time() - t - 60) for i in range(PIXEL_COUNT)]
            set_array_color(arr)
        time.sleep(0.01)
    #"""
    """
    while time.time() - t < 10:
        arr = [alarm_cycle(i, time.time() - t) for i in range(PIXEL_COUNT)]
        set_array_color(arr)
        time.sleep(0.1)
    """
    set_all((0, 0, 0))