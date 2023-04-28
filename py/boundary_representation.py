import matplotlib.pyplot as plt
import cv2
import numpy as np
from pathlib import Path
import os 

def manhattan_distance(p1, p2):
    return np.abs(p1[0] - p2[0]) + np.abs(p1[1] - p2[1])

images = []
test_image = cv2.imread('../data/boundary_images/boundaryimage_1_2018-10-31-06-55-01_2018-10-31-07-00-50-232.jpg')
test_image = cv2.cvtColor(test_image, cv2.COLOR_RGB2GRAY)
_, test_image = cv2.threshold(test_image, 250, 255, cv2.THRESH_BINARY)

images.append(test_image)

for image in images:
    points = []
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i][j] == 255:
                points.append([i, j])

    # Iterate through all points in (bubble search pattern) and get the
    # maximum distance.
    # Using distance as |x1 - x2| + |y1 - y2| (i.e manhattan distance)
    diam = 0
    for i in range(len(points)):
        for j in range(len(points)):
            diam = max(diam, manhattan_distance(points[i], points[j]))
    print("Source image")
    plt.imshow(image, cmap='gray')
    plt.show()
    print("Dimameter is : ", diam)


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

for image in images:
  chain_code, diff = chain_code_8n(image, get_start_point(image))
  plt.imshow(image, cmap='gray')
  plt.show()
  print('Chain code')
  print(chain_code)
  print('Shape number')
  print(len(chain_code))
  print('Difference')
  print(diff)

  # Bounding energy.
  # Diff chain code difference with respect to 0.
  be = []
  for d in diff:
    if int(d) <= 3:
      be.append(int(d))
    else:
      be.append(0 - int(d))
  print("Bounding energies", be)
  plt.title("Bounding Energy (a) : Chain code diff vs Diff w.r.t 0")
  plt.xlabel("Chain code diff")
  plt.ylabel("Diff w.r.t. 0")
  plt.plot(be)
  plt.legend()
  plt.show()

  print("Square of be")
  be = np.square(np.array(be))
  print('Average bounding energy : ', np.mean(be))
  plt.title("Bounding Energy (b) : Chain code diff vs Diff w.r.t 0")
  plt.xlabel("Chain code diff")
  plt.ylabel("Diff w.r.t. 0")
  plt.plot(be)
  plt.legend()
  plt.show()


  print("Bound energy", np.average(be))