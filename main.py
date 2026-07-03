"""
CV Filter Studio — API layer.
"""

from typing import Optional
import urllib.request

import os

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles

# ---------- imports from your modules ----------
from Filters import blur as blur_mod
from Filters import threshold as threshold_mod
from Filters import edge_detection as edge_mod
from utils import histogram as histogram_mod

app = FastAPI(title="CV Filter Studio")

# CORS (allow all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- helpers (unchanged) ----------
VALID_IMAGE_FORMATS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")

async def read_image(file: UploadFile) -> np.ndarray:
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty image upload")
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image (unsupported format?)")
    return img

def fetch_image_from_url(url: str) -> np.ndarray:
    try:
        req = urllib.request.urlopen(url, timeout=10)
        contents = req.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {exc}")
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image from URL")
    return img

def encode_image(img: np.ndarray, fmt: str = "png") -> bytes:
    # lstrip(".") removes leading dots. No spaces inside the quotes!
    fmt_lower = fmt.lower().lstrip(".")
    if fmt_lower == "jpg":
        fmt_lower = "jpeg"
    if fmt_lower not in ("png", "jpeg", "webp"):
        fmt_lower = "png"
        
    if fmt_lower == "jpeg" and img.ndim == 3 and img.shape[2] == 4:
        white = np.full_like(img, 255, dtype=np.uint8)
        alpha = img[:, :, 3:4] / 255.0
        img = (img[:, :, :3] * alpha + white[:, :, :3] * (1 - alpha)).astype(np.uint8)
        
    # FIX: Removed the spaces inside the f-string
    success, encoded = cv2.imencode(f".{fmt_lower}", img)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode result image")
    return encoded.tobytes()

def media_type_for(fmt: str) -> str:
    fmt_lower = fmt.lower().lstrip(".")
    if fmt_lower == "jpg":
        fmt_lower = "jpeg"
    # FIX: Removed spaces from dictionary keys and values
    return {
        "png": "image/png",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
    }.get(fmt_lower, "image/png")

def ensure_grayscale(img: np.ndarray) -> np.ndarray:
    if img.ndim == 2:
        return img
    if img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    if img.shape[2] == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if img.shape[2] == 1:
        return img[:, :, 0]
    raise HTTPException(status_code=400, detail="Unsupported image channel count")

def to_odd(value: int, minimum: int = 3) -> int:
    value = max(minimum, int(value))
    if value % 2 == 0:
        value += 1
    return value

# ---------- API endpoints (FIRST) ----------
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "cv-filter-studio"}

# Place your /api/blur, /api/threshold, /api/edge-detection, /api/histogram here.
# (They are unchanged – copy them from your previous version.)
# For brevity, I’m not repeating them here – keep them as they were.

# ---------- Static files (LAST) ----------
# Serve all files inside the 'static' folder at /static
# ========== API ROUTES ==========

@app.post("/api/blur")
async def api_blur(
    image: UploadFile = File(...),
    kernel_type: str = Form("gaussian"),
    size: int = Form(5),
    sigma_x: float = Form(1.0),
    diameter: int = Form(9),
    sigma_color: float = Form(75),
    sigma_space: float = Form(75),
    format: str = Form("png"),
):
    img = await read_image(image)
    ktype = kernel_type.strip().lower()
    size = to_odd(size, 3)

    # FIX: Median and Bilateral filters do not support 4-channel (BGRA) images.
    # Convert to 3-channel (BGR) by blending the alpha channel with a white background.
    if ktype in ("median", "bilateral") and img.ndim == 3 and img.shape[2] == 4:
        white = np.full_like(img, 255, dtype=np.uint8)
        alpha = img[:, :, 3:4] / 255.0
        img = (img[:, :, :3] * alpha + white[:, :, :3] * (1 - alpha)).astype(np.uint8)

    if ktype in ("blur", "standard", "box"):
        if ktype == "box":
            result = blur_mod.box_filter(img, (size, size))
        else:
            result = blur_mod.blur(img, (size, size))
    elif ktype == "gaussian":
        result = blur_mod.gaussian_blur(img, (size, size), float(sigma_x))
    elif ktype == "median":
        result = blur_mod.median_blur(img, size)
    elif ktype == "bilateral":
        result = blur_mod.bilateral_filter(
            img,
            diameter=int(diameter),
            sigma_color=float(sigma_color),
            sigma_space=float(sigma_space),
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown kernel_type '{kernel_type}'. "
                   "Valid: blur, gaussian, median, bilateral, box.",
        )

    return Response(content=encode_image(result, format), media_type=media_type_for(format))


@app.post("/api/threshold")
async def api_threshold(
    image: UploadFile = File(...),
    type: str = Form("binary"),
    value: float = Form(127),
    max_value: float = Form(255),
    block_size: int = Form(11),
    C: float = Form(5),
    adaptive_method: str = Form("mean"),
    invert: bool = Form(False),
    format: str = Form("png"),
):
    img = await read_image(image)
    
    # FIX: Thresholding ONLY works on single-channel grayscale images.
    img = ensure_grayscale(img) 
    
    ttype = type.strip().lower()
    thresh_flag = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    
    if ttype == "binary":
        result = threshold_mod.threshold(
            img,
            threshold_value=float(value),
            max_value=float(max_value),
            threshold_type=thresh_flag,
        )
    elif ttype == "adaptive":
        method = (
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C
            if adaptive_method.strip().lower() == "gaussian"
            else cv2.ADAPTIVE_THRESH_MEAN_C
        )
        block_size = to_odd(block_size, 3)
        result = threshold_mod.adaptive_threshold(
            img,
            max_value=float(max_value),
            adaptive_method=method,
            threshold_type=thresh_flag,
            block_size=block_size,
            C=float(C),
        )
    elif ttype == "otsu":
        result = threshold_mod.otsu_threshold(
            img,
            max_value=float(max_value),
            threshold_type=thresh_flag,
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown threshold type '{type}'. Valid: binary, adaptive, otsu.",
        )

    return Response(content=encode_image(result, format), media_type=media_type_for(format))


@app.post("/api/edge-detection")
async def api_edge_detection(
    image: UploadFile = File(...),
    method: str = Form("canny"),
    low_threshold: float = Form(50),
    high_threshold: float = Form(150),
    dx: int = Form(1),
    dy: int = Form(0),
    kernel_size: int = Form(3),
    format: str = Form("png"),
):
    img = await read_image(image)
    method_lower = method.strip().lower()
    img = ensure_grayscale(img)

    if method_lower == "canny":
        result = edge_mod.canny_edge_detection(
            img,
            low_threshold=float(low_threshold),
            high_threshold=float(high_threshold),
        )
    elif method_lower == "sobel":
        result = edge_mod.sobel_edge_detection(
            img,
            dx=int(dx),
            dy=int(dy),
            kernel_size=to_odd(kernel_size, 1),
        )
    elif method_lower == "laplacian":
        result = edge_mod.laplacian_edge_detection(
            img,
            kernel_size=to_odd(kernel_size, 1),
        )
    elif method_lower == "prewitt":
        result = edge_mod.prewitt_edge_detection(img)
    elif method_lower == "scharr":
        result = edge_mod.scharr_edge_detection(img, dx=int(dx), dy=int(dy))
    elif method_lower == "roberts":
        result = edge_mod.roberts_edge_detection(img)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown edge method '{method}'. "
                   "Valid: canny, sobel, laplacian, prewitt, scharr, roberts.",
        )

    return Response(content=encode_image(result, format), media_type=media_type_for(format))


@app.get("/api/histogram")
def api_histogram_get(
    url: Optional[str] = Query(default=None),
    format: str = Query(default="json"),
    color: bool = Query(default=False),
):
    if not url:
        return JSONResponse({
            "endpoint": "/api/histogram",
            "methods": ["GET", "POST"],
            "params": {
                "format": "json (default) | png",
                "color": "true to include per-channel BGR histograms (default false)",
                "url": "(GET only) HTTP URL of the image to analyse",
            },
            "notes": "POST the image as multipart/form-data with field `image`.",
        })
    img = fetch_image_from_url(url)
    return _histogram_response(img, format, color)


@app.post("/api/histogram")
async def api_histogram_post(
    image: UploadFile = File(...),
    format: str = Form("json"),
    color: bool = Form(False),
):
    img = await read_image(image)
    return _histogram_response(img, format, color)


def _histogram_response(img: np.ndarray, fmt: str, color: bool):
    fmt_lower = fmt.strip().lower()
    if fmt_lower == "png":
        png_bytes = histogram_mod.render_histogram_png(img, color=color)
        return Response(content=png_bytes, media_type="image/png")
    data = histogram_mod.compute_histogram_data(img, color=color)
    return JSONResponse(data)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/", response_class=FileResponse)
async def serve_index():
    return os.path.join(BASE_DIR, "static", "index.html")