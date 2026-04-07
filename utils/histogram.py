import cv2 # type: ignore
import matplotlib.pyplot as plt 

def plot_histogram(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Calculate the histogram
    histogram = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
    
    # Plot the histogram
    plt.figure(figsize=(10, 5))
    plt.title("Grayscale Histogram")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.plot(histogram, color='black')
    plt.xlim([0, 256])
    plt.grid()
    plt.show()

def plot_color_histogram(image):
    # Split the image into its color channels
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
    plt.show()      