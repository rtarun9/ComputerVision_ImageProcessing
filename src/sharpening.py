import cv2
import numpy as np

# As smoothing is achieved by smoothing in the neighbourhood, we can say that sharpening is done by
# spatial differentiation, where the strenght of the derivative operation is directly proportional to the magnitude of 
# intensity discontinuity at that point.
# Areas of edges (areas of high varying intensities) are emphasized while de emphasizes areas of slow varying intensities.

image = cv2.imread('data/car_camera_test.jpg')

cv2.imshow('org image', image)

# Image with padding for convineince (for use with a 3X3 filter).
padded_image = image.copy()

print(padded_image.shape)
padded_image = cv2.copyMakeBorder(padded_image, 2, 2, 2, 2, cv2.BORDER_CONSTANT, None, 0)
img_width, img_height = padded_image.shape[0:2]

# Sharpening using second derivative (i.e Laplacian), non rotated no diagonal consideration.
# partial_derivative_on_x = f(x + 1, y) - f(x, y)
# partial_derivative_on_x_2 = f(x + 1, y) + f(x - 1, y) - 2f(x, y)
 
# partial_derivative_on_y = f(x, y + 1) - f(x, y)
# partial_derivative_on_y_2 = f(x, y + 1) + f(x, y - 1) - 2f(x, y)

# combining, laplacian = f(x + 1, y) + f(x - 1, y) + f(x, y + 1) + f(x, y -1) - 4f(x, y)
# For convinience, as the center coeff is -ve, negating the full filter so it can be added directly with base / original image.

# in filter form, we have for n4 : 
laplacian_filter_4 = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
laplacian_filtered_image_4 = cv2.filter2D(image, -1, laplacian_filter_4)
print(laplacian_filtered_image_4.shape)
cv2.imshow('custom laplacian image (n4)', laplacian_filtered_image_4)
 
sharpened_image = cv2.addWeighted(image, 1, laplacian_filtered_image_4, 2, gamma=0)
cv2.imshow('custom sharpened image (using laplacian)', sharpened_image)

# Performing laplacian considering all 8 neighbours
laplacian_filter_8 = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
laplacian_filtered_image_8 = cv2.filter2D(image, -1, laplacian_filter_8)
print(laplacian_filtered_image_8.shape)
cv2.imshow('custom laplacian image (n8)', laplacian_filtered_image_8)
 
sharpened_image_8 = cv2.addWeighted(image, 1, laplacian_filtered_image_8, 2, gamma=0)
cv2.imshow('n8 custom sharpened image (using laplacian)', sharpened_image_8)

laplacian_sharpened_cv = cv2.Laplacian(image, ddepth=-1)
cv2.imshow('cv laplacian image', laplacian_sharpened_cv)

# Unsharp masking method for sharpening (primarily used by publishing industry.)
# denoise image first as laplacian will amplify the noise
blurred = cv2.medianBlur(image, 3)
mask = cv2.addWeighted(image, 1, blurred, -1, gamma=0)


print('unsharp mask')
cv2.imshow('unsharp mask', mask)

print('unsharp masking result')
unsharp_masking_result = cv2.addWeighted(image, 1, mask, 3, gamma=0)
cv2.imshow('unsharp masking result', unsharp_masking_result)

print('org image for reference')
cv2.imshow('org image', image)

cv2.waitKey()
