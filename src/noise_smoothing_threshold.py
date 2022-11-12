import cv2
import numpy as np

# Median filter for smoothing : used for noise removal.
# Uses median value of neighbourhood and replaces current pixel value with median of neighbourhood.
# Does not blur the edges much.
# However, thin lines and sharp corners will be affected.

noisy_image = cv2.imread('data/salt_and_pepper_noised.jpg')
noisy_image = cv2.resize(noisy_image, (300, 300), interpolation=cv2.INTER_CUBIC)

cv2.imshow('org noise image', noisy_image)

denoised_med_filter = cv2.medianBlur(noisy_image, 3)
cv2.imshow('denoised median filter cv', denoised_med_filter)

# Custom median filter implementation.
# Image with padding for convineince (for use with a 3X3 filter).
padded_image = noisy_image.copy()

print(padded_image.shape)
padded_image = cv2.copyMakeBorder(padded_image, 2, 2, 2, 2, cv2.BORDER_CONSTANT, None, 0)
img_width, img_height = padded_image.shape[0:2]
cv2.imshow('paded image', padded_image)
print(img_width, img_height)
print(padded_image.shape)

custom_median_denoised =  np.zeros((300, 300, 3), dtype = "uint8")

for i in range(1, len(noisy_image)):
    for j in range(1, len(noisy_image)):
        # Get median. Heavily affected by 0's used in padding.
        med = np.median([padded_image[i,j], padded_image[i - 1, j], padded_image[i + 1, j], padded_image[i, j + 1], 
            padded_image[i, j - 1], padded_image[i - 1, j - 1], padded_image[i + 1, j - 1], padded_image[i - 1, j + 1], 
            padded_image[i + 1, j + 1]])
        custom_median_denoised[i, j] = med

cv2.imshow('denoised median custom', custom_median_denoised)

# Box (averaging filter) : Does not preserve edges such as median filter. Used here just for demonstration.
custom_box_denoised =  np.zeros((300, 300, 3), dtype = "uint8")

for i in range(1, len(noisy_image)):
    for j in range(1, len(noisy_image)):
        s = np.average([padded_image[i,j], padded_image[i - 1, j], padded_image[i + 1, j], padded_image[i, j + 1], 
            padded_image[i, j - 1], padded_image[i - 1, j - 1], padded_image[i + 1, j - 1], padded_image[i - 1, j + 1], 
            padded_image[i + 1, j + 1]])
        custom_box_denoised[i, j] = s

cv2.imshow('denoised box custom', custom_box_denoised)

box_filtered_noise_removal = cv2.boxFilter(noisy_image, -1, (3, 3))
cv2.imshow('denoised box cv', box_filtered_noise_removal)


cv2.waitKey()
