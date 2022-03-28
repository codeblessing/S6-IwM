import math
import numpy as np
def rmse(image1, image2):
    return math.sqrt(np.mean((image1 - image2)**2))