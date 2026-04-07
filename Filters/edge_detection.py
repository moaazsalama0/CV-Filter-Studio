import cv2 # type: ignore

def canny_edge_detection(image, low_threshold=100, high_threshold=200):
    """
    Apply Canny edge detection to the input image.

    Parameters:
    - image: The input image to be processed.
    - low_threshold: The lower threshold for the hysteresis procedure.
    - high_threshold: The upper threshold for the hysteresis procedure.

    Returns:
    - The image with edges detected.
    """
    return cv2.Canny(image, low_threshold, high_threshold)

def sobel_edge_detection(image, dx=1, dy=0, kernel_size=3):
    """
    Apply Sobel edge detection to the input image.

    Parameters:
    - image: The input image to be processed.
    - dx: Order of the derivative in the x direction.
    - dy: Order of the derivative in the y direction.
    - kernel_size: Size of the extended Sobel kernel; it must be 1, 3, 5, or 7.

    Returns:
    - The image with edges detected.
    """
    return cv2.Sobel(image, cv2.CV_64F, dx, dy, ksize=kernel_size)

def laplacian_edge_detection(image, kernel_size=3):
    """
    Apply Laplacian edge detection to the input image.

    Parameters:
    - image: The input image to be processed.
    - kernel_size: Size of the extended Laplacian kernel; it must be 1, 3, 5, or 7.

    Returns:
    - The image with edges detected.
    """
    return cv2.Laplacian(image, cv2.CV_64F, ksize=kernel_size)

def prewitt_edge_detection(image):
    """
    Apply Prewitt edge detection to the input image.

    Parameters:
    - image: The input image to be processed.

    Returns:
    - The image with edges detected.
    """
    kernel_x = cv2.getDerivKernels(1, 0, 3)[0]
    kernel_y = cv2.getDerivKernels(0, 1, 3)[0]
    edge_x = cv2.filter2D(image, cv2.CV_64F, kernel_x)
    edge_y = cv2.filter2D(image, cv2.CV_64F, kernel_y)
    return cv2.magnitude(edge_x, edge_y)

def scharr_edge_detection(image, dx=1, dy=0):   
    """
    Apply Scharr edge detection to the input image.

    Parameters:
    - image: The input image to be processed.
    - dx: Order of the derivative in the x direction.
    - dy: Order of the derivative in the y direction.

    Returns:
    - The image with edges detected.
    """
    return cv2.Scharr(image, cv2.CV_64F, dx, dy)

def roberts_edge_detection(image):
    """
    Apply Roberts edge detection to the input image.

    Parameters:
    - image: The input image to be processed.

    Returns:
    - The image with edges detected.
    """
    # Roberts X kernel
    kernel_x = cv2.getDerivKernels(1, 0, 1)[0]
    # Roberts Y kernel
    kernel_y = cv2.getDerivKernels(0, 1, 1)[0]
    
    edge_x = cv2.filter2D(image, cv2.CV_64F, kernel_x)
    edge_y = cv2.filter2D(image, cv2.CV_64F, kernel_y)
    
    return cv2.magnitude(edge_x, edge_y)