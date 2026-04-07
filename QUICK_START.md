# 🚀 QUICK START GUIDE

## Installation & First Run

### Step 1: Install Dependencies
```bash
pip install opencv-python pillow matplotlib
```

### Step 2: Run the Application
```bash
python main.py
```

## ⚡ 30-Second Tutorial

### First Time Use:
1. **Load an Image** → Click "📁 Browse Image" → Select any JPG/PNG file
2. **Pick a Filter** → Select "Blur" → Choose "Gaussian Blur"
3. **Adjust Parameters** → Move the slider → See preview update instantly
4. **View Kernel** → Check "Show Kernel Matrix" → See mathematical details
5. **Play Animation** → Click "🎯 Play Animation" → Watch smooth transition
6. **Save** → Click "💾 Save Image" → Choose location

---

## 🎯 Key Features Explained

### **Real-Time Preview**
Changes apply instantly as you adjust sliders - no "Apply" button needed!

### **Kernel Display**
Shows the mathematical matrix (kernel) used internally by each filter.

Example kernel for 5x5 Gaussian Blur:
```
0.04  0.04  0.04  0.04  0.04
0.04  0.04  0.04  0.04  0.04
0.04  0.04  0.04  0.04  0.04
0.04  0.04  0.04  0.04  0.04
0.04  0.04  0.04  0.04  0.04
```

### **Animation Mode**
Smoothly blends original image → filtered result over 10 frames.
Great for visualizing the effect of each filter!

---

## 🎨 Filter Quick Reference

| Filter | Best For | Result |
|--------|----------|--------|
| Gaussian Blur | Smooth, professional blur | Soft focus |
| Median Blur | Remove noise while keeping edges | Cleaner image |
| Canny Edge | Detect object boundaries | Black lines on white |
| Sobel Edge | Detect edges with direction | Oriented edges |
| Threshold | Convert to pure black/white | High contrast |
| Adaptive Threshold | Works with uneven lighting | Local contrast |

---

## 💻 System Requirements

- **Python:** 3.7 or higher
- **Display:** 1400x900 minimum recommended
- **RAM:** 4GB minimum
- **Storage:** ~50MB for Python packages

---

## 🆘 Common Issues & Solutions

**Problem:** "Image not loading"
- **Solution:** Ensure file is JPG, PNG, BMP, or TIFF format

**Problem:** Filter changes don't show
- **Solution:** Make sure you selected a filter from the dropdown

**Problem:** Application freezes during animation
- **Solution:** Try with a smaller image size (under 2000x2000 pixels)

**Problem:** Kernel display is empty
- **Solution:** Check the "Show Kernel Matrix" checkbox

---

## 🎮 Recommended Workflows

### **Professional Photo Editing**
1. Load photo → Apply Gaussian Blur (kernel 7) → Save

### **Document Scanning**
1. Load document image → Apply Adaptive Threshold → Otsu Threshold → Save

### **Object Detection Preview**
1. Load image → Try different Edge Detections → Pick best one → Save

### **Image Analysis**
1. Load image → Click "📈 Show Histogram" → Analyze distribution

---

## 📱 UI Layout

```
┌─────────────────────────────┬────────────────────────┐
│   CONTROLS (Left)           │  PREVIEW (Right)       │
│                             │                        │
│ 📁 Load Image              │  ┌─────────────┬──────┐│
│ 🎯 Category Selection       │  │  Original   │Filtered
│ ✨ Filter Selection         │  │   Image     │Image  │
│ ⚙️ Parameters (Sliders)     │  └─────────────┴──────┘│
│ 🔢 Kernel Display           │                        │
│ 🎬 Animation Controls       │  Status: Ready...      │
│ 📊 Histogram & Save         │                        │
└─────────────────────────────┴────────────────────────┘
```

---

## 🔑 Keyboard Hints

While using the app:
- **Ctrl+O**: Load image (click Browse button)
- **Ctrl+S**: Save image (click Save button)
- **ESC**: Stop animation (click Stop button)

---

## 📈 Parameter Ranges

**Kernel Size**: 3-21 (odd numbers only, controls effect strength)
**Threshold Value**: 0-255 (pixel intensity cutoff)
**Sigma**: 0-100 (blur smoothness)
**Block Size**: 3-31 (adaptive threshold neighborhood)

Smaller = More detail, Larger = Stronger effect

---

## 🎓 Learning Path

1. **Start with:** Gaussian Blur (easiest to understand)
2. **Then try:** Edge Detection filters (visual impact)
3. **Then explore:** Threshold variations (understand parameters)
4. **Finally:** Mix filters and parameters to create effects

---

**Need help? Check README.md for detailed documentation!**
