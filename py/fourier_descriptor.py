from pyefd import elliptic_fourier_descriptors
import cv2
import numpy as np
from pyefd import plot_efd

test_image = cv2.imread('../data/sculpture_image.jpg')
test_image = cv2.cvtColor(test_image, cv2.COLOR_RGB2GRAY)

contour, _ = cv2.findContours(test_image, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)

fd = elliptic_fourier_descriptors(np.squeeze(contour))

plot_efd(fd)

cv2.imshow('source image', test_image)
cv2.waitKey()