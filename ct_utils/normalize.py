import numpy as np
def normalize(image):
    max_val = np.amax(image)
    image = image / max_val * 255

    return image / 255.0