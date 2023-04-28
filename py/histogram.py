import matplotlib.pyplot as plt
import cv2
import numpy as np
from pathlib import Path
import os 

def plot_histogram(image):
    # plt.hist(image.ravel(), bins=256, range=(0, 255), fc='k', ec='k')
    plt.show()
    print(image.max())
    vals = [0] * 256
    for i in range(image.shape[0]-3):
        for j in range(image.shape[1]-3):
            if image[i][j] > 255 or image[i][j] < 0:
                continue
            vals[image[i][j]] = vals[image[i][j]] + 1

    # plot histogram with 255 bins
    plt.plot(vals)
    plt.show()

    return vals

test_image = cv2.imread('../data/sculpture_image.jpg')
test_image = cv2.cvtColor(test_image, cv2.COLOR_RGB2GRAY)

print(test_image.shape)

cv2.imshow('source image', test_image)
hist = plot_histogram(test_image)

print("R = ", 1 - (1 / (1 + np.var(hist))))
temp = []
for i in range(len(hist)):
    if hist[i]  != 0:
        temp.append(hist[i])

print('R without bg = ', 1 - (1 / (1 + np.var(temp))))