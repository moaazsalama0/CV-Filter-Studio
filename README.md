# 🎨 Photoshop Clone - Advanced Image Editor

A professional-grade image editing application with real-time filter preview, kernel visualization, and animated transformations.

## 📋 Features

### 🎯 Filter Categories

#### **Blur Filters**
- **Standard Blur**: Basic averaging blur
- **Gaussian Blur**: Smooth blur using Gaussian kernel
- **Median Blur**: Noise-reducing blur preserving edges
- **Bilateral Filter**: Edge-preserving blur
- **Box Filter**: Simple weighted averaging

#### **Edge Detection**
- **Canny Edge**: Multi-stage edge detection (best for most images)
- **Sobel**: First derivative-based edge detection
- **Laplacian**: Second derivative-based sharp edge detection
- **Prewitt**: Similar to Sobel, slightly different kernel
- **Scharr**: Optimized Sobel variant
- **Roberts**: Fast diagonal edge detection

#### **Threshold**
- **Binary Threshold**: Simple black/white conversion
- **Adaptive Threshold**: Local threshold for varying illumination
- **Otsu Threshold**: Automatic threshold calculation

### ✨ Advanced Features

- **Real-Time Preview**: See filter effects instantly with parameter adjustments
- **🔢 Kernel Display**: View the mathematical kernel matrices used by filters
- **🎬 Animated Transitions**: Smooth animation showing filter application over time
- **📊 Histogram Viewer**: Analyze image intensity distributions
- **💾 Save Filtered Images**: Export results in PNG, JPG formats
- **⚙️ Parameter Adjustment**: Use sliders to fine-tune filter parameters

## 🚀 Getting Started

### Requirements
```
- Python 3.7+
- opencv-python (cv2)
- tkinter (usually included with Python)
- pillow (PIL)
- matplotlib
- numpy
```

### Installation

1. Place all files in the project directory:
```
Photoshop Clone/
├── main.py
├── Filters/
│   ├── __init__.py
│   ├── blur.py
│   ├── edge_detection.py
│   └── threshold.py
└── utils/
    ├── __init__.py
    ├── image_loader.py
    └── histogram.py
```

2. Install dependencies:
```bash
pip install opencv-python pillow matplotlib
```

3. Run the application:
```bash
python main.py
```

## 📖 Usage Guide

### 1. **Loading an Image**
   - Click "📁 Browse Image" button
   - Select an image file (JPG, PNG, BMP, TIFF)
   - Image appears in the "Original" panel

### 2. **Selecting a Filter**
   - Choose filter category from radio buttons (Blur, Edge Detection, Threshold)
   - Select specific filter from dropdown
   - Filter applies instantly with real-time preview

### 3. **Adjusting Parameters**
   - Use parameter sliders to fine-tune filter settings
   - Changes apply in real-time to the preview
   - Current values shown on the right of each slider

### 4. **Viewing Kernel Information**
   - Check "Show Kernel Matrix" box
   - View the mathematical kernel used by the filter
   - Kernel display updates with parameter changes

### 5. **Animation**
   - Click "🎯 Play Animation" to see smooth filter transition
   - Animation blends original image gradually to filtered result
   - Click "⏹️ Stop Animation" to stop

### 6. **Histogram Analysis**
   - Click "📈 Show Histogram" to view pixel intensity distribution
   - Shows grayscale histogram of the image
   - Useful for analyzing image contrast

### 7. **Saving Results**
   - Click "💾 Save Image" to save filtered image
   - Choose format (PNG recommended for quality)
   - Select location and filename

## 🎮 Quick Tips

### Filter Selection Tips

**Best for photos:** Gaussian Blur, Median Blur
**Best for edge detection:** Canny Edge Detection
**Best for document scanning:** Adaptive Threshold, Otsu Threshold

### Parameter Guidelines

**Kernel Size**: 
- Smaller (3-5): Subtle effects, preserves detail
- Larger (7-21): Stronger effects, more blurring

**Threshold Values**:
- Low (0-85): Detects faint edges
- Medium (85-170): Balanced detection
- High (170-255): Only strong edges

**Sigma (Gaussian)**:
- Lower values: Less blur
- Higher values: More blur

## 🔧 Troubleshooting

### Image not loading?
- Ensure file format is supported (JPG, PNG, BMP, TIFF)
- Check file path doesn't contain special characters

### Filter applying too slow?
- Reduce image resolution
- Use simpler filters (Standard Blur vs Gaussian)

### Kernel display not updating?
- Ensure "Show Kernel Matrix" checkbox is enabled
- Try applying a different filter and returning

### Animation stuttering?
- Close other applications
- Try with a smaller image size
- Reduce animation complexity

## 📚 Technical Details

### Filter Kernel Matrices

**Blur Kernel (5x5):**
```
0.04  0.04  0.04  0.04  0.04
0.04  0.04  0.04  0.04  0.04
0.04  0.04  0.04  0.04  0.04
0.04  0.04  0.04  0.04  0.04
0.04  0.04  0.04  0.04  0.04
```

**Sobel X Edge Detection (3x3):**
```
-1    0    1
-2    0    2
-1    0    1
```

### Color Spaces
- BGR format used internally (OpenCV standard)
- RGB for display (PIL/Tkinter)
- Grayscale for filter processing

## 🎨 Keyboard Shortcuts

While image is active:
- `Ctrl+O`: Load image
- `Ctrl+S`: Save image
- `Ctrl+R`: Reset to original

## 💡 Advanced Usage

### Batch Processing
To process multiple images, write a script:
```python
from Filters.blur import gaussian_blur
from utils.image_loader import load_image
import cv2

images = ['img1.jpg', 'img2.jpg', 'img3.jpg']
for img_path in images:
    img = load_image(img_path)
    filtered = gaussian_blur(img, (7, 7))
    cv2.imwrite(f'filtered_{img_path}', filtered)
```

### Custom Filters
Add new filters in appropriate category file:
```python
def my_custom_filter(image, param1=5, param2=10):
    """Custom filter description"""
    # Implementation
    return processed_image
```

## 📄 License

This project is open source and available for educational use.

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add new filters
- Improve UI/UX
- Optimize performance
- Fix bugs

---

**Happy Image Editing! 🖼️**
