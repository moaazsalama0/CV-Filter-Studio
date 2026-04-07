import cv2 # type: ignore

def blur(image, kernel_size=(5, 5)):
    """
    Apply a blur filter to the input image.

    Parameters:
    - image: The input image to be blurred.
    - kernel_size: A tuple specifying the size of the kernel (width, height).

    Returns:
    - The blurred image.
    """
    return cv2.blur(image, kernel_size)

def gaussian_blur(image, kernel_size=(5, 5), sigma_x=0):
    """
    Apply a Gaussian blur filter to the input image.

    Parameters:
    - image: The input image to be blurred.
    - kernel_size: A tuple specifying the size of the kernel (width, height).
    - sigma_x: The standard deviation in the X direction. If 0, it is calculated from the kernel size.

    Returns:
    - The blurred image.
    """
    return cv2.GaussianBlur(image, kernel_size, sigma_x)

def median_blur(image, kernel_size=5):
    """
    Apply a median blur filter to the input image.

    Parameters:
    - image: The input image to be blurred.
    - kernel_size: The size of the kernel (must be an odd integer).

    Returns:
    - The blurred image.
    """
    return cv2.medianBlur(image, kernel_size)

def bilateral_filter(image, diameter=9, sigma_color=75, sigma_space=75):
    """
    Apply a bilateral filter to the input image.

    Parameters:
    - image: The input image to be blurred.
    - diameter: The diameter of each pixel neighborhood.
    - sigma_color: The filter sigma in the color space. A larger value means that farther colors will be mixed together.
    - sigma_space: The filter sigma in the coordinate space. A larger value means that farther pixels will influence each other.

    Returns:
    - The blurred image.
    """
    return cv2.bilateralFilter(image, diameter, sigma_color, sigma_space)

def box_filter(image, kernel_size=(5, 5)):
    """
    Apply a box filter to the input image.

    Parameters:
    - image: The input image to be blurred.
    - kernel_size: A tuple specifying the size of the kernel (width, height).

    Returns:
    - The blurred image.
    """
    return cv2.boxFilter(image, -1, kernel_size)
