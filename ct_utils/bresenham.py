def bresenham(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    # If starting point is also endpoint there's no line, just point.
    if start == end:
        return []

    # We want start.x to **always** be less than end.x
    if start[0] > end[0]:
        start, end = end, start

    # If line is completely horizontal
    if start[1] == end[1]:
        return [(x, start[1]) for x in range(start[0], end[0])]

    # If line is completely vertical
    if start[0] == end[0]:
        if start[1] < end[1]:
            return [(start[0], y) for y in range(start[1], end[1])]
        else:
            return [(start[0], y) for y in range(end[1], start[1])]

    # At this point we are sure that start.x < end.x
    # The only difference between normal and reversed line
    # Bresenham's algorithm is value we change `j` by.
    # If we have inversed y coordinates we have to decrease
    # `j` otherwise - increase it.
    if start[1] > end[1]:
        step = -1
        offset = -1
    else:
        step = 1
        offset = 0

    delta_x = end[0] - start[0]
    delta_y = abs(end[1] - start[1])

    j = start[1] + offset
    epsilon = delta_y - delta_x

    illuminated = []

    for i in range(start[0], end[0]):
        illuminated.append((i, j))
        if epsilon >= 0:
            j += step
            epsilon -= delta_x
        epsilon += delta_y

    return illuminated