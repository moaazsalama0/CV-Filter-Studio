import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
from collections import OrderedDict

# Import all filters and utilities
from Filters.blur import (blur, gaussian_blur, median_blur, 
                          bilateral_filter, box_filter)
from Filters.edge_detection import (canny_edge_detection, sobel_edge_detection,
                                     laplacian_edge_detection, prewitt_edge_detection,
                                     scharr_edge_detection, roberts_edge_detection)
from Filters.threshold import (threshold, adaptive_threshold, otsu_threshold)
from utils.image_loader import load_image
from utils.histogram import plot_histogram, plot_color_histogram


class FilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 CV Filter Studio - Advanced Image Editor")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#1e1e1e")
        
        # State variables
        self.original_image = None
        self.current_image = None
        self.show_kernel = False
        self.animation_active = False
        self.kernel_data = None
        
        # Filter configurations with parameters
        self.filter_configs = OrderedDict([
            ("Blur", {
                "filters": {
                    "Standard Blur": (blur, {"kernel_size": (5, 5)}),
                    "Gaussian Blur": (gaussian_blur, {"kernel_size": (5, 5), "sigma_x": 0}),
                    "Median Blur": (median_blur, {"kernel_size": 5}),
                    "Bilateral": (bilateral_filter, {"diameter": 9, "sigma_color": 75, "sigma_space": 75}),
                    "Box Filter": (box_filter, {"kernel_size": (5, 5)}),
                },
                "params": {
                    "kernel_size": {"type": "slider", "range": (3, 21), "step": 2},
                    "diameter": {"type": "slider", "range": (3, 21), "step": 2},
                    "sigma_x": {"type": "slider", "range": (0, 100), "step": 1},
                    "sigma_color": {"type": "slider", "range": (10, 200), "step": 10},
                    "sigma_space": {"type": "slider", "range": (10, 200), "step": 10},
                }
            }),
            ("Edge Detection", {
                "filters": {
                    "Canny Edge": (canny_edge_detection, {"low_threshold": 100, "high_threshold": 200}),
                    "Sobel": (sobel_edge_detection, {"dx": 1, "dy": 0, "kernel_size": 3}),
                    "Laplacian": (laplacian_edge_detection, {"kernel_size": 3}),
                    "Prewitt": (prewitt_edge_detection, {}),
                    "Scharr": (scharr_edge_detection, {"dx": 1, "dy": 0}),
                    "Roberts": (roberts_edge_detection, {}),
                },
                "params": {
                    "low_threshold": {"type": "slider", "range": (0, 200), "step": 10},
                    "high_threshold": {"type": "slider", "range": (50, 400), "step": 10},
                    "kernel_size": {"type": "slider", "range": (1, 7), "step": 2},
                }
            }),
            ("Threshold", {
                "filters": {
                    "Binary Threshold": (threshold, {"threshold_value": 127, "max_value": 255}),
                    "Adaptive Threshold": (adaptive_threshold, {"max_value": 255, "block_size": 11, "C": 2}),
                    "Otsu Threshold": (otsu_threshold, {"max_value": 255}),
                },
                "params": {
                    "threshold_value": {"type": "slider", "range": (0, 255), "step": 1},
                    "max_value": {"type": "slider", "range": (0, 255), "step": 1},
                    "block_size": {"type": "slider", "range": (3, 31), "step": 2},
                    "C": {"type": "slider", "range": (-50, 50), "step": 1},
                }
            }),
        ])
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control Panel (Left)
        self.control_panel = ttk.Frame(main_container)
        self.control_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        self.setup_control_panel()
        
        # Image Display Area (Right)
        self.image_panel = ttk.Frame(main_container)
        self.image_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.setup_image_display()
    
    def setup_control_panel(self):
        """Setup the control panel with buttons and options"""
        # Title
        title = ttk.Label(self.control_panel, text="Image Editor Controls", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Image Loading
        load_frame = ttk.LabelFrame(self.control_panel, text="📁 Load Image")
        load_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(load_frame, text="Browse Image", command=self.load_image).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(load_frame, text="Reset", command=self.reset_image).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Category Selection
        category_frame = ttk.LabelFrame(self.control_panel, text="🎯 Filter Category")
        category_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.category_var = tk.StringVar(value="Blur")
        for category in self.filter_configs.keys():
            ttk.Radiobutton(category_frame, text=category, variable=self.category_var, 
                           value=category, command=self.on_category_change).pack(anchor=tk.W, padx=10, pady=5)
        
        # Filter Selection
        filter_frame = ttk.LabelFrame(self.control_panel, text="✨ Select Filter")
        filter_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.filter_var = tk.StringVar()
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, state="readonly", width=25)
        self.filter_combo.pack(fill=tk.X, padx=5, pady=5)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.update_filter_preview())
        
        # Parameters Frame
        self.params_frame = ttk.LabelFrame(self.control_panel, text="⚙️ Parameters")
        self.params_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.param_widgets = {}
        
        # Kernel Display Toggle
        kernel_frame = ttk.LabelFrame(self.control_panel, text="🔢 Kernel Information")
        kernel_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.kernel_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(kernel_frame, text="Show Kernel Matrix", variable=self.kernel_var,
                       command=self.toggle_kernel_display).pack(anchor=tk.W, padx=10, pady=5)
        
        self.kernel_text = tk.Text(kernel_frame, height=6, width=30, font=("Courier", 8))
        self.kernel_text.pack(padx=5, pady=5, fill=tk.BOTH)
        
        # Animation Controls
        animation_frame = ttk.LabelFrame(self.control_panel, text="🎬 Animation")
        animation_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(animation_frame, text="🎯 Play Animation", command=self.play_animation).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(animation_frame, text="⏹️ Stop Animation", command=self.stop_animation).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Histogram & Save
        action_frame = ttk.LabelFrame(self.control_panel, text="📊 Actions")
        action_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(action_frame, text="📈 Show Histogram", command=self.show_histogram).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(action_frame, text="💾 Save Image", command=self.save_image).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Initialize filter display after all frames are created
        self.on_category_change()
    
    def setup_image_display(self):
        """Setup the image display area with before/after views"""
        # Title
        title = ttk.Label(self.image_panel, text="Image Preview", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Image display frame
        display_frame = ttk.Frame(self.image_panel)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Before image
        before_frame = ttk.LabelFrame(display_frame, text="Original")
        before_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.before_label = ttk.Label(before_frame, background="#333333")
        self.before_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Arrow indicator
        arrow_label = ttk.Label(display_frame, text="→", font=("Arial", 20))
        arrow_label.pack(side=tk.LEFT, padx=10)
        
        # After image
        after_frame = ttk.LabelFrame(display_frame, text="Filtered")
        after_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.after_label = ttk.Label(after_frame, background="#333333")
        self.after_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready. Please load an image.")
        status_bar = ttk.Label(self.image_panel, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, padx=5, pady=5)
    
    def on_category_change(self):
        """Update filter options when category changes"""
        category = self.category_var.get()
        filters = list(self.filter_configs[category]["filters"].keys())
        self.filter_combo["values"] = filters
        if filters:
            self.filter_combo.set(filters[0])
            self.update_parameter_sliders()
            self.update_filter_preview()
    
    def update_parameter_sliders(self):
        """Update parameter sliders based on selected filter"""
        # Clear previous widgets
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        self.param_widgets.clear()
        
        category = self.category_var.get()
        filter_name = self.filter_var.get()
        
        if not filter_name:
            return
        
        # Get filter function and default parameters
        filter_func, defaults = self.filter_configs[category]["filters"][filter_name]
        
        # Create sliders for each parameter
        for param, value in defaults.items():
            if param in self.filter_configs[category]["params"]:
                param_info = self.filter_configs[category]["params"][param]
                
                frame = ttk.Frame(self.params_frame)
                frame.pack(fill=tk.X, padx=5, pady=5)
                
                ttk.Label(frame, text=f"{param}:").pack(side=tk.LEFT, padx=5)
                
                if isinstance(value, tuple):
                    value = value[0]
                
                min_val, max_val = param_info["range"]
                slider = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                                  command=lambda v, p=param: self.on_parameter_change(p, v))
                slider.set(min(value, max_val) if value <= max_val else max_val)
                slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                value_label = ttk.Label(frame, text=str(value), width=5)
                value_label.pack(side=tk.LEFT, padx=5)
                
                self.param_widgets[param] = {"slider": slider, "label": value_label, "type": param_info["type"]}
    
    def on_parameter_change(self, param_name, value):
        """Handle parameter slider changes"""
        param_type = self.param_widgets[param_name]["type"]
        
        if param_type == "slider":
            if param_name == "kernel_size" and param_name in [p for p in self.param_widgets.keys()]:
                int_value = int(float(value))
                if int_value % 2 == 0:
                    int_value += 1
                self.param_widgets[param_name]["slider"].set(int_value)
                self.param_widgets[param_name]["label"].config(text=str(int_value))
            else:
                int_value = int(float(value))
                self.param_widgets[param_name]["label"].config(text=str(int_value))
        
        self.update_filter_preview()
    
    def load_image(self):
        """Load an image from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("All files", "*.*")]
        )
        
        if file_path:
            self.original_image = load_image(file_path)
            self.current_image = self.original_image.copy()
            self.display_images()
            self.status_var.set(f"Image loaded: {file_path.split('/')[-1]}")
    
    def reset_image(self):
        """Reset to original image"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.display_images()
            self.kernel_text.delete("1.0", tk.END)
            self.status_var.set("Image reset to original")
    
    def update_filter_preview(self):
        """Apply filter and update preview"""
        if self.original_image is None:
            messagebox.showwarning("No Image", "Please load an image first")
            return
        
        category = self.category_var.get()
        filter_name = self.filter_var.get()
        
        if not filter_name:
            return
        
        filter_func, defaults = self.filter_configs[category]["filters"][filter_name]
        
        # Build parameters from sliders
        params = defaults.copy()
        for param, widgets in self.param_widgets.items():
            value = widgets["slider"].get()
            if "size" in param or "block_size" in param:
                value = int(value)
                if value % 2 == 0:
                    value += 1
                if "kernel_size" in param or "size" in param:
                    value = (value, value)
            elif "threshold" in param or "diameter" in param:
                value = int(value)
            else:
                value = int(value)
            
            if param in params:
                params[param] = value
        
        try:
            # Convert to grayscale if needed
            if len(self.original_image.shape) == 3:
                processing_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            else:
                processing_image = self.original_image
            
            self.current_image = filter_func(processing_image, **params)
            
            # Generate kernel visualization
            self.generate_kernel_display(filter_name, params)
            
            self.display_images()
            self.status_var.set(f"✨ Filter applied: {filter_name}")
        except Exception as e:
            messagebox.showerror("Filter Error", f"Error applying filter:\n{str(e)}")
            self.status_var.set("❌ Error applying filter")
    
    def generate_kernel_display(self, filter_name, params):
        """Generate kernel matrix for display"""
        kernel_info = f"Filter: {filter_name}\n"
        kernel_info += f"Parameters:\n"
        
        for param, value in params.items():
            kernel_info += f"  • {param}: {value}\n"
        
        # Generate some kernel visualizations based on filter type
        if "kernel_size" in params:
            kernel_size = params["kernel_size"]
            if isinstance(kernel_size, tuple):
                kernel_size = kernel_size[0]
            kernel = np.ones((kernel_size, kernel_size)) / (kernel_size * kernel_size)
            kernel_info += f"\nGaussian-like Kernel ({kernel_size}x{kernel_size}):\n"
            for row in kernel:
                kernel_info += "  " + "  ".join([f"{v:.3f}" for v in row]) + "\n"
        
        self.kernel_text.config(state=tk.NORMAL)
        self.kernel_text.delete("1.0", tk.END)
        self.kernel_text.insert("1.0", kernel_info)
        self.kernel_text.config(state=tk.DISABLED)
        self.kernel_data = kernel_info
    
    def toggle_kernel_display(self):
        """Toggle kernel display on/off"""
        self.show_kernel = self.kernel_var.get()
    
    def display_images(self):
        """Display original and filtered images side by side"""
        if self.original_image is None:
            return
        
        # Prepare images for display (resize to fit window)
        display_size = (350, 300)
        
        before_img = self.resize_image_for_display(self.original_image, display_size)
        after_img = self.resize_image_for_display(self.current_image, display_size)
        
        # Convert to PhotoImage
        before_photo = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(before_img, cv2.COLOR_BGR2RGB)))
        
        if len(after_img.shape) == 2:
            after_photo = ImageTk.PhotoImage(Image.fromarray(after_img, mode="L"))
        else:
            after_photo = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(after_img, cv2.COLOR_BGR2RGB)))
        
        # Update labels
        self.before_label.config(image=before_photo)
        self.before_label.image = before_photo
        
        self.after_label.config(image=after_photo)
        self.after_label.image = after_photo
    
    def resize_image_for_display(self, image, max_size):
        """Resize image to fit display while maintaining aspect ratio"""
        h, w = image.shape[:2]
        max_h, max_w = max_size
        
        scale = min(max_w / w, max_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        return cv2.resize(image, (new_w, new_h))
    
    def play_animation(self):
        """Play animated filter application"""
        if self.original_image is None:
            messagebox.showwarning("No Image", "Please load an image first")
            return
        
        self.animation_active = True
        self.status_var.set("▶️ Animation playing...")
        
        # Run animation in separate thread
        thread = threading.Thread(target=self._animation_thread)
        thread.daemon = True
        thread.start()
    
    def _animation_thread(self):
        """Animation thread that gradually applies the filter"""
        if not self.animation_active or self.original_image is None:
            return
        
        # Create a series of filter strength variations
        num_frames = 10
        for frame in range(num_frames + 1):
            if not self.animation_active:
                break
            
            # Blend original with filtered image
            alpha = frame / num_frames
            
            if len(self.current_image.shape) == 2:
                blended = cv2.addWeighted(
                    cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY), 1 - alpha,
                    self.current_image, alpha, 0
                )
            else:
                if len(self.original_image.shape) == 3:
                    original_gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
                else:
                    original_gray = self.original_image
                blended = cv2.addWeighted(original_gray, 1 - alpha, self.current_image, alpha, 0)
            
            # Display intermediate frame
            display_size = (350, 300)
            blended_resized = self.resize_image_for_display(blended, display_size)
            
            if len(blended_resized.shape) == 2:
                blended_photo = ImageTk.PhotoImage(Image.fromarray(blended_resized, mode="L"))
            else:
                blended_photo = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(blended_resized, cv2.COLOR_BGR2RGB)))
            
            self.after_label.config(image=blended_photo)
            self.after_label.image = blended_photo
            
            self.root.update()
            time.sleep(0.1)
        
        self.display_images()
        self.animation_active = False
        self.status_var.set("✅ Animation completed")
    
    def stop_animation(self):
        """Stop the animation"""
        self.animation_active = False
        self.display_images()
        self.status_var.set("⏹️ Animation stopped")
    
    def show_histogram(self):
        """Display histogram of the image"""
        if self.original_image is None:
            messagebox.showwarning("No Image", "Please load an image first")
            return
        
        hist_window = tk.Toplevel(self.root)
        hist_window.title("Histogram Viewer")
        
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
        
        # Create figure
        fig = Figure(figsize=(10, 5), dpi=100)
        
        # Plot histograms
        gray_img = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
        
        ax = fig.add_subplot(111)
        ax.plot(hist, color='black')
        ax.set_title("Grayscale Histogram")
        ax.set_xlabel("Pixel Intensity")
        ax.set_ylabel("Frequency")
        ax.grid(True)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=hist_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def save_image(self):
        """Save the filtered image"""
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please load an image first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                cv2.imwrite(file_path, self.current_image)
                messagebox.showinfo("Success", f"Image saved to:\n{file_path}")
                self.status_var.set(f"💾 Image saved: {file_path.split('/')[-1]}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving image:\n{str(e)}")


def main():
    root = tk.Tk()
    app = FilterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
