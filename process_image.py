import numpy as np
import cv2
import matplotlib.pyplot as plt

#Perform sobel edge detection and thresholding on the lane image
def threshold_image(img, sx_thresh=(25, 255)):
    #Convert image to greyscale
    rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    grey = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    #Perform Sobel edge detection on x axis of image
    sobel_x64f = cv2.Sobel(grey, cv2.CV_64F, 1, 0, ksize=5)
    abs_sobel_x64f = np.absolute(sobel_x64f)
    sobel_x8u = np.uint8(255*abs_sobel_x64f/np.max(abs_sobel_x64f))

    sobel_x_binary = np.zeros_like(sobel_x8u)
    sobel_x_binary[(sobel_x8u >= sx_thresh[0]) & (sobel_x8u <= sx_thresh[1])] = 1

    #Blur image to reduce noise
    sobel_x_binary = cv2.GaussianBlur(sobel_x_binary, (5,5), 0)

    return sobel_x_binary

def perspective_warp(img, height, width, warp_type):
    if(warp_type == "warp"):
        desired=np.float32([(0, 0),(0, 1),(1, 1),(1, 0)]), 
        src=np.float32([(0.386, 0.526), (0, 1), (1, 1), (0.616, 0.526)])
    else:
        src=np.float32([(0, 0),(0, 1),(1, 1),(1, 0)]), 
        desired=np.float32([(0.386, 0.526), (0, 1), (1, 1), (0.616, 0.526)])

    desired_size = (width, height)
    img_size = np.float32([img.shape[1], img.shape[0]])
    src = src * img_size
    desired = desired * np.float32(desired_size)
    transform_matrix = cv2.getPerspectiveTransform(src, desired)
    warped = cv2.warpPerspective(img, transform_matrix, desired_size)
    return warped

def process_image(img, height, width):
    img = threshold_image(img)
    img = perspective_warp(img, height, width, "warp")
    return img