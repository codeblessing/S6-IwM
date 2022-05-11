
def get_metrics(files):
    
    import cv2 as cv
    import numpy as np
    import pandas as pd
    import math
    from skimage import img_as_bool
    from matplotlib.pylab import imshow, imsave
    from skimage.filters import frangi
    from matplotlib import pyplot as plt
    from skimage.morphology import remove_small_objects, remove_small_holes
    from process_image import process_image
    from ipyregulartable import RegularTableWidget as table
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import confusion_matrix
    from sklearn.neighbors import KNeighborsClassifier
    from imblearn.under_sampling import RandomUnderSampler
    from sklearn.model_selection import train_test_split
    from prepare_image import prepare_image
    from joblib import dump, load
    from IPython.display import display
    from imblearn.metrics import sensitivity_specificity_support
    accuracies = []
    specificities = []
    sensitivities = []
    g_means = []
    w_sen = []
    w_spe = []
    for file_number in files:
        kNN_classifier = load('kNN_classifier.joblib')
        image = cv.imread('data/all/images/' + file_number + '_h.JPG')
        mask = cv.imread('data/all/manual1/' + file_number + '_h.tif')
        cut = cv.imread('data/all/mask/' + file_number + '_h_mask.tif')
        new_image_data_frame = prepare_image(image, mask, cut)
        new_X = new_image_data_frame.iloc[:, 0:7]
        image_pred = kNN_classifier.predict(new_X)
        image = cv.imread('data/all/images/' + file_number + '_h.JPG')
        mask = cv.imread('data/all/manual1/' + file_number + '_h.tif')
        cut = cv.imread('data/all/mask/' + file_number + '_h_mask.tif')
        predicted_image_to_display = image_pred.reshape((464, 697)).astype('uint8')
        cut = cv.cvtColor(cut, cv.COLOR_BGR2GRAY)
        mask = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
        cut = cv.resize(cut, (predicted_image_to_display.shape[1], predicted_image_to_display.shape[0]))
        mask = cv.resize(mask, (predicted_image_to_display.shape[1], predicted_image_to_display.shape[0]))
        inversed_image = predicted_image_to_display.copy()
        inversed_image[cut == 0] = 1
        inversed_image = cv.bitwise_not(inversed_image)
        inversed_image = (inversed_image - np.min(inversed_image)) / (np.max(inversed_image) - np.min(inversed_image))

        predicted = (inversed_image == 1.0)
        truth = (mask == 255)
        true_positive = (predicted & truth)

        yellow_mask = np.zeros((*cut.shape, 3))
        yellow_mask[truth, :] = 255
        yellow_mask[true_positive] = [127, 127, 0]

        inversed_image = img_as_bool(inversed_image)
        mask = img_as_bool(mask)
        TN, FP, FN, TP = confusion_matrix(mask.flatten(), inversed_image.flatten()).ravel()
        x = sensitivity_specificity_support(mask.flatten(), inversed_image.flatten(), average='weighted')
        w_sen.append(x[0])
        w_spe.append(x[1])
        accuracy = (TP + TN) / (TP + FP + FN + TN)
        sensitivity = TP / (TP + FN)
        specificity = TN / (TN + FP)
        geometric_mean = math.sqrt(specificity * sensitivity)
        accuracies.append(accuracy)
        sensitivities.append(sensitivity)
        specificities.append(specificity)
        g_means.append(geometric_mean)

    data = [files, accuracies, sensitivities, specificities, g_means, w_sen, w_spe]
    data_frame = pd.DataFrame(data, index=['file no.', 'accuracy', 'sensitivity', 'specificity', 'G-mean', 'w_sensitivity', 'w_specificity']).transpose()
    data_frame.to_csv('machine_learning.csv')
    return data_frame

