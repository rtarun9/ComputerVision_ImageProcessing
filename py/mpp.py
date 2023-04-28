import cv2
import numpy as np

test_image = cv2.imread('../data/sculpture_image.jpg')
test_image = cv2.cvtColor(test_image, cv2.COLOR_RGB2GRAY)

_, test_image = cv2.threshold(test_image, 200, 255, cv2.THRESH_BINARY)
test_image = test_image - cv2.erode(test_image, (3,3))
cv2.imshow('source image', test_image)

contours, _ = cv2.findContours(test_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

min_perimeter = 99999999999999
min_contour = None
for c in contours:
    if  cv2.arcLength(c, True) < min_perimeter:
        min_perimeter = cv2.arcLength(c, True)
        min_contour = c

print('min perimeter: ', min_perimeter)
min_perimeter_polygon = cv2.approxPolyDP(min_contour, epsilon=0.01*min_perimeter, closed=True)


test_image = cv2.drawContours(test_image, [min_perimeter_polygon], -1, (0, 255, 0), 3)

cv2.imshow('MPP', test_image)
cv2.waitKey(0)