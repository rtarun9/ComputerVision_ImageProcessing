import cv2
import numpy as np

image = cv2.imread('data/sculpture_image.jpg')
print(image.shape)

cv2.imshow("Org image", image)

# Averaging (blurring) filter.
averaging_kernel = np.ones((3, 3), np.float32)
averaging_kernel *= 1/9

avg_blurred_image = cv2.filter2D(image, ddepth=-1, kernel=averaging_kernel)
cv2.imshow("Avg blurred image", avg_blurred_image)

averaging_kernel = np.ones((15, 15), np.float32)
averaging_kernel *= 1/(15**2)

avg_blurred_image = cv2.filter2D(image, ddepth=-1, kernel=averaging_kernel)
cv2.imshow("Avg blurred image k15", avg_blurred_image)

# Motion blur (horizontal dir for example)
motion_blur_kernel = np.zeros((25, 25))
motion_blur_kernel[:,int((25-1)/2)] = np.ones(25)
motion_blur_kernel = motion_blur_kernel/25

motion_blurred_image = cv2.filter2D(image, -1, motion_blur_kernel)
cv2.imshow("Motion blur image", motion_blurred_image)

cv2.waitKey()