import cv2
import numpy as np

left_view = cv2.imread('data/stereo/left_camera_view.jpg')
cv2.imshow('left_view', left_view)

right_view = cv2.imread('data/stereo/right_camera_view.jpg')
cv2.imshow('right_view', right_view)

left_shape = left_view.shape
right_shape = right_view.shape

print(left_shape)
# Using homogeneous coordinates to represent 2D point (x, y) as 3D point(x', y', z')
# so that to go from 3D to 2D point we must do (x' / z', y' / z')

# Translation.
# Matrix requires so that (x, y, 1) -> (x + t2, y + t1, 1) is : 
t1 = 50
t2 = 50

# Note, matrix is premultiplied (i.e lies on the left of vector, so vector is column vector here.)
# It is negated here because the (x, y) of translated image = source_image(x + t2, y + t1), so for visual appeal negating t2 and t1 (will be changed in future)
translation_matrix = np.array([[1, 0, -t2], [0, 1, -t1], [0, 0, 1]])

translated_image = left_view.copy()
for i in range(0, left_shape[0]):
    for j in range(0, left_shape[1]):
        homogeneous_coord = [i, j, 1]
        coord = translation_matrix.dot(homogeneous_coord)
        coord = coord[0:2]
        if coord[0] < 0 or coord[0] >= translated_image.shape[0] or coord[1] < 0 or coord[1] >= translated_image.shape[1]:
            translated_image[i, j, 0] = 0
            translated_image[i, j, 1] = 0
            translated_image[i, j, 2] = 0
            continue
            

        translated_image[i, j, 0] = left_view[int(coord[0]), int(coord[1]), 0]
        translated_image[i, j, 1] = left_view[int(coord[0]), int(coord[1]), 1]
        translated_image[i, j, 2] = left_view[int(coord[0]), int(coord[1]), 2]

cv2.imshow('translated image where t1 = ' + str(t1) + ', t2 = ' + str(t2), translated_image)

# Scaling
s1 = 3
s2 = 3

# Scaling matrix is required so it takes (x, y, 1) to (xs1, ys2, 1). Matrix for this is : 
scaling_matrix = np.array([[s1, 0, 0], [0, s2, 0], [0, 0, 1]]) # Column vector required.


scaled_image = left_view.copy()
scaled_image = cv2.resize(scaled_image, (int(left_shape[1] * s1), int(left_shape[0] *  s2)))
print(scaled_image.shape)

for i in range(0, left_shape[0]):
    for j in range(0, left_shape[1]):
        homogeneous_coord = [i, j, 1]
        coord = scaling_matrix.dot(homogeneous_coord)
        coord = coord[0:2]
        if coord[0] < 0 or coord[0] >= scaled_image.shape[0] or coord[1] < 0 or coord[1] >= scaled_image.shape[1]:
            scaled_image[i, j, 0] = 0
            scaled_image[i, j, 1] = 0
            scaled_image[i, j, 2] = 0
            continue
            

        scaled_image[int(coord[0]), int(coord[1]), 0] = left_view[i, j, 0]
        scaled_image[int(coord[0]), int(coord[1]), 1] = left_view[i, j, 1]
        scaled_image[int(coord[0]), int(coord[1]), 2] = left_view[i, j, 2]

cv2.imshow('scaled image where s1 = ' + str(s1) + ', s2 = ' + str(s2), scaled_image)

downscaled_image = cv2.resize(scaled_image, (left_shape[1], left_shape[0]))
cv2.imshow('downscaled image', downscaled_image)

# Rotation around z axis by theta degree CCW
theta = np.deg2rad(10)
rotation_matrix = np.array([[np.cos(theta), -np.sin(theta), 0], [np.sin(theta), np.cos(theta), 0], [0, 0, 1]])

rotated_image = left_view.copy()
for i in range(0, left_shape[0]):
    for j in range(0, left_shape[1]):
        homogeneous_coord = [i, j, 1]
        coord = rotation_matrix.dot(homogeneous_coord)
        coord = coord[0:2]
        if coord[0] < 0 or coord[0] >= left_shape[0] or coord[1] < 0 or coord[1] >= left_shape[1]:
            rotated_image[i, j, 0] = 0
            rotated_image[i, j, 1] = 0
            rotated_image[i, j, 2] = 0
            continue
            

        rotated_image[i, j, 0] = left_view[int(coord[0]), int(coord[1]), 0]
        rotated_image[i, j, 1] = left_view[int(coord[0]), int(coord[1]), 1]
        rotated_image[i, j, 2] = left_view[int(coord[0]), int(coord[1]), 2]


cv2.imshow('rotated left view angle = ' + str(theta), rotated_image)

cv2.waitKey()