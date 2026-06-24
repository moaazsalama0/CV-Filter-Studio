import cv2 # type: ignore
import numpy as np


def _to_uint8(image):
    return cv2.convertScaleAbs(image)


def canny_edge_detection(image, low_threshold=100, high_threshold=200):
    return cv2.Canny(image, low_threshold, high_threshold)


def sobel_edge_detection(image, dx=1, dy=0, kernel_size=3):
    return _to_uint8(cv2.Sobel(image, cv2.CV_64F, dx, dy, ksize=kernel_size))


def laplacian_edge_detection(image, kernel_size=3):
    return _to_uint8(cv2.Laplacian(image, cv2.CV_64F, ksize=kernel_size))


def prewitt_edge_detection(image):
    kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
    kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
    edge_x = cv2.filter2D(image, cv2.CV_32F, kernel_x)
    edge_y = cv2.filter2D(image, cv2.CV_32F, kernel_y)
    return _to_uint8(cv2.magnitude(edge_x, edge_y))


def scharr_edge_detection(image, dx=1, dy=0):
    return _to_uint8(cv2.Scharr(image, cv2.CV_64F, dx, dy))


def roberts_edge_detection(image):
    kernel_x = np.array([[1, 0], [0, -1]], dtype=np.float32)
    kernel_y = np.array([[0, 1], [-1, 0]], dtype=np.float32)

    edge_x = cv2.filter2D(image, cv2.CV_32F, kernel_x)
    edge_y = cv2.filter2D(image, cv2.CV_32F, kernel_y)

    return _to_uint8(cv2.magnitude(edge_x, edge_y))