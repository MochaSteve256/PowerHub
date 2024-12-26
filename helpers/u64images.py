## RGB values for 8x8 matrix

#colors
black  = [0, 0, 0]
pink   = [170, 50, 50]
purple = [100, 60, 140]
red    = [128, 0, 0]
green  = [0, 128, 0]
blue   = [0, 0, 128]


#psu
psu_text = [
    [pink, pink,  pink,  purple, purple, pink,  black, pink],
    [pink, black, pink,  purple, black,  pink,  black, pink],
    [pink, pink,  black, purple, purple, pink,  black, pink],
    [pink, black, black, black,  purple, pink,  black, pink],
    [pink, black, black, purple, purple, black, pink,  pink]
]
for i in range(len(psu_text)):
    for j in range(len(psu_text[i])):
        psu_text[i][j] = [x // 2 for x in psu_text[i][j]]

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

#led
led_text = [[pink, black, purple, purple, purple, pink, pink,  black],
            [pink, black, purple, black,  black,  pink, black, pink ],
            [pink, black, purple, purple, purple, pink, black, pink ],
            [pink, black, purple, black,  black,  pink, black, pink ],
            [pink, pink,  purple, purple, purple, pink, pink,  black],
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

if __name__ == '__main__':
    import u64led
    u64led.set_matrix(psu_text + psu_on)