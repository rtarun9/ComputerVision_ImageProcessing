import cv2
import numpy as np

image = cv2.imread('data/sculpture_image.jpg')
print(image.shape)

# Resize (scale) the image.
resized_image_linear = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_LINEAR)
resized_image_cubic = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

cv2.imshow("Org Image", image)
cv2.imshow("Linear upscaled image", resized_image_linear)
cv2.imshow("Cubix upscaled image", resized_image_cubic)

# Translation.
translation_mat = np.float32([[1, 0, 100], [0, 1, 100]])
translation_image = cv2.warpAffine(image, translation_mat, image.shape[0:2])

cv2.imshow("Translated image", translation_image)

# Rotation.
rotation_mat = cv2.getRotationMatrix2D((image.shape[0] / 2, image.shape[1] / 2), 45, 1)
rotated_image = cv2.warpAffine(image, rotation_mat, image.shape[0:2])

cv2.imshow("Rotated image", rotated_image)

cv2.waitKey()