# CV Filter Studio

CV Filter Studio is a Python-based image processing project for experimenting with classic computer vision filters through a clean web interface and a FastAPI backend. It is designed for learning, prototyping, and visually exploring operations such as blur, thresholding, edge detection, and histogram analysis.

## Overview

This project combines:
- a lightweight web front end served from the static folder,
- a FastAPI application for processing uploaded images,
- modular OpenCV-based filter implementations in the Filters package,
- reusable image utilities for histogram generation and loading.

It is a practical tool for understanding how common image processing techniques behave on real images.

## Key Features

- Blur filters including box, standard, Gaussian, median, and bilateral blur
- Thresholding methods including simple binary, adaptive, and Otsu thresholding
- Edge detection using Canny, Sobel, Laplacian, Prewitt, Scharr, and Roberts methods
- Histogram generation in JSON or PNG formats
- Image upload support and URL-based image fetching
- REST API endpoints for programmatic access
- Static web experience for quick interactive testing

## Tech Stack

- Python 3.9+
- FastAPI
- Uvicorn
- OpenCV
- NumPy
- Matplotlib
- Python multipart support

## Project Structure

```text
CV Filter Studio/
├── main.py                 # FastAPI application entry point
├── Filters/                # Image processing filter implementations
│   ├── blur.py
│   ├── edge_detection.py
│   └── threshold.py
├── static/                 # Front-end assets and HTML/JS files
├── utils/                  # Histogram and image utility helpers
├── requirements.txt        # Python dependencies
└── QUICK_START.md          # Short usage guide
```

## Prerequisites

Before installing, make sure you have:
- Python 3.9 or newer
- pip installed and available on your PATH
- a virtual environment is recommended

## Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd "CV Filter Studio"
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   On macOS or Linux, use:
   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the FastAPI server with:

```bash
uvicorn main:app --reload
```

Then open one of the following in your browser:
- http://127.0.0.1:8000/ for the landing page
- http://127.0.0.1:8000/studio.html for the processing studio

## API Overview

The app exposes several endpoints for image processing:

- GET /api/health — health check
- POST /api/blur — apply blur filters
- POST /api/threshold — apply thresholding operations
- POST /api/edge-detection — apply edge detection methods
- POST /api/histogram — generate histogram data or image output

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/blur \
  -F "image=@sample.png" \
  -F "kernel_type=gaussian" \
  -F "size=5"
```

## Usage Notes

- Upload a common image format such as PNG, JPG, JPEG, BMP, WEBP, or TIFF.
- For best results, use images that are reasonably sized and not excessively large.
- Thresholding and edge detection work best when the input is grayscale or converted appropriately by the backend.

## Development Notes

The codebase is organized to keep filter logic separate from the web-facing API layer. This makes the project easier to extend with additional filters, richer UI controls, and alternate front-end experiences.

## License

This project is provided as-is for learning and experimentation.