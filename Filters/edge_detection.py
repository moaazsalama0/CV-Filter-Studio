import cv2 # type: ignore

def canny_edge_detection(image, low_threshold=100, high_threshold=200):
    return cv2.Canny(image, low_threshold, high_threshold)

def sobel_edge_detection(image, dx=1, dy=0, kernel_size=3):
    return cv2.Sobel(image, cv2.CV_64F, dx, dy, ksize=kernel_size)

def laplacian_edge_detection(image, kernel_size=3):
    return cv2.Laplacian(image, cv2.CV_64F, ksize=kernel_size)

def prewitt_edge_detection(image):
    kernel_x = cv2.getDerivKernels(1, 0, 3)[0]
    kernel_y = cv2.getDerivKernels(0, 1, 3)[0]
    edge_x = cv2.filter2D(image, cv2.CV_64F, kernel_x)
    edge_y = cv2.filter2D(image, cv2.CV_64F, kernel_y)
    return cv2.magnitude(edge_x, edge_y)

def scharr_edge_detection(image, dx=1, dy=0):   
    return cv2.Scharr(image, cv2.CV_64F, dx, dy)

def roberts_edge_detection(image):
    # Roberts X kernel
    kernel_x = cv2.getDerivKernels(1, 0, 1)[0]
    # Roberts Y kernel
    kernel_y = cv2.getDerivKernels(0, 1, 1)[0]
    
    edge_x = cv2.filter2D(image, cv2.CV_64F, kernel_x)
    edge_y = cv2.filter2D(image, cv2.CV_64F, kernel_y)
    
    return cv2.magnitude(edge_x, edge_y)