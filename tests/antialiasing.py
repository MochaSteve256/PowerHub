def plot_aa_line(matrix, x0, y0, x1, y1):
    def plot(x, y, brightness):
        # Clamp values and set brightness on the matrix
        if 0 <= x < 8 and 0 <= y < 8:
            matrix[int(y)][int(x)] = brightness

    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0
    gradient = dy / dx if dx != 0 else 1

    # Handle first endpoint
    xend = round(x0)
    yend = y0 + gradient * (xend - x0)
    xpxl1 = xend
    ypxl1 = int(yend)
    plot(xpxl1, ypxl1, 1 - (yend % 1))
    plot(xpxl1, ypxl1 + 1, yend % 1)

    # Handle the main loop
    for x in range(xpxl1 + 1, round(x1)):
        y = y0 + gradient * (x - x0)
        plot(x, int(y), 1 - (y % 1))
        plot(x, int(y) + 1, y % 1)

    # Handle last endpoint
    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xpxl2 = xend
    ypxl2 = int(yend)
    plot(xpxl2, ypxl2, 1 - (yend % 1))
    plot(xpxl2, ypxl2 + 1, yend % 1)


if __name__ == '__main__':
    matrix = [[0 for _ in range(8)] for _ in range(8)]
    plot_aa_line(matrix, 0, 0, 7, 7)
    for row in matrix:
        print(row)
