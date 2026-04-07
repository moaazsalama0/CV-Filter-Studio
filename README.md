# ◈ CV Filter Studio

**CV Filter Studio** is a high-performance, interactive desktop application designed for real-time classical Computer Vision experimentation. Built with a modular architecture, it allows users to apply, tune and visualize the mathematical foundations of image processing—from Gaussian smoothing to Canny edge detection. All within a modern and dark-themed interface.

---

## 🚀 Key Features

* **Real-Time Processing Engine**: Instantaneous filter feedback using optimized OpenCV backends and Tkinter event debouncing.
* **🔢 Mathematical Kernel Visualization**: Dynamic display of the underlying convolution matrices (e.g., Sobel, Laplacian, Gaussian) to bridge the gap between code and theory.
* **🎬 Asynchronous Animations**: Threaded implementation of frame-blending transitions to visualize the "before-and-after" transformation without locking the UI.
* **📊 Statistical Analysis**: Integrated grayscale histogram generation using Matplotlib to analyze pixel intensity distributions and contrast.
* **⚙️ Granular Parameter Control**: Precision tuning of hyper-parameters (Sigma, Kernel Size, Thresholds) via custom-styled sliders.

---

## 🛠 Tech Stack

| Category | Tools |
| :--- | :--- |
| **Language** | Python 3.8+ |
| **Computer Vision** | OpenCV (`cv2`), NumPy |
| **GUI Framework** | Tkinter (Custom Themed) |
| **Imaging & Plotting** | PIL (Pillow), Matplotlib |
| **Architecture** | Multi-threaded (Threading), Modular Filter Design |

---

## 📂 Architecture

The project follows a modular design pattern, separating the UI logic from the mathematical filter implementations to ensure scalability and ease of testing.

```text
CV-Filter-Studio/
├── main.py                 # Application entry point & UI Logic
├── Filters/                # Mathematical Implementations
│   ├── blur.py             # Smoothing & Denoising algorithms
│   ├── edge_detection.py   # Gradient & Derivative operators
│   └── threshold.py        # Segmention & Binarization
└── utils/                  # Shared Utilities
    ├── image_loader.py     # IO Handling & Error Validation
    └── histogram.py        # Matplotlib integration
```

---

## 🧠 Technical Highlights

### **1. Threaded UI Management**
To ensure a smooth user experience, the **Animation Engine** runs on a secondary thread. This prevents the GUI from "freezing" during heavy computation while using `root.after()` to safely update the Tkinter canvas from the main thread.

### **2. Numerical Normalization**
For edge detection filters (Sobel, Laplacian) that often result in floating-point data types or values outside the $[0, 255]$ range, the application implements **Min-Max Normalization** to maintain visual integrity across all display canvases.

### **3. Optimized UX**
Implemented a **Debouncing Mechanism** on parameter sliders. Instead of re-calculating filters on every pixel of movement, the app waits for a brief period of inactivity (80ms) to trigger the `cv2` backend, significantly reducing CPU overhead.

---

## 🏁 Quick Start

### **Prerequisites**
* Python 3.7+
* OpenCV, NumPy, Pillow, and Matplotlib

### **Installation**
1. **Clone the repository**:
   ```bash
   git clone https://github.com/moaazsalama0/CV-Filter-Studio.git
   cd CV-Filter-Studio
   ```
2. **Install dependencies**:
   ```bash
   pip install opencv-python pillow matplotlib numpy
   ```
3. **Launch the Studio**:
   ```bash
   python main.py
   ```

---

## 📄 License
Distributed under the MIT License.

---

**Developed with ☕ by Moaaz Salama**
*AI Engineer*
