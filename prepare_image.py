import cv2 as cv
import numpy as np
from matplotlib.pylab import imshow
from skimage.filters import frangi, sato
import math
from matplotlib import pyplot as plt
from skimage.util import img_as_bool
from skimage.morphology import remove_small_objects, remove_small_holes
from process_image import process_image
from ipyregulartable import RegularTableWidget as table
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn.neighbors import NearestNeighbors, KNeighborsClassifier
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import train_test_split


def prepare_image(image: np.ndarray, mask: np.ndarray, cut: np.ndarray):

    image_lab = cv.cvtColor(image, cv.COLOR_BGR2LAB)
    l, a, b = cv.split(image_lab)
    clahe = cv.createCLAHE(clipLimit = 2.0)
    merged = cv.merge((clahe.apply(l), a, b))
    merged = cv.cvtColor(merged, cv.COLOR_LAB2RGB)
    merged = cv.cvtColor(merged, cv.COLOR_RGB2GRAY)
    tile_size = 5
    cut = cv.cvtColor(cut, cv.COLOR_BGR2GRAY)
    merged = cv.bitwise_and(merged, cut)

    merged = cv.copyMakeBorder(merged,
                               tile_size - merged.shape[0] % tile_size,
                               0,
                               tile_size - merged.shape[1] % tile_size,
                               0,
                               cv.BORDER_CONSTANT,
                               value = [0, 0, 0])

    mask = cv.copyMakeBorder(mask,
                             tile_size - mask.shape[0] % tile_size,
                             0,
                             tile_size - mask.shape[1] % tile_size,
                             0,
                             cv.BORDER_CONSTANT,
                             value = [0, 0, 0])

    merged = cv.resize(merged, (0, 0), fx = 0.2, fy = 0.2)
    mask = cv.resize(mask, (0, 0), fx = 0.2, fy = 0.2)
    strides = merged.strides * 2
    merged_shape = [merged.shape[0] - tile_size + 1, merged.shape[1] - tile_size + 1, tile_size, tile_size]
    data = np.lib.stride_tricks.as_strided(merged, shape = merged_shape, strides = strides)
    mask = np.lib.stride_tricks.as_strided(mask, shape = merged_shape, strides = strides)
    mask = data.reshape(-1, tile_size, tile_size)
    data = data.reshape(-1, tile_size, tile_size)
    r = np.zeros((data.shape[0]))

    for i in range(data.shape[0]):
        r[i] = data[i][2][2]

    r = r.reshape((464, 697))

    moments_0 = np.zeros((data.shape[0]))
    moments_1 = np.zeros((data.shape[0]))
    moments_2 = np.zeros((data.shape[0]))
    moments_3 = np.zeros((data.shape[0]))
    moments_4 = np.zeros((data.shape[0]))
    moments_5 = np.zeros((data.shape[0]))
    moments_6 = np.zeros((data.shape[0]))
    for i in range(0, data.shape[0], 10):
        m = cv.moments(data[i])
        moments_0[i] = cv.HuMoments(m)[0]
        moments_1[i] = cv.HuMoments(m)[1]
        moments_2[i] = cv.HuMoments(m)[2]
        moments_3[i] = cv.HuMoments(m)[3]
        moments_4[i] = cv.HuMoments(m)[4]
        moments_5[i] = cv.HuMoments(m)[5]
        moments_6[i] = cv.HuMoments(m)[6]
    means = np.mean(data, axis = (1, 2))
    _vars = np.var(data, axis = (1, 2))
    truth = np.zeros((mask.shape[0]), dtype = 'uint8')
    #tile_coords = np.zeros((mask.shape[0], 2))
    for i in range(mask.shape[0]):
        truth[i] = 1 if mask[i][tile_size // 2][tile_size // 2] > 127 else 0
    data = [
        means.flatten(),
        _vars.flatten(),
        moments_0.flatten(),
        moments_1.flatten(),
        moments_2.flatten(),
        moments_3.flatten(),
        moments_4.flatten(),
        truth.flatten()
    ]
    knn_data_frame = pd.DataFrame(
        data, index = ['mean', 'var', 'moment 0', 'moment 1', 'moment 2', 'moment 3', 'moment 4', 'truth']).transpose()

    return knn_data_frame