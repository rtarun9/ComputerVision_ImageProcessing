import cv2 
import numpy as np

img = cv2.imread('data/sculpture_image.jpg', cv2.IMREAD_GRAYSCALE)
print(img.shape)

cv2.imshow("image", img)

cv2.waitKey(0)