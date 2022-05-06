import numpy as np
import cv2 as cv
from matplotlib.pylab import imshow
from skimage.filters import frangi, sato
from skimage.util import img_as_bool
from matplotlib import pyplot as plt
from skimage.morphology import binary_erosion, remove_small_objects, remove_small_holes
def process_image(image: np.ndarray, manual: np.ndarray, mask: np.ndarray):
    

    image_lab = cv.cvtColor(image, cv.COLOR_BGR2LAB)
    l, a, b = cv.split(image_lab)
    clahe = cv.createCLAHE(clipLimit=3.0)
    merged = cv.merge((clahe.apply(l), a, b))
    merged = cv.cvtColor(merged, cv.COLOR_LAB2BGR)
    b, g, r = cv.split(merged)
    image_frangi = frangi(g)
    ret, thresh = cv.threshold(image_frangi, np.mean(
        image_frangi)*0.45, 255, cv.THRESH_BINARY)
    thresh = thresh.astype('uint8')
    deblobed = thresh > 0
    deblobed = remove_small_objects(deblobed, 2500, connectivity=2)
    deblobed = remove_small_holes(deblobed, 900, connectivity=1)
    deblobed = deblobed.astype('uint8')*255
    # (6,6) gives ca 96-98% accuracy and specificity
    deblobed = cv.erode(
        deblobed, cv.getStructuringElement(cv.MORPH_ELLIPSE, (1, 1)))
    deblobed = cv.morphologyEx(deblobed, cv.MORPH_CLOSE,
                               cv.getStructuringElement(cv.MORPH_ELLIPSE, (12, 12)))
    cut = cv.bitwise_and(mask, deblobed)
    processed = cut
    image_size = processed.shape[0]*processed.shape[1]
    mask_binary = manual.copy()
    mask_binary[mask_binary < 127] = 0
    mask_binary[mask_binary >= 127] = 1

    processed_binary = processed.copy()
    processed_binary[processed_binary < 127] = 0
    processed_binary[processed_binary >= 127] = 1
    TP = np.sum(processed_binary[mask_binary == 1])
    FP = np.sum(processed_binary[mask_binary == 0])
    FN = np.sum(mask_binary[mask_binary == 1]) - \
        np.sum(processed_binary[mask_binary == 1])
    TN = image_size - np.sum(processed_binary[mask_binary == 0]) - TP - FN

    return TN, FP, FN, TP