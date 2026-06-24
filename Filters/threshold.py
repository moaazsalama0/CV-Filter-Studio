import cv2 # type: ignore


def _ensure_grayscale(image):
    """Convert color images to grayscale so thresholding works reliably."""
    if image.ndim == 2:
        return image
    if image.ndim == 3:
        if image.shape[2] == 1:
            return image[:, :, 0]
        if image.shape[2] == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    raise ValueError("Unsupported image format")


def threshold(image, threshold_value=127, max_value=255, threshold_type=cv2.THRESH_BINARY):
    """
    Apply a thresholding operation to the input image.

    Parameters:
    - image: The input image to be processed.
    - threshold_value: The threshold value used for the thresholding operation.
    - max_value: The maximum value to use with the THRESH_BINARY and THRESH_BINARY_INV thresholding types.
    - threshold_type: The type of thresholding to apply (e.g., cv2.THRESH_BINARY, cv2.THRESH_BINARY_INV, etc.).

    Returns:
    - The thresholded image.
    """
    gray_image = _ensure_grayscale(image)
    _, thresh_image = cv2.threshold(gray_image, threshold_value, max_value, threshold_type)
    return thresh_image


def adaptive_threshold(image, max_value=255, adaptive_method=cv2.ADAPTIVE_THRESH_MEAN_C, threshold_type=cv2.THRESH_BINARY, block_size=11, C=2):
    """
    Apply adaptive thresholding to the input image.

    Parameters:
    - image: The input image to be processed.
    - max_value: The maximum value to use with the THRESH_BINARY and THRESH_BINARY_INV thresholding types.
    - adaptive_method: The adaptive method to use (e.g., cv2.ADAPTIVE_THRESH_MEAN_C, cv2.ADAPTIVE_THRESH_GAUSSIAN_C).
    - threshold_type: The type of thresholding to apply (e.g., cv2.THRESH_BINARY, cv2.THRESH_BINARY_INV).
    - block_size: Size of a pixel neighborhood that is used to calculate a threshold value for the pixel. It must be an odd integer.
    - C: A constant subtracted from the mean or weighted mean calculated by the adaptive method.

    Returns:
    - The thresholded image.
    """
    gray_image = _ensure_grayscale(image)
    return cv2.adaptiveThreshold(gray_image, max_value, adaptive_method, threshold_type, block_size, C)


def otsu_threshold(image, max_value=255, threshold_type=cv2.THRESH_BINARY):
    """
    Apply Otsu's thresholding to the input image.

    Parameters:
    - image: The input image to be processed.
    - max_value: The maximum value to use with the THRESH_BINARY and THRESH_BINARY_INV thresholding types.
    - threshold_type: The type of thresholding to apply (e.g., cv2.THRESH_BINARY, cv2.THRESH_BINARY_INV).

    Returns:
    - The thresholded image.
    """
    gray_image = _ensure_grayscale(image)
    _, thresh_image = cv2.threshold(gray_image, 0, max_value, threshold_type + cv2.THRESH_OTSU)
    return thresh_image