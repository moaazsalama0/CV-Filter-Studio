import cv2 # type: ignore
import sys

def load_image(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from path: {image_path}")
        return image
    except Exception as e:
        sys.exit(f"Error loading image: {e}")