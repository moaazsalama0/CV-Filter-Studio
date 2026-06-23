import cv2 # type: ignore

def blur(image, kernel_size=(5, 5)):
    return cv2.blur(image, kernel_size)

def gaussian_blur(image, kernel_size=(5, 5), sigma_x=0):
    return cv2.GaussianBlur(image, kernel_size, sigma_x)

def median_blur(image, kernel_size=5):
    return cv2.medianBlur(image, kernel_size)

def bilateral_filter(image, diameter=9, sigma_color=75, sigma_space=75):
    return cv2.bilateralFilter(image, diameter, sigma_color, sigma_space)

def box_filter(image, kernel_size=(5, 5)):
    return cv2.boxFilter(image, -1, kernel_size)
