from numpy import ndarray
import numpy
from .bresenham import bresenham


def radon(img: ndarray, detector_count: int,
          rotation_angles: ndarray[float]) -> ndarray:

    def cut_external(point):
        height, width = img.shape
        x, y = point
        return x >= 0 and x < width and y >= 0 and y < height

    max_size = max(*img.shape)
    space_between = max_size / detector_count
    sinogram = numpy.zeros((len(rotation_angles), detector_count + 1))

    for row, angle in enumerate(rotation_angles):
        sinogram[row][0] = angle
        _x = numpy.cos(angle) * max_size
        _y = numpy.sin(angle) * max_size
        for col in range(1, detector_count):
            _offset = (col - 1) * space_between
            pixels = list(filter(cut_external, bresenham((-_x, -_y + _offset), (_x, _y + _offset))))
            sinogram[row][col] = sum([img[y][x] for x, y in pixels])

    return sinogram