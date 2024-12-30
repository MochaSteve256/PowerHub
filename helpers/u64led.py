import time
import board
import neopixel
PIN = board.D18
PIXEL_COUNT = 64
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(PIN, PIXEL_COUNT, brightness=0.2, auto_write=False, pixel_order=ORDER)
def wheel(pos):
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

def rainbow_cycle(wait):
    for j in range(255):
        for i in range(PIXEL_COUNT):
            pixel_index = (i * 256 // PIXEL_COUNT) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

def set_matrix(matrix):
    for j in range(8):
        for i in range(8):
            pixels[j * 8 + i] = matrix[j][i]
    pixels.show()

def get_matrix():
    matrix = []
    for j in range(8):
        matrix.append([])
        for i in range(8):
            matrix[j].append(pixels[j * 8 + i])
    return matrix

if __name__ == '__main__':
    print('U64 LED Matrix Module test script')
    print('[Press CTRL + C to end the script!]')
    try:
        while True:
            pixels.fill((255, 0, 0))
            pixels.show()
            time.sleep(1)
            pixels.fill((0, 255, 0))
            pixels.show()
            time.sleep(1)
            pixels.fill((0, 0, 255))
            pixels.show()
            time.sleep(1)
            rainbow_cycle(0.001)
            pixels.fill((0, 0, 0))
            pixels.show()
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nScript end!')
