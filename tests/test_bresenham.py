from ct_utils import bresenham


def test_bresenham_point():
    pixels = bresenham((1, 5), (1, 5))
    assert pixels == []


def test_bresenham_horizontal_line():
    pixels = bresenham((0, 5), (15, 5))
    assert pixels == [(0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5),
                      (7, 5), (8, 5), (9, 5), (10, 5), (11, 5), (12, 5),
                      (13, 5), (14, 5)]


def test_bresenham_vertical_line():
    pixels = bresenham((5, 0), (5, 15))
    assert pixels == [(5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
                      (5, 7), (5, 8), (5, 9), (5, 10), (5, 11), (5, 12),
                      (5, 13), (5, 14)]


def test_bresenham_diagonal_line():
    pixels = bresenham((0, 0), (15, 15))
    assert pixels == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6),
                      (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12),
                      (13, 13), (14, 14)]


def test_bresenham_normal_line():
    pixels = bresenham((0, 0), (9, 3))
    assert pixels == [(0, 0), (1, 0), (2, 0), (3, 1), (4, 1), (5, 1), (6, 2),
                      (7, 2), (8, 2)]


def test_bresenham_reversed_normal_line():
    pixels = bresenham((9, 3), (0, 0))
    assert pixels == [(0, 0), (1, 0), (2, 0), (3, 1), (4, 1), (5, 1), (6, 2),
                      (7, 2), (8, 2)]


def test_bresenham_inversed_line():
    pixels = bresenham((0, 4), (10, 0))
    assert pixels == [(0, 3), (1, 3), (2, 3), (3, 2), (4, 2), (5, 1), (6, 1),
                      (7, 1), (8, 0), (9, 0)]


def test_bresenham_reversed_inversed_line():
    pixels = bresenham((10, 0), (0, 4))
    assert pixels == [(0, 3), (1, 3), (2, 3), (3, 2), (4, 2), (5, 1), (6, 1),
                      (7, 1), (8, 0), (9, 0)]
