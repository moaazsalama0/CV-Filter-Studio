import cv2
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO


def plot_histogram(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    histogram = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
    plt.figure(figsize=(10, 5))
    plt.title("Grayscale Histogram")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.plot(histogram, color='black')
    plt.xlim([0, 256])
    plt.grid()
    plt.show(block=False)


def plot_color_histogram(image):
    channels = cv2.split(image)
    colors = ('b', 'g', 'r')
    plt.figure(figsize=(10, 5))
    plt.title("Color Histogram")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    for channel, color in zip(channels, colors):
        histogram = cv2.calcHist([channel], [0], None, [256], [0, 256])
        plt.plot(histogram, color=color)
        plt.xlim([0, 256])
    plt.grid()
    plt.show(block=False)


def compute_histogram_data(img: np.ndarray, color: bool = False):
    """
    Return histogram data as a dict.
    For grayscale: {"hist": [...], "bins": [...]}
    For color (if color=True): {"b": [...], "g": [...], "r": [...]}
    """
    if color and (img.ndim == 3 and img.shape[2] >= 3):
        # BGR -> split channels
        channels = cv2.split(img)  # [b, g, r]
        data = {}
        for i, ch_name in enumerate(['b', 'g', 'r']):
            hist = cv2.calcHist([channels[i]], [0], None, [256], [0, 256])
            data[ch_name] = hist.flatten().tolist()
        return data
    else:
        # Grayscale
        gray = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        return {"hist": hist.flatten().tolist(), "bins": list(range(256))}


def render_histogram_png(img: np.ndarray, color: bool = False) -> bytes:
    """Render histogram as a PNG image and return the bytes."""
    plt.figure(figsize=(8, 4))
    if color and (img.ndim == 3 and img.shape[2] >= 3):
        channels = cv2.split(img)
        colors = ('b', 'g', 'r')
        for channel, col in zip(channels, colors):
            hist = cv2.calcHist([channel], [0], None, [256], [0, 256])
            plt.plot(hist, color=col, label=col.upper())
        plt.legend()
    else:
        gray = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        plt.plot(hist, color='black')

    plt.title("Histogram")
    plt.xlabel("Pixel intensity")
    plt.ylabel("Frequency")
    plt.xlim([0, 256])
    plt.grid(True, alpha=0.3)
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return buf.getvalue()