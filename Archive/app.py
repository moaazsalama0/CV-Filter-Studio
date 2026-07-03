"""
CV Filter Studio — Advanced Image Processing Application
Modern dark-themed UI with real-time filter preview and kernel visualization.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
from collections import OrderedDict

# ── Filter imports ──────────────────────────────────────────────────────────
from Filters.blur import (blur, gaussian_blur, median_blur,
                          bilateral_filter, box_filter)
from Filters.edge_detection import (canny_edge_detection, sobel_edge_detection,
                                    laplacian_edge_detection, prewitt_edge_detection,
                                    scharr_edge_detection)
from Filters.threshold import (threshold, adaptive_threshold, otsu_threshold)
from utils.image_loader import load_image
from utils.histogram import plot_histogram

# ── Design tokens ────────────────────────────────────────────────────────────
PAL = {
    "bg":          "#1a1a2e",   # deep navy background
    "surface":     "#16213e",   # card / panel surface
    "surface2":    "#0f3460",   # slightly elevated surface
    "accent":      "#e94560",   # vivid coral-red accent
    "accent2":     "#533483",   # purple secondary accent
    "text":        "#eaeaea",   # primary text
    "text_dim":    "#8892a4",   # muted text
    "border":      "#1e2d4a",   # subtle border
    "success":     "#2ecc71",
    "warning":     "#f39c12",
    "slider_trough":"#0f3460",
    "slider_thumb": "#e94560",
    "button_bg":   "#e94560",
    "button_fg":   "#ffffff",
    "button_hover":"#c73652",
    "panel_title": "#e94560",
}

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_HEAD   = ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 9)
FONT_SMALL  = ("Segoe UI", 8)
FONT_MONO   = ("Consolas", 8)
FONT_CAT    = ("Segoe UI", 10, "bold")


# ── Helpers ──────────────────────────────────────────────────────────────────

def flat_button(parent, text, command, accent=True, width=None):
    """Create a styled flat button that looks modern."""
    bg   = PAL["accent"] if accent else PAL["surface2"]
    hov  = PAL["button_hover"] if accent else "#1a3a6e"
    btn  = tk.Label(parent, text=text, bg=bg, fg=PAL["button_fg"],
                    font=FONT_BODY, cursor="hand2", relief="flat",
                    padx=12, pady=6)
    if width:
        btn.config(width=width)
    btn.bind("<Button-1>", lambda e: command())
    btn.bind("<Enter>",    lambda e: btn.config(bg=hov))
    btn.bind("<Leave>",    lambda e: btn.config(bg=bg))
    return btn


def section_label(parent, text):
    """Section header with accent underline bar."""
    f = tk.Frame(parent, bg=PAL["bg"])
    tk.Label(f, text=text, bg=PAL["bg"], fg=PAL["panel_title"],
             font=FONT_CAT).pack(anchor="w")
    tk.Frame(f, bg=PAL["accent"], height=2).pack(fill="x", pady=(2, 6))
    return f


def dark_slider(parent, from_, to, command, initial=None):
    """Custom-styled horizontal slider."""
    s = tk.Scale(parent, from_=from_, to=to, orient="horizontal",
                 command=command, bg=PAL["surface"], fg=PAL["text"],
                 troughcolor=PAL["slider_trough"], activebackground=PAL["accent"],
                 highlightthickness=0, bd=0, sliderrelief="flat",
                 sliderlength=18, width=8, showvalue=False)
    if initial is not None:
        s.set(initial)
    return s


# ── Main Application ─────────────────────────────────────────────────────────

class FilterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CV Filter Studio")
        self.root.geometry("1400x820")
        self.root.configure(bg=PAL["bg"])
        self.root.resizable(True, True)

        # ── State ────────────────────────────────────────────────────────────
        self.original_image   = None
        self.filtered_image   = None
        self.animation_active = False
        self.show_kernel_var  = tk.BooleanVar(value=False)
        self.param_widgets    = {}
        self._after_id        = None

        # ── Filter registry ──────────────────────────────────────────────────
        #   BUG FIX #1: Removed "kernel_size" slider entry for filters where
        #               it isn't a separate parameter (avoids tuple-vs-int chaos).
        #   BUG FIX #2: Roberts removed (crashes due to cv2.getDerivKernels(1,0,2)).
        #   BUG FIX #4: median_blur uses "ksize" (int only) — never a tuple.
        self.filter_configs = OrderedDict([
            ("Blur", OrderedDict([
                ("Standard Blur",  (blur,            {"kw": 5})),
                ("Gaussian Blur",  (gaussian_blur,   {"kw": 5, "sigma_x": 0})),
                ("Median Blur",    (median_blur,      {"ksize": 5})),
                ("Bilateral",      (bilateral_filter, {"diameter": 9, "sigma_color": 75, "sigma_space": 75})),
                ("Box Filter",     (box_filter,       {"kw": 5})),
            ])),
            ("Edge Detection", OrderedDict([
                ("Canny Edge",  (canny_edge_detection,      {"low_threshold": 100, "high_threshold": 200})),
                ("Sobel",       (sobel_edge_detection,       {"dx": 1, "dy": 0})),
                ("Laplacian",   (laplacian_edge_detection,   {})),
                ("Prewitt",     (prewitt_edge_detection,     {})),
                ("Scharr",      (scharr_edge_detection,      {"dx": 1, "dy": 0})),
            ])),
            ("Threshold", OrderedDict([
                ("Binary",    (threshold,          {"threshold_value": 127, "max_value": 255})),
                ("Adaptive",  (adaptive_threshold,  {"max_value": 255, "block_size": 11, "C": 2})),
                ("Otsu",      (otsu_threshold,      {"max_value": 255})),
            ])),
        ])

        # Slider metadata: param_key → (min, max, step, is_odd_int)
        self.param_meta = {
            "kw":              (3, 31, 2,  True),   # kernel width (int, always odd)
            "ksize":           (3, 31, 2,  True),   # median blur int kernel
            "sigma_x":         (0, 100, 1, False),
            "sigma_color":     (10, 200, 5, False),
            "sigma_space":     (10, 200, 5, False),
            "diameter":        (3, 21, 2,  True),
            "low_threshold":   (0, 200, 5, False),
            "high_threshold":  (50, 400, 5, False),
            "dx":              (0, 1, 1,   False),
            "dy":              (0, 1, 1,   False),
            "threshold_value": (0, 255, 1, False),
            "max_value":       (100, 255, 5, False),
            "block_size":      (3, 51, 2,  True),
            "C":               (-20, 50, 1, False),
        }

        self._build_ui()
        self.set_category("Blur")

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        topbar = tk.Frame(self.root, bg=PAL["surface"], height=52)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)
        tk.Label(topbar, text="◈  CV Filter Studio",
                 bg=PAL["surface"], fg=PAL["accent"],
                 font=FONT_TITLE).pack(side="left", padx=20, pady=8)
        tk.Label(topbar, text="Classical Computer Vision · Real-Time Preview",
                 bg=PAL["surface"], fg=PAL["text_dim"],
                 font=FONT_SMALL).pack(side="left", padx=4, pady=8)

        # Body
        body = tk.Frame(self.root, bg=PAL["bg"])
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)
        self._build_preview(body)

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=PAL["surface"], width=290)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        inner = tk.Frame(sidebar, bg=PAL["surface"])
        inner.pack(fill="both", expand=True, padx=14, pady=14)

        # ── Load / Reset ─────────────────────────────────────────────────────
        section_label(inner, "Image").pack(fill="x")
        btn_row = tk.Frame(inner, bg=PAL["surface"])
        btn_row.pack(fill="x", pady=(0, 12))
        flat_button(btn_row, "📁  Load Image", self.load_image).pack(side="left")
        tk.Frame(btn_row, bg=PAL["surface"], width=6).pack(side="left")
        flat_button(btn_row, "↺  Reset", self.reset_image, accent=False).pack(side="left")

        # ── Category tabs ────────────────────────────────────────────────────
        section_label(inner, "Category").pack(fill="x")
        self.cat_var = tk.StringVar(value="Blur")
        self._cat_buttons = {}
        cat_row = tk.Frame(inner, bg=PAL["surface"])
        cat_row.pack(fill="x", pady=(0, 12))
        for cat in self.filter_configs:
            b = tk.Label(cat_row, text=cat, bg=PAL["surface2"], fg=PAL["text_dim"],
                         font=FONT_SMALL, cursor="hand2", padx=8, pady=5, relief="flat")
            b.pack(side="left", padx=(0, 4))
            b.bind("<Button-1>", lambda e, c=cat: self.set_category(c))
            self._cat_buttons[cat] = b

        # ── Filter list ──────────────────────────────────────────────────────
        section_label(inner, "Filter").pack(fill="x")
        self._filter_var = tk.StringVar()
        self._filter_listbox_frame = tk.Frame(inner, bg=PAL["surface"])
        self._filter_listbox_frame.pack(fill="x", pady=(0, 12))
        self._filter_buttons = {}

        # ── Parameters ───────────────────────────────────────────────────────
        section_label(inner, "Parameters").pack(fill="x")
        self.params_container = tk.Frame(inner, bg=PAL["surface"])
        self.params_container.pack(fill="x", pady=(0, 12))

        # ── Kernel display ───────────────────────────────────────────────────
        section_label(inner, "Kernel Matrix").pack(fill="x")
        toggle_row = tk.Frame(inner, bg=PAL["surface"])
        toggle_row.pack(fill="x", pady=(0, 4))
        self._kernel_toggle = tk.Label(toggle_row, text="○  Show kernel",
                                       bg=PAL["surface"], fg=PAL["text_dim"],
                                       font=FONT_SMALL, cursor="hand2")
        self._kernel_toggle.pack(side="left")
        self._kernel_toggle.bind("<Button-1>", self._toggle_kernel)

        self.kernel_frame = tk.Frame(inner, bg=PAL["bg"],
                                     relief="flat", bd=0)
        self.kernel_text = tk.Text(self.kernel_frame, height=7,
                                   bg=PAL["bg"], fg=PAL["text_dim"],
                                   font=FONT_MONO, relief="flat",
                                   wrap="none", state="disabled",
                                   insertbackground=PAL["accent"],
                                   selectbackground=PAL["accent2"])
        self.kernel_text.pack(fill="both", padx=4, pady=4)

        # ── Animation ────────────────────────────────────────────────────────
        section_label(inner, "Animation").pack(fill="x")
        anim_row = tk.Frame(inner, bg=PAL["surface"])
        anim_row.pack(fill="x", pady=(0, 12))
        flat_button(anim_row, "▶  Play", self.play_animation).pack(side="left")
        tk.Frame(anim_row, bg=PAL["surface"], width=6).pack(side="left")
        flat_button(anim_row, "■  Stop", self.stop_animation, accent=False).pack(side="left")

        # ── Actions ──────────────────────────────────────────────────────────
        section_label(inner, "Export").pack(fill="x")
        act_row = tk.Frame(inner, bg=PAL["surface"])
        act_row.pack(fill="x")
        flat_button(act_row, "📊  Histogram", self.show_histogram, accent=False).pack(side="left")
        tk.Frame(act_row, bg=PAL["surface"], width=6).pack(side="left")
        flat_button(act_row, "💾  Save", self.save_image).pack(side="left")

    def _build_preview(self, parent):
        preview = tk.Frame(parent, bg=PAL["bg"])
        preview.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        # Label row
        label_row = tk.Frame(preview, bg=PAL["bg"])
        label_row.pack(fill="x", pady=(0, 6))
        tk.Label(label_row, text="Original", bg=PAL["bg"],
                 fg=PAL["text_dim"], font=FONT_HEAD).pack(side="left", expand=True)
        tk.Label(label_row, text="→", bg=PAL["bg"],
                 fg=PAL["accent"], font=("Segoe UI", 16)).pack(side="left", padx=20)
        tk.Label(label_row, text="Filtered", bg=PAL["bg"],
                 fg=PAL["text_dim"], font=FONT_HEAD).pack(side="left", expand=True)

        # Canvas pair
        canvas_row = tk.Frame(preview, bg=PAL["bg"])
        canvas_row.pack(fill="both", expand=True)

        self.orig_canvas  = tk.Canvas(canvas_row, bg=PAL["surface"],
                                      highlightthickness=1,
                                      highlightbackground=PAL["border"])
        self.orig_canvas.pack(side="left", fill="both", expand=True)

        tk.Frame(canvas_row, bg=PAL["bg"], width=12).pack(side="left")

        self.filt_canvas  = tk.Canvas(canvas_row, bg=PAL["surface"],
                                      highlightthickness=1,
                                      highlightbackground=PAL["border"])
        self.filt_canvas.pack(side="left", fill="both", expand=True)

        # Bind resize
        self.orig_canvas.bind("<Configure>", lambda e: self._redraw())
        self.filt_canvas.bind("<Configure>", lambda e: self._redraw())

        # Status bar
        self.status_var = tk.StringVar(value="Ready — load an image to begin.")
        status_bar = tk.Frame(preview, bg=PAL["surface"], height=28)
        status_bar.pack(fill="x", pady=(8, 0))
        status_bar.pack_propagate(False)
        tk.Label(status_bar, textvariable=self.status_var,
                 bg=PAL["surface"], fg=PAL["text_dim"],
                 font=FONT_SMALL, anchor="w").pack(side="left", padx=10, pady=4)

        # Keep photo references alive
        self._orig_photo = None
        self._filt_photo = None

    # ── Category & Filter Selection ───────────────────────────────────────────

    def set_category(self, cat):
        self.cat_var.set(cat)
        # Update tab styles
        for c, btn in self._cat_buttons.items():
            if c == cat:
                btn.config(bg=PAL["accent"], fg="#ffffff")
            else:
                btn.config(bg=PAL["surface2"], fg=PAL["text_dim"])

        # Rebuild filter list
        for w in self._filter_listbox_frame.winfo_children():
            w.destroy()
        self._filter_buttons.clear()

        filters = list(self.filter_configs[cat].keys())
        for i, fname in enumerate(filters):
            b = tk.Label(self._filter_listbox_frame, text=fname,
                         bg=PAL["surface2"], fg=PAL["text_dim"],
                         font=FONT_SMALL, cursor="hand2",
                         anchor="w", padx=10, pady=5, relief="flat")
            b.pack(fill="x", pady=1)
            b.bind("<Button-1>", lambda e, f=fname: self.set_filter(f))
            b.bind("<Enter>",    lambda e, btn=b, f=fname: btn.config(
                bg=PAL["accent2"] if f != self._filter_var.get() else PAL["accent"]))
            b.bind("<Leave>",    lambda e, btn=b, f=fname: btn.config(
                bg=PAL["accent"] if f == self._filter_var.get() else PAL["surface2"]))
            self._filter_buttons[fname] = b

        self.set_filter(filters[0])

    def set_filter(self, fname):
        self._filter_var.set(fname)
        cat = self.cat_var.get()
        # Highlight selected
        for f, btn in self._filter_buttons.items():
            btn.config(bg=PAL["accent"] if f == fname else PAL["surface2"],
                       fg="#ffffff" if f == fname else PAL["text_dim"])
        self._rebuild_params(cat, fname)
        self._apply_filter()

    # ── Parameter Sliders ─────────────────────────────────────────────────────

    def _rebuild_params(self, cat, fname):
        for w in self.params_container.winfo_children():
            w.destroy()
        self.param_widgets.clear()

        _, defaults = self.filter_configs[cat][fname]
        if not defaults:
            tk.Label(self.params_container, text="No adjustable parameters.",
                     bg=PAL["surface"], fg=PAL["text_dim"],
                     font=FONT_SMALL).pack(anchor="w")
            return

        for param, default_val in defaults.items():
            if param not in self.param_meta:
                continue
            pmin, pmax, _, is_odd = self.param_meta[param]

            row = tk.Frame(self.params_container, bg=PAL["surface"])
            row.pack(fill="x", pady=3)

            # Label
            display_name = param.replace("_", " ").title()
            tk.Label(row, text=display_name, bg=PAL["surface"],
                     fg=PAL["text"], font=FONT_SMALL, width=14,
                     anchor="w").pack(side="left")

            # Value label
            val_label = tk.Label(row, text=str(default_val),
                                 bg=PAL["surface"], fg=PAL["accent"],
                                 font=FONT_SMALL, width=4)
            val_label.pack(side="right")

            # Slider
            s = dark_slider(row, pmin, pmax,
                            lambda v, p=param, l=val_label, odd=is_odd:
                                self._on_param(p, v, l, odd),
                            initial=default_val)
            s.pack(side="left", fill="x", expand=True, padx=4)

            self.param_widgets[param] = {"slider": s, "label": val_label, "is_odd": is_odd}

    def _on_param(self, param, raw_val, label, is_odd):
        v = int(float(raw_val))
        if is_odd and v % 2 == 0:
            v += 1
            self.param_widgets[param]["slider"].set(v)
        label.config(text=str(v))
        # Debounce
        if self._after_id:
            self.root.after_cancel(self._after_id)
        self._after_id = self.root.after(80, self._apply_filter)

    # ── Core Filter Application ───────────────────────────────────────────────

    def _build_call_params(self, cat, fname):
        """
        BUG FIX #4: Build the correct kwargs dict for each filter,
        correctly converting kw → kernel_size tuple, and keeping
        ksize as a plain int for median_blur.
        """
        _, defaults = self.filter_configs[cat][fname]
        params = {}

        for param, default_val in defaults.items():
            if param in self.param_widgets:
                v = int(float(self.param_widgets[param]["slider"].get()))
                if self.param_widgets[param]["is_odd"] and v % 2 == 0:
                    v += 1
            else:
                v = default_val

            # "kw" is our internal name for kernel width → convert to tuple
            if param == "kw":
                params["kernel_size"] = (v, v)
            else:
                params[param] = v

        return params

    def _apply_filter(self):
        if self.original_image is None:
            return

        cat   = self.cat_var.get()
        fname = self._filter_var.get()
        if not fname:
            return

        func, _ = self.filter_configs[cat][fname]
        params   = self._build_call_params(cat, fname)

        try:
            # Work in grayscale
            if self.original_image.ndim == 3:
                gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = self.original_image.copy()

            result = func(gray, **params)

            # Normalise float outputs (edge detectors)
            if result.dtype != np.uint8:
                result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX)
                result = result.astype(np.uint8)

            self.filtered_image = result
            self._redraw()
            self._update_kernel_display(fname, params)
            self.status_var.set(f"Filter: {fname}  |  params: {params}")

        except Exception as ex:
            self.status_var.set(f"⚠  Error: {ex}")

    # ── Image Display ─────────────────────────────────────────────────────────

    def _redraw(self):
        """BUG FIX #5: fit image to the full canvas area."""
        self._draw_on_canvas(self.orig_canvas, self.original_image,
                             is_gray=False, ref_attr="_orig_photo")
        self._draw_on_canvas(self.filt_canvas, self.filtered_image,
                             is_gray=True,  ref_attr="_filt_photo")

    def _draw_on_canvas(self, canvas, img, is_gray, ref_attr):
        if img is None:
            canvas.delete("all")
            cw = canvas.winfo_width()  or 400
            ch = canvas.winfo_height() or 300
            canvas.create_text(cw//2, ch//2, text="No image",
                                fill=PAL["text_dim"], font=FONT_BODY)
            return

        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 2 or ch < 2:
            return

        h, w = img.shape[:2]
        scale = min(cw / w, ch / h)
        nw, nh = int(w * scale), int(h * scale)

        resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)

        if is_gray or resized.ndim == 2:
            pil_img = Image.fromarray(resized if resized.ndim == 2
                                      else cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
        else:
            pil_img = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))

        photo = ImageTk.PhotoImage(pil_img)
        setattr(self, ref_attr, photo)

        canvas.delete("all")
        # Centre the image
        x = (cw - nw) // 2
        y = (ch - nh) // 2
        canvas.create_image(x, y, anchor="nw", image=photo)

    # ── Kernel Display ────────────────────────────────────────────────────────

    def _toggle_kernel(self, _event=None):
        """BUG FIX #3: kernel was never enabled for writing."""
        if self.show_kernel_var.get():
            self.show_kernel_var.set(False)
            self._kernel_toggle.config(text="○  Show kernel", fg=PAL["text_dim"])
            self.kernel_frame.pack_forget()
        else:
            self.show_kernel_var.set(True)
            self._kernel_toggle.config(text="●  Hide kernel", fg=PAL["accent"])
            self.kernel_frame.pack(fill="x", pady=(0, 12))
            self._update_kernel_display(self._filter_var.get(), {})

    def _update_kernel_display(self, fname, params):
        """Write kernel info — always enable the Text widget first."""
        if not self.show_kernel_var.get():
            return

        lines = [f"Filter : {fname}"]
        if params:
            lines.append("Params : " + ", ".join(f"{k}={v}" for k, v in params.items()))

        # Show a representative kernel matrix where applicable
        ksize = None
        if "kernel_size" in params and isinstance(params["kernel_size"], tuple):
            ksize = params["kernel_size"][0]
        elif "ksize" in params:
            ksize = params["ksize"]

        if ksize and fname in ("Standard Blur", "Gaussian Blur", "Box Filter"):
            k = np.ones((ksize, ksize), dtype=float) / (ksize * ksize)
            lines.append(f"\nKernel ({ksize}×{ksize}):")
            for row in k:
                lines.append("  " + "  ".join(f"{v:.3f}" for v in row))
        elif fname == "Sobel":
            lines.append("\nSobel-X (3×3):")
            for r in [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]:
                lines.append("  " + "  ".join(f"{v:3d}" for v in r))
        elif fname == "Laplacian":
            lines.append("\nLaplacian (3×3):")
            for r in [[0, 1, 0], [1, -4, 1], [0, 1, 0]]:
                lines.append("  " + "  ".join(f"{v:3d}" for v in r))

        text = "\n".join(lines)

        # BUG FIX #3: must set state NORMAL before inserting
        self.kernel_text.config(state="normal")
        self.kernel_text.delete("1.0", "end")
        self.kernel_text.insert("1.0", text)
        self.kernel_text.config(state="disabled")

    # ── Image I/O ─────────────────────────────────────────────────────────────

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                       ("All files", "*.*")])
        if not path:
            return
        img = load_image(path)
        if img is None:
            messagebox.showerror("Load Error", "Could not open that file.")
            return
        self.original_image = img
        self.filtered_image = None
        self._apply_filter()
        self.status_var.set(f"Loaded: {path.split('/')[-1].split(chr(92))[-1]}")

    def reset_image(self):
        if self.original_image is None:
            return
        self.filtered_image = None
        self._redraw()
        self.status_var.set("Reset — showing original image.")

    def save_image(self):
        if self.filtered_image is None:
            messagebox.showwarning("Nothing to save", "Apply a filter first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All", "*.*")])
        if not path:
            return
        cv2.imwrite(path, self.filtered_image)
        self.status_var.set(f"Saved → {path.split('/')[-1]}")
        messagebox.showinfo("Saved", f"Image written to:\n{path}")

    # ── Histogram ─────────────────────────────────────────────────────────────

    def show_histogram(self):
        if self.original_image is None:
            messagebox.showwarning("No image", "Load an image first.")
            return

        win = tk.Toplevel(self.root)
        win.title("Histogram")
        win.configure(bg=PAL["bg"])
        win.geometry("700x420")

        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure

        fig = Figure(figsize=(7, 4), dpi=100, facecolor=PAL["surface"])
        ax  = fig.add_subplot(111)
        ax.set_facecolor(PAL["bg"])

        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY) \
               if self.original_image.ndim == 3 else self.original_image
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

        ax.fill_between(range(256), hist.flatten(), alpha=0.6, color="#e94560")
        ax.plot(hist, color="#e94560", linewidth=1.5)
        ax.set_title("Grayscale Histogram", color=PAL["text"], fontsize=11)
        ax.set_xlabel("Pixel Intensity", color=PAL["text_dim"])
        ax.set_ylabel("Frequency",       color=PAL["text_dim"])
        ax.tick_params(colors=PAL["text_dim"])
        for spine in ax.spines.values():
            spine.set_color(PAL["border"])
        ax.grid(True, color=PAL["border"], linestyle="--", alpha=0.5)
        fig.tight_layout()

        fc = FigureCanvasTkAgg(fig, master=win)
        fc.draw()
        fc.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # ── Animation ─────────────────────────────────────────────────────────────

    def play_animation(self):
        if self.original_image is None:
            messagebox.showwarning("No image", "Load an image first.")
            return
        if self.filtered_image is None:
            messagebox.showwarning("No filter", "Apply a filter first.")
            return
        self.animation_active = True
        self.status_var.set("▶  Animation playing…")
        t = threading.Thread(target=self._animate_thread, daemon=True)
        t.start()

    def _animate_thread(self):
        gray_orig = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY) \
                    if self.original_image.ndim == 3 else self.original_image.copy()

        frames = 20
        for i in range(frames + 1):
            if not self.animation_active:
                break
            alpha = i / frames
            blended = cv2.addWeighted(gray_orig, 1 - alpha,
                                      self.filtered_image, alpha, 0)
            # schedule draw on main thread
            self.root.after(0, self._draw_blend_frame, blended)
            time.sleep(0.05)

        self.root.after(0, self._end_animation)

    def _draw_blend_frame(self, frame):
        self._draw_on_canvas(self.filt_canvas, frame,
                             is_gray=True, ref_attr="_filt_photo")

    def _end_animation(self):
        self.animation_active = False
        self._redraw()
        self.status_var.set("Animation complete.")

    def stop_animation(self):
        self.animation_active = False
        self._redraw()
        self.status_var.set("Animation stopped.")


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()

    # Dark title bar on Windows
    try:
        from ctypes import windll
        windll.dwmapi.DwmSetWindowAttribute(
            windll.user32.GetForegroundWindow(), 20,
            (4).to_bytes(4, "little"), 4)
    except Exception:
        pass

    app = FilterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
