# Tarun Ramaswamy
# CB.EN.U4CSE20666

# Changes made in code:
# ValueError (relating the line  u=np.array([heading,distance[0]])) has been fixed.
# The issue was that heading and distance BOTH are expected to be float64's, but in all interations (except the first),
# np.arctan2 tends to return a array. Also, distance also tends to return a array (because of np.linalg.norm).
# I have added this code to fix the error:
#    if type(heading) != int: (In first iteration, type(heading) is always int)
#        heading = heading[0]
        
#    print("Heading :: ", heading, " ", type(heading))
# Manual euclidean distance calculation
# distance=np.sqrt(pow(previous_x - new_x, 2) + pow(previous_y-new_y, 2))   


# -*- coding: utf-8 -*-

"""
Created on Tue Apr 11 17:05:56 2023 
PARTICLE FILTERS FOR TRACKING EXPLAINED
@author: K.A.Narayanankutty
"""
"""
This is a modified version of Parcticle Filter Explained With Python Code 
From Scratch, by Behnam for Beginers.
Imagine the ball to be a robot, which can find its approximate position
new_x,new_y from time to time and has a map giving places of some landmarks\
positions.Computed distances, zs becomes the observation model.
Heading distance and direction are first predicted from robot movement.
Weights are then updated using Importance sampling. From this information
resampling is done generate or delete some particles at hand.

"""
import cv2
import numpy as np 
import scipy.stats 
from numpy.random import uniform   
global center     # This is the current position of the object [new_x,new_y]
global previous_x # These are coordinates of previous position 
global previous_y
global zs
 
centers=[]
# This creates first level particles
def generate_uniform_points(x_range, y_range, N):
    points = np.empty((N,2))
    points[:, 0] = uniform(x_range[0], x_range[1], size=N)   
    points[:, 1] = uniform(y_range[0], y_range[1], size=N)  
    return points

def predict(points, u, std, dt=1.):
    N = len(points)
    dist = (u[1] * dt) + (np.random.randn(N) * std[1])
    points[:, 0] += np.cos(u[0]) * dist
    points[:, 1] += np.sin(u[0]) * dist
    return points
      
def update(points, weights, z, R, landmarks):
    #weights.fill(1.)
    weights=1. #(1/N)*np.ones((N))
    for i, landmark in enumerate(landmarks):
        distance=np.power((points[:,0] - landmark[0])**2 +(points[:,1] - landmark[1])**2,0.5)
        # find the area between values of mean = distance; standard deviation = R; 
        # the probability of distance between [z[i]]
        weights *= scipy.stats.norm(distance, R).pdf(z[i]) # 100 weights, *= allow tuples # IMPORTANT LINE : USING IMPORTANCE SAMPLING (Montecarlo integration)
        # Samples are drawn from distribution
    weights += 1.e-200 # To avoid round-off to zero
    weights /= sum(weights)
    return weights

# This generates indexes for resampling
def systematic_resample(weights):
     N = len(weights)
     positions = (np.arange(N) + np.random.random()) / N # Allocates N positions
     indexes = np.zeros(N,'i')
     cumulative_sum = np.cumsum(weights)
     i, j = 0, 0
     while i < N and j<N:
         if positions[i] < cumulative_sum[j]:
             indexes[i] = j
             i += 1
         else:
             j += 1       
     return indexes
# Resamples weights are now alocated to indexes
def resample_from_index(points, weights, indexes):
    points[:] = points[indexes]
    weights[:] = weights[indexes]
    weights /= np.sum(weights)
    
# This finds the approximate centroid of the object    
def find_center(gray):
    global center
    #m,n=gray.shape
    ret,thresh = cv2.threshold(gray,100,255,0)
    M = cv2.moments(thresh)
    cx = int(M['m10']/M['m00']) # Sum of mi*xi/sum of mi
    cy=int(M['m01']/M['m00'])   # Sum of mi*yi/sum of mi
    center=[cx,cy]
    return center          
landmarks=np.array([[100,100],[100,620],[1100,100],[1100,620]]) 
# Number of landmarks 
NL=len(landmarks)  
N=200 # Number of particles 
WIDTH=1200
HEIGHT=720
WINDOW_NAME="Particle Filter"
sensor_std_err=5  
# Following are the limits of search, initially whole image   
x_range=np.array([0,1200])
y_range=np.array([0,720])
mask=np.zeros((720,1200))
# Create opencv video capture object
videoCap=cv2.VideoCapture('stereo_video.mp4')  
# Initialise ball direction and movement
heading=0   # Direction of ball (angle)
distance=0
# Initialise previous position outside the screen
previous_x=-1 
previous_y=-1
# Initialise the weights, sum of which has to be 1
weights=(1/N)*np.ones((N))
# Generate N samples spread out on the screen area
points=generate_uniform_points(x_range, y_range, N) 
# You can see this point cloud moving towards location
#ret, frame = videoCap.read()
while(True):
    # Read frame    
    ret, frame = videoCap.read()
    # Detect object
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) # Convert frame from BGR to GRAY     
    h,s,v=cv2.split(gray)
    center=find_center(s)  # Center of the object         
    #landmarks
    for landmark in landmarks:
        cv2.circle(frame,tuple(landmark),10,(0,0,255),-1) # Filled circle of RED color for landmark.         
    for point in points:
        cv2.circle(frame,tuple((int(point[0]),int(point[1]))),1,(255,255,255),-1)   # WHILE color for points.
       
    # Now Predict Update    
    zs = (np.linalg.norm(landmarks - center, axis=1) + (np.random.randn(NL) * sensor_std_err))    # Distance of landmark to cneter of object (4 distances). zs = array of 4 floats.
    new_x,new_y=center #objec[0].astype(int),objec[1].astype(int) 
    # trajectory=np.vstack((trajectory,np.array([new_x,new_y])))
    if previous_x >0:
        heading=np.arctan2(np.array([new_y-previous_y]), np.array([previous_x-new_x ]))
        if heading>0:
            heading=-(heading-np.pi)
        else:
            heading=-(np.pi+heading)  
    if type(heading) != int:
        heading = heading[0]
        
    #print("Heading :: ", heading, " ", type(heading))

    distance=np.sqrt(pow(previous_x - new_x, 2) + pow(previous_y-new_y, 2))        
    #print("Distance :: ", distance, type(distance))
    std=np.array([2,4]) # Variance of u; Heading and distance
    #np.array([np.array([1]), np.array([1, 2])], dtype=object)
    u=np.array([heading,distance])
    predict(points, u, std, dt=1.) # Given points and Distance and heading predict points
    # Find approximate distribution of distances to landmarks
    zs = (np.linalg.norm(landmarks - center, axis=1) + (np.random.randn(NL) * sensor_std_err))
    # Normal continuous random variable (distance,R) its pdf in weights update
    weights=update(points, weights, z=zs, R=50, landmarks=landmarks) # Get weights            
    indexes = systematic_resample(weights)
    weights=resample_from_index(points, weights, indexes)
    previous_x=new_x
    previous_y=new_y
    cv2.circle(frame,center, 10, (0,255, 255), 2)
    
    cv2.imshow(WINDOW_NAME, frame) 
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
videoCap.release()
cv2.destroyAllWindows()      