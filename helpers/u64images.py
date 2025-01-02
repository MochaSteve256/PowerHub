import copy

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

nothing1 = [
    [black, black, black, black, black, black, black, black]
]

nothing3 = [
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

def add_navbars_together(*args):
    """
    Overlay multiple navbars, with later navbars overwriting earlier ones where they are non-black.
    
    Args:
        *args: Lists of RGB tuples representing navbar colors.
        
    Returns:
        List of RGB tuples representing the combined navbar.
    """
    if not args:
        raise ValueError("At least one navbar must be provided.")
    
    # Ensure all navbars are the same length
    length = len(args[0])
    if not all(len(navbar) == length for navbar in args):
        raise ValueError("All navbars must have the same length.")
    
    result = list(args[0])  # Start with the first navbar
    
    for navbar in args[1:]:
        for i, color in enumerate(navbar):
            if color != [0, 0, 0]:  # Overlay non-black colors
                result[i] = color
    
    return result


def add_navbar(matrix, select, back, scroll):
    if len(matrix) < 8:
        print("matrix too small")
        return
    if select and back and scroll:
        matrix[7] = add_navbars_together(navbar_scroll, navbar_back, navbar_select)
    elif select and back:
        matrix[7] = add_navbars_together(navbar_back, navbar_select)
    elif select and scroll:
        matrix[7] = add_navbars_together(navbar_scroll, navbar_select)
    elif back and scroll:
        matrix[7] = add_navbars_together(navbar_scroll, navbar_back)
    elif select:
        matrix[7] = navbar_select[i]
    elif back:
        matrix[7] = navbar_back[i]
    elif scroll:
        matrix[7] = navbar_scroll[i]

    if len(matrix) > 8:
        print("matrix too big", matrix)
        return
    if len(matrix[7]) < 8:
        print("m7 too small", matrix[7])
        return
    if len(matrix[7]) > 8:
        print("m7 too big")
        return
    
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
purple_numbers = copy.deepcopy(numbers)
for z in range(10):
    for i in range(3):
        for j in range(6):
            if purple_numbers[z][j][i] == pink:
                purple_numbers[z][j][i] = purple

def number_to_matrix(number):
    matrix = blank
    if number < 0:
        matrix[3][0] = orange
        matrix[3][1] = orange
    for z in range(2):
        for i in range(3):
            for j in range(6):
                if z == 0:
                    matrix[j][i + 1] = numbers[int(str(number)[z])][j][i]
                else:
                    matrix[j][i + 4] = purple_numbers[int(str(number)[z])][j][i]
    
    return matrix



if __name__ == '__main__':
    import u64led
    #u64led.set_matrix(add_navbar(psu_text + psu_on, True, False, True))
    u64led.set_matrix(add_navbar(number_to_matrix(12), False, False, True))