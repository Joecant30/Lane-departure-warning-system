import numpy as np
import process_image as process
import cv2

def histogram_values(img):
    hist = np.sum(img[img.shape[0]//2:,:], axis=0)
    return hist

left1, left2, left3 = [], [], []
right1, right2, right3 = [], [], []

def sliding_window(img):
    num_windows = 9
    margin = 150
    minpix = 1
    left_fit_ = np.empty(3)
    right_fit_ = np.empty(3)
    output_windows = np.dstack((img, img, img))*255

    #calculate histogram peaks of image halves
    histogram = histogram_values(img)
    midpoint = int(histogram.shape[0]/2)
    leftx_initial = np.argmax(histogram[:midpoint])
    rightx_initial = np.argmax(histogram[midpoint:]) + midpoint

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
        window_right_low_x = rightx_current - margin
        window_right_high_x = rightx_current + margin

        #Add boxes showing the sliding windows to an output image
        cv2.rectangle(output_windows,(window_left_low_x, window_low_y),(window_left_high_x, window_high_y), (100,255,255), 3) 
        cv2.rectangle(output_windows,(window_right_low_x, window_low_y),(window_right_high_x, window_high_y), (100,255,255), 3)

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

    #Find second order polynomial coefficients that fit the lines
    left_fit = np.polyfit(left_y, left_x, 2)
    right_fit = np.polyfit(right_y, right_x, 2)

    left1.append(left_fit[0])
    left2.append(left_fit[1])
    left3.append(left_fit[2])
    
    right1.append(right_fit[0])
    right2.append(right_fit[1])
    right3.append(right_fit[2])
    
    #Average out the left and right lane pixels
    left_fit_[0] = np.mean(left1[-10:])
    left_fit_[1] = np.mean(left2[-10:])
    left_fit_[2] = np.mean(left3[-10:])
    
    right_fit_[0] = np.mean(right1[-10:])
    right_fit_[1] = np.mean(right2[-10:])
    right_fit_[2] = np.mean(right3[-10:])

    #Use coefficients to generate x and y values for lines
    polyline = np.linspace(0, img.shape[0]-1, img.shape[0])
    left_fit_x = left_fit_[0]*polyline**2 + left_fit_[1]*polyline + left_fit_[2]
    right_fit_x = right_fit_[0]*polyline**2 + right_fit_[1]*polyline + right_fit_[2]

    output_windows[nonzero_y[left_lane_indices], nonzero_x[left_lane_indices]] = [255, 0, 100]
    output_windows[nonzero_y[right_lane_indices], nonzero_x[right_lane_indices]] = [0, 100, 255]

    return output_windows, (left_fit_x, right_fit_x), (left_fit_, right_fit_)

def find_curve(img, left_fit, right_fit):
    polyline = np.linspace(0, img.shape[0]-1, img.shape[0])
    y_eval = np.max(polyline)
    meters_pp_y = 25/720
    meters_pp_x = 3/1280
    
    new_left_fit = np.polyfit(polyline*meters_pp_y, left_fit*meters_pp_x, 2)
    new_right_fit = np.polyfit(polyline*meters_pp_y, right_fit*meters_pp_x, 2)
    left_curveradius = ((1 + (2*new_left_fit[0]*y_eval*meters_pp_y + new_left_fit[1])**2)**1.5) / np.absolute(2*new_left_fit[0])
    right_curveradius = ((1 + (2*new_right_fit[0]*y_eval*meters_pp_y + new_right_fit[1])**2)**1.5) / np.absolute(2*new_right_fit[0])
    
    car_position = img.shape[1]/2
    fit_left_to_img = new_left_fit[0]*img.shape[0]**2 + new_left_fit[1]*img.shape[0] + new_left_fit[2]
    fit_right_to_img = new_right_fit[0]*img.shape[0]**2 + new_right_fit[1]*img.shape[0] + new_right_fit[2]
    lane_center = (fit_left_to_img + fit_right_to_img)/2
    lane_width = fit_left_to_img + fit_right_to_img
    dist_from_center = (car_position - lane_center)*meters_pp_x / 10

    return (left_curveradius, right_curveradius, dist_from_center, lane_width)

def draw_lines(img, left, right, sensor_h, sensor_w):
    polyline = np.linspace(0, img.shape[0]-1, img.shape[0])
    bin_img = np.zeros_like(img)

    rev_left = np.array([np.transpose(np.vstack([left, polyline]))])
    rev_right = np.array([np.flipud(np.transpose(np.vstack([right, polyline])))])
    points = np.hstack((rev_left, rev_right))
    
    cv2.fillPoly(bin_img, np.int_(points), (0,255,100))
    inv_perspective = process.perspective_warp(bin_img, sensor_h, sensor_w, "")
    inv_perspective = cv2.addWeighted(img, 1, inv_perspective, 0.7, 0)

    return inv_perspective
