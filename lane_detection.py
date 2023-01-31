import numpy as np
import cv2
import matplotlib.pyplot as plt

def histogram_values(img):
    hist = np.sum(img[img.shape[0]//2:,:], axis=0)
    return hist

def sliding_window(img):
    num_windows = 9
    margin = 50 #inner and outer margin for weindow
    minpix = 1 #minmimum number of pixels needed to recenter window

    out_img = np.dstack((img, img, img))*255

    #calculate histogram peaks of image halves
    histogram = histogram_values(img)
    midpoint = int(histogram.shape[0]/2)
    leftx_initial = np.argmax(histogram[:midpoint])
    rightx_initial = np.argmax(histogram[:midpoint]) + midpoint

    #set height of sliding window
    window_height = np.int(img.shape[0]/num_windows)

    #get x and y location of all non-zero pixels in the image
    nonzero = img.nonzero()
    nonzero_y = np.array(nonzero[0])
    nonzero_x = np.array(nonzero[1])

    #set current left and right peaks to initial peaks
    leftx_current = leftx_initial
    rightx_current = rightx_initial

    #empty arrays to store pixel indices of lane lines
    left_lane_indices = []
    right_lane_indices = []

    for window in range(num_windows):
        #Define borders for sliding window
        window_low_y = img.shape[0] - (window+1) * window_height
        window_high_y = img.shape[0] - window * window_height
        window_left_low_x = leftx_current - margin
        window_left_high_x = leftx_current + margin
        window_right_low_x =rightx_current - margin
        window_right_high_x =rightx_current + margin

        #Draw windows on current frame
        cv2.rectangle(out_img, (window_left_low_x, window_low_y), (window_left_high_x, window_high_y), (100, 255, 255), 3)
        cv2.rectangle(out_img, (window_right_low_x, window_low_y), (window_right_high_x, window_high_y), (100, 255, 255), 3)

        #Identify nonzero pixels in each window
        nonzero_left_indices = ((nonzero_y >= window_low_y) & (nonzero_y < window_high_y) & 
        (nonzero_x >= window_left_low_x) & (nonzero_x < window_left_high_x)).nonzero()[0]
        nonzero_right_indices = ((nonzero_y >= window_low_y) & (nonzero_y < window_high_y) & 
        (nonzero_x >= window_right_low_x) & (nonzero_x < window_right_high_x)).nonzero()[0]

        #Append nonzero pixels to lane indices lists
        left_lane_indices.append(nonzero_left_indices)
        right_lane_indices.append(nonzero_right_indices)

        #If number of pixels found > minipix then recenter window at mean position
        if len(nonzero_left_indices) > minpix:
            leftx_current = np.int(np.mean(nonzero_x[nonzero_left_indices]))
        if len(nonzero_right_indices) > minpix:
            rightx_current = np.int(np.mean(nonzero_x[nonzero_right_indices]))
        
    #Concatenate indices lists
    left_lane_indices = np.concatenate(left_lane_indices)
    right_lane_indices = np.concatenate(right_lane_indices)

    #Retrieve left and right line pixel positions
    left_x = nonzero_x[left_lane_indices]
    left_y = nonzero_y[left_lane_indices]
    right_x = nonzero_x[right_lane_indices]
    right_y = nonzero_y[right_lane_indices]







