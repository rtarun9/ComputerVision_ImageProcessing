import matplotlib.pyplot as plt
import cv2
import numpy as np
from pathlib import Path
import os 

def glcm(image, d):
  print('type : ', type(image))
  print('shape : ', image.shape)
  print('min : ', np.min(image))
  print('max : ', np.max(image))
   
  glcm_mat = np.zeros((np.max(image) + 1, np.max(image) + 1), dtype=np.uint8)

  for x in range(image.shape[1]-1):
      for y in range(image.shape[0]-1):
        if (x < image.shape[1]) and (y < image.shape[0]) and (x + d[0]) < image.shape[1] and (y + d[1]) < image.shape[0]:
              i = image[y,x]
              j = image[y + d[1],x+d[0]]
              glcm_mat[j,i] = glcm_mat[j,i] + 1

  glcm_mat = glcm_mat / np.sum(glcm_mat)

  return glcm_mat

# Features derived from the GLCM.
def get_uniformaty(glcm_matrix):
   # Sum of square of entry in matrix.
   u = 0
   for x in range(glcm_matrix.shape[1]):
      for y in range(glcm_matrix.shape[0]):
         u = u + glcm_matrix[y, x] * glcm_matrix[y, x]
   
   return u 

ds = [[1, 1], [1, 0], [0, 1], [0, 0]]

test_image = cv2.imread('../data/sculpture_image.jpg')
test_image = [cv2.cvtColor(test_image, cv2.COLOR_RGB2GRAY)]

for image in test_image:
    print('original image')
    plt.imshow(image, cmap='gray')
    plt.show()
    for d in ds:
        print("d =", d)
        glcm_mat = glcm(image, d)
        print('UNIFORMATY : ', get_uniformaty(glcm_mat / np.max(glcm_mat)))
        print('Maximum probability', np.max(glcm_mat) / np.sum(glcm_mat))
        print('glcm matrix')
        plt.imshow(glcm_mat)
        plt.show()
