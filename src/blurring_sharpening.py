import cv2
import numpy as np

image = cv2.imread('data/car_camera_test.jpg')
cv2.imshow('Org image', image)

width, heigh = image.shape[0:2]

# Kernel blurring.
kernel = np.ones((5, 5), np.float32) / 25.0
blurred_image = cv2.filter2D(image, -1, kernel)

cv2.imshow('Blurred image', blurred_image)

# Blurring using api blur function.
blurred_image2 = cv2.blur(image, (5, 5))
cv2.imshow('Blurred image2', blurred_image2)

# Box filter blur. Can be used to increase overall intensity if no normalizing is done.
box_filtered_image = cv2.boxFilter(image, -1, (5, 5))
cv2.imshow('Box filter', box_filtered_image)

# Gaussian blur.
gaussian_blur_image = cv2.GaussianBlur(image, (5, 5), sigmaX=1, sigmaY=1)
cv2.imshow('Gaussian Blur', gaussian_blur_image)

# Median blur (useful for reduction of noise).
median_blur_image = cv2.medianBlur(image, 5)
cv2.imshow("Median blur", median_blur_image)

# Bilaterial filter (reduce noise + preserve edges).
bilateral_blur = cv2.bilateralFilter(image, 5, sigmaColor=6, sigmaSpace=6)

cv2.imshow("Bilateral image", bilateral_blur)

# Generate gaussian noise.
gauss = np.random.normal(0, 1, image.size)
gauss = gauss.reshape(image.shape).astype('uint8')
noised_image = cv2.add(image, gauss)

cv2.imshow("Noised image", noised_image)

# Denoising using median blur.
denoised_median_blur = cv2.medianBlur(noised_image, 5)
cv2.imshow("Denoised image", denoised_median_blur)

# Image sharpening -> subtracting the blur from the image. Hikes the high frequency components.
sharpened_image = cv2.addWeighted(image, 3.5, gaussian_blur_image, -2.5, 0)
cv2.imshow("Sharpened image", sharpened_image)

cv2.waitKey(0)