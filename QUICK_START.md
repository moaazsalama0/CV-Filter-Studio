# Quick Start

This short guide is for getting the app running quickly.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Start the app

```bash
uvicorn main:app --reload
```

Then open:
- http://127.0.0.1:8000/ for the landing page
- http://127.0.0.1:8000/studio.html for the image processing studio

## 3. Try a sample workflow

1. Open the studio page in your browser.
2. Upload an image.
3. Choose a filter such as blur, threshold, or edge detection.
4. Adjust parameters and inspect the result.

## 4. API usage

You can also call the processing endpoints directly:

```bash
curl -X POST http://127.0.0.1:8000/api/blur \
  -F "image=@sample.png" \
  -F "kernel_type=gaussian" \
  -F "size=5"
```

For more details, see the main README.
