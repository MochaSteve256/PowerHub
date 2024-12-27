## RGB values for 8x8 matrix

#colors
black  = [0, 0, 0]
pink   = [170 // 2, 50 // 2, 50 // 2]
purple = [80 // 2, 60 // 2, 150 // 2]
orange = [150 // 2, 100 // 2, 0]
red    = [64, 0, 0]
green  = [0, 64, 0]
blue   = [0, 0, 64]


#psu
psu_text = [
    [pink, pink,  pink,  purple, purple, pink,  black, pink],
    [pink, black, pink,  purple, black,  pink,  black, pink],
    [pink, pink,  black, purple, purple, pink,  black, pink],
    [pink, black, black, black,  purple, pink,  black, pink],
    [pink, black, black, purple, purple, black, pink,  pink]
]

psu_on = [
    [black, green, green, green, green, green, green, black],
    [black, green, green, green, green, green, green, black],
    [black, black, black, black, black, black, black, black]
]

psu_off = [
    [black, red,   red,   red,   red,   red,   red,    black],
    [black, red,   red,   red,   red,   red,   red,   black ],
    [black, black, black, black, black, black, black, black ]
]

#standby
stby_text = [
    [pink,  pink,  purple, purple, purple, orange, black,  orange],
    [pink,  black, black,  purple, black,  orange, black,  orange],
    [pink,  pink,  black,  pink,   pink,   black,  orange, orange],
    [black, pink,  black,  pink,   black,  pink,   black,  orange],
    [pink,  pink,  black,  pink,   pink,   black,  orange, black ],
    [black, black, black,  pink,   black,  pink,   black,  black ],
    [black, black, black,  pink,   pink,   black,  black,  black ],
    [black, black, black,  black,  black,  black,  black,  black ]
]

#led
led_text = [
    [pink, black, purple, purple, purple, pink, pink,  black],
    [pink, black, purple, black,  black,  pink, black, pink ],
    [pink, black, purple, purple, purple, pink, black, pink ],
    [pink, black, purple, black,  black,  pink, black, pink ],
    [pink, pink,  purple, purple, purple, pink, pink,  black],
]


nothing = [
    [black, black, black, black, black, black, black, black],
    [black, black, black, black, black, black, black, black],
    [black, black, black, black, black, black, black, black]
]

blank = [
    [black, black, black, black, black, black, black, black],
    [black, black, black, black, black, black, black, black],
    [black, black, black, black, black, black, black, black],
    [black, black, black, black, black, black, black, black],
    [black, black, black, black, black, black, black, black],
    [black, black, black, black, black, black, black, black],
    [black, black, black, black, black, black, black, black],
    [black, black, black, black, black, black, black, black]
]

#nav bar
navbar_scroll = [black, black, blue,  blue,  blue,  blue,  black, black]
navbar_back   = [blue,  black, black, black, black, black, black, black]
navbar_select = [black, black, black, black, black, black, black, blue ]
#overlay navbar elements
navbar_full = [
    [
        navbar_scroll[i][j] + navbar_back[i][j] + navbar_select[i][j]
        for j in range(len(navbar_scroll[0]))
    ]
    for i in range(len(navbar_scroll))
]
def add_navbar(matrix, select, back, scroll):
    if select and back and scroll:
        for i in range(8):
            matrix[7][i] = [navbar_scroll[i][j] + navbar_back[i][j] + navbar_select[i][j] for j in range(3)]
    elif select and back:
        for i in range(8):
            matrix[7][i] = [navbar_back[i][j] + navbar_select[i][j] for j in range(3)]
    elif select and scroll:
        for i in range(8):
            matrix[7][i] = [navbar_scroll[i][j] + navbar_select[i][j] for j in range(3)]
    elif back and scroll:
        for i in range(8):
            matrix[7][i] = [navbar_scroll[i][j] + navbar_back[i][j] for j in range(3)]
    elif select:
        for i in range(8):
            matrix[7][i] = [navbar_select[i][j] for j in range(3)]
    elif back:
        for i in range(8):
            matrix[7][i] = [navbar_back[i][j] for j in range(3)]
    elif scroll:
        for i in range(8):
            matrix[7][i] = [navbar_scroll[i][j] for j in range(3)]

    return matrix

numbers = [
    [[black, pink, black], [pink, black, pink], [pink, black, pink], [pink, black, pink], [pink, black, pink], [black, pink, black]],
    [[black, black, pink], [black, pink, pink], [pink, black, pink], [black, black, pink], [black, black, pink], [black, black, pink]],
    [[black, pink, black], [pink, black, pink], [black, black, pink], [black, pink, black], [pink, black, black], [pink, pink, pink]],
    [[pink, pink, pink], [black, black, pink], [black, pink, black], [black, black, pink], [pink, black, pink], [black, pink, black]],
    [[black, pink, black], [black, pink, black], [pink, black, black], [pink, black, pink], [pink, pink, pink], [black, black, pink]],
    [[pink, pink, pink], [pink, black, black], [pink, pink, black], [black, black, pink], [black, black, pink], [pink, pink, black]],
    [[black, pink, black], [pink, black, pink], [pink, black, black], [pink, pink, black], [pink, black, pink], [black, pink, black]],
    [[pink, pink, pink], [black, black, pink], [black, pink, black], [black, pink, black], [pink, black, black], [pink, black, black]],
    [[black, pink, black], [pink, black, pink], [black, pink, black], [pink, black, pink], [pink, black, pink], [black, pink, black]],
    [[black, pink, pink], [pink, black, pink], [black, pink, pink], [black, black, pink], [black, pink, black], [black, pink, black]]
]

def number_to_matrix(number):
    matrix = blank
    for z in range(2):
        for i in range(3):
            for j in range(6):
                if z == 0:
                    matrix[j][i + 1] = numbers[int(str(number)[z])][j][i]
                else:
                    matrix[j][i + 1] = numbers[int(str(number)[z])][j][i]

if __name__ == '__main__':
    import u64led
    #u64led.set_matrix(add_navbar(psu_text + psu_on, True, False, True))
    u64led.set_matrix(add_navbar(number_to_matrix(12), False, False, True))