import matplotlib.pyplot as plt
import cv2
import numpy as np
from pathlib import Path
import os   

# Chain code (n8)
def get_start_point(image):
    start_point = [0, 0]
    for j in range(image.shape[1]):
      for i in range(image.shape[0]):
        if (image[i][j] == 255):
          start_point[0] = i
          start_point[1] = j
          return start_point
        
def to_chr(x):
  if x == 0:
    return '0'
  elif x == 1:
    return '1'
  elif x == 2:
    return '2'
  elif x == 3:
    return '3'
  elif x == 4:
    return '4'
  elif x == 5:
    return '5'
  elif x == 6:
    return '6'
  elif x == 7:
    return '7'

def is_in_range(image, point):
    if point[0] >= 0 and point[0] < image.shape[0] and point[1] >= 0 and point[1] < image.shape[1]:
      return True
    return False

def chain_code_difference(a, b):
    if a == '0' and b == '7':
      return 7
    elif a == '7' and b == '0':
      return 1
    elif a == b:
      return 0
    else:
      if a >= b:
        return int(a) - int(b)
      else:
        return int(b) - int(a)
    
def chain_code_8n(image, start_point):
  s = ""
  visited = list()

  prev_point = [-1, -1]
  curr_point = start_point
  
  while curr_point in visited and prev_point[0] != curr_point[0] or prev_point[1] != curr_point[1]:
    prev_point = curr_point

    if (is_in_range(image, [prev_point[0]+1, prev_point[1]]) and image[curr_point[0]+1][curr_point[1]] == 255 and not [prev_point[0]+1, prev_point[1]] in visited):
      curr_point = [curr_point[0]+1, curr_point[1]]
      s += '0'
      
    elif (is_in_range(image,  [prev_point[0]+1, prev_point[1]+1]) and image[curr_point[0]+1][curr_point[1]+1] == 255 and not [prev_point[0]+1, prev_point[1]+1] in visited):
      curr_point = [curr_point[0]+1, curr_point[1]+1]
      s += '7'

    elif (is_in_range(image,  [prev_point[0], prev_point[1]+1]) and image[curr_point[0]][curr_point[1]+1] == 255 and not [prev_point[0], prev_point[1]+1] in visited):
      curr_point = [curr_point[0], curr_point[1]+1]
      s += '6'

    elif (is_in_range(image,  [prev_point[0]-1, prev_point[1]+1]) and image[curr_point[0]-1][curr_point[1]+1] == 255 and not [prev_point[0]-1, prev_point[1]+1] in visited):
      curr_point = [curr_point[0]-1, curr_point[1]+1]
      s += '5'

    elif (is_in_range(image,  [prev_point[0]-1, prev_point[1]]) and image[curr_point[0]-1][curr_point[1]] == 255 and not [prev_point[0]-1, prev_point[1]] in visited):
      curr_point = [curr_point[0]-1, curr_point[1]]
      s += '4'
      
    elif (is_in_range(image,  [prev_point[0]-1, prev_point[1]-1]) and image[curr_point[0]-1][curr_point[1]-1] == 255 and not [prev_point[0]-1, prev_point[1]-1] in visited):
      curr_point = [curr_point[0]-1, curr_point[1]-1]
      s += '3'

    elif (is_in_range(image,  [prev_point[0], prev_point[1]-1]) and image[curr_point[0]][curr_point[1]-1] == 255 and not [prev_point[0], prev_point[1]-1] in visited):
      curr_point = [curr_point[0], curr_point[1]-1]
      s += '2'

    elif (is_in_range(image,  [prev_point[0]+1, prev_point[1]-1]) and image[curr_point[0]+1][curr_point[1]-1] == 255 and not [prev_point[0]+1, prev_point[1]-1] in visited):
      curr_point = [curr_point[0]+1, curr_point[1]-1]
      s += '1'

    visited.append(curr_point)

  # Difference of chain code.
  diff = to_chr(chain_code_difference(s[len(s) - 1], s[0]))
  for x in range(len(s)-1):
    diff += to_chr(chain_code_difference(s[x],s[x+1]))
  return s, diff

def calculate_signature(mask, single_contour=False):
  _c = []
  if single_contour:
    _c =  cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  else:
    _c, _ =  cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  for c in _c:
    m = cv2.moments(c)
 
    c_x = int(m["m10"] / m["m00"])
    c_y = int(m["m01"] / m["m00"])

    print('centroid')
    plt.imshow(cv2.circle(mask, (c_x, c_y), 5, (0, 0, 0), -1))
    plt.show()

    print(c_x, c_y)
    # Convert all points to a array sorted in anticlockwise order using polar coordinates.
    angles_with_dist = []
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            if (mask[i][j] == 255):
                cartesian_coords = [i, j]
                dist_to_center = np.sqrt((c_x - j) * (c_x - j) + (c_y - i) * (c_y - i))
                _x = j - c_x
                _y = i - c_y

                angle = np.arctan2([_y], [_x]) * 180 / np.pi
                if angle < 0:
                    angle += 360

                angles_with_dist.append((angle, dist_to_center))
                angles_with_dist.sort(key=lambda x: x[0])

    angles = []
    dists = []

    for ad in angles_with_dist:
        angles.append((ad[1]))
        dists.append(ad[0])

    plt.plot(dists, angles)
    plt.show()


test_image = cv2.imread('../data/boundary_images/boundaryimage_1_2018-10-31-06-55-01_2018-10-31-07-00-50-232.jpg')
test_image = cv2.cvtColor(test_image, cv2.COLOR_RGB2GRAY)
_, test_image = cv2.threshold(test_image, 250, 255, cv2.THRESH_BINARY)

cv2.imshow('test image', test_image)

chain_code, diff = chain_code_8n(test_image, get_start_point(test_image))

print('chain code: ', chain_code)
print('diff: ', diff)

calculate_signature(test_image)

cv2.waitKey()