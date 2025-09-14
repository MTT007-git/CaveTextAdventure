"""
Converts an image to ASCII art
Not used by the quest programm, but was used to create the ASCII art

Written by ChatGPT 5.0

https://chatgpt.com/share/68b865b3-b180-8011-a75d-800995db694c
Everything that is not in the convesation end was written by me
"""

from PIL import Image, ImageSequence, ImageEnhance
import sys
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import time
import threading

# Default ASCII characters (from dark to light)
DEFAULT_ASCII_CHARS = "@#S%?*+;:,."


# Resize image according to new width
def resize_image(image, new_width=80):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)
    return image.resize((new_width, new_height))


# Convert each pixel to grayscale
def grayify(image):
    return image.convert("L")


# Convert pixels to ASCII
def pixels_to_ascii(image, ascii_chars):
    pixels = image.getdata()
    interval = 256 / len(ascii_chars)
    ascii_str = "".join([ascii_chars[int(pixel // interval)] for pixel in pixels])
    return ascii_str


# Convert image to ASCII frame
def image_to_ascii(image, new_width=80, ascii_chars=DEFAULT_ASCII_CHARS, brightness=1.0, contrast=1.0):
    # Resize first
    image = resize_image(image, new_width)

    # Apply brightness & contrast adjustments
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness)
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)

    # Convert to grayscale
    image = grayify(image)

    # Map pixels to ASCII
    ascii_str = pixels_to_ascii(image, ascii_chars)
    pixel_count = len(ascii_str)
    ascii_image = "\n".join([ascii_str[i:(i + new_width)] for i in range(0, pixel_count, new_width)])
    return ascii_image


# Extract original frames (PIL images)
def extract_frames(path):
    try:
        img = Image.open(path)
    except Exception as e:
        return [], f"Error: {e}"

    originals = []
    if getattr(img, "is_animated", False):
        for frame in ImageSequence.Iterator(img):
            originals.append(frame.copy().convert("RGB"))
    else:
        originals.append(img.convert("RGB"))
    return originals, None


# Process frames into ASCII
def process_frames(frames, new_width, ascii_chars, brightness, contrast, zoom=1.0, x=0, y=0):
    ascii_frames = []
    for frame in frames:
        center = (frame.size[0]//2, frame.size[1]//2)
        crop = (center[0]+x-center[0]//zoom, center[1]+y-center[1]//zoom, center[0]+x+center[0]//zoom,
                center[1]+y+center[1]//zoom)
        ascii_frames.append(image_to_ascii(frame.crop(crop), new_width, ascii_chars, brightness, contrast))
    return ascii_frames


# GUI Application
def launch_gui():
    def load_image():
        path = filedialog.askopenfilename(filetypes=[("Images", "*.gif *.png *.jpg *.jpeg")])
        if not path:
            return
        originals, err = extract_frames(path)
        if err:
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, err)
            return
        app_state["path"] = path
        app_state["original_frames"] = originals
        app_state["playing"] = False
        app_state["animation"] = None
        update_ascii()

    def create_anim(orig_frames, anim, x, y):
        if anim is None:
            return orig_frames, x, y
        if anim["name"] == "zoom":
            orig_frames = [orig_frames[0] for _ in range(anim["frames"])]
            for i in range(anim["frames"]):
                zoom = anim["from"]+i/anim["frames"]*(anim["to"]-anim["from"])
                center = (orig_frames[i].size[0]//2, orig_frames[i].size[1]//2)
                crop = (center[0]+x-center[0]//zoom, center[1]+y-center[1]//zoom, center[0]+x+center[0]//zoom,
                        center[1]+y+center[1]//zoom)
                orig_frames[i] = orig_frames[i].crop(crop)
            return orig_frames, 0, 0
        return orig_frames, x, y

    def update_ascii(*args, reset=True):
        if not app_state.get("original_frames"):
            return
        x_scale.config(from_=-app_state["original_frames"][0].size[0]//2,
                       to=app_state["original_frames"][0].size[0]//2)
        y_scale.config(from_=-app_state["original_frames"][0].size[1]//2,
                       to=app_state["original_frames"][0].size[1]//2)
        frames, x, y = create_anim(app_state["original_frames"], app_state["animation"], x_scale.get(), y_scale.get())
        app_state["frames"] = process_frames(
            frames=frames,
            new_width=width_scale.get(),
            ascii_chars=chars_entry.get() or DEFAULT_ASCII_CHARS,
            brightness=brightness_scale.get(),
            contrast=contrast_scale.get(),
            zoom=zoom_scale.get(),
            x=x,
            y=y
        )
        if not app_state["playing"]:
            if reset:
                show_frame(0)
            else:
                show_frame(app_state["current_frame"])

    def show_frame(index):
        if not app_state.get("frames"):
            return
        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, app_state["frames"][index])
        print("\n\n"+app_state["frames"][index], end="")
        app_state["current_frame"] = index

    def make_anim():
        def reset_anim():
            app_state["animation"] = None
            dlg.destroy()
            update_ascii()

        def create_zoom_anim(from_=0.0, to=0.0, frames=0):
            app_state["animation"] = {"name": "zoom", "from": from_, "to": to, "frames": frames}
            dlg.destroy()
            update_ascii()

        stop_animation()
        dlg = tk.Toplevel(root)
        dlg.title("Animation")
        dlg_width, dlg_height = 500, 275
        dlg.geometry(f"{dlg_width}x{dlg_height}+{(root.winfo_screenwidth()-dlg_width)//2}"
                     f"+{(root.winfo_screenheight()-dlg_height)//2}")

        notebook = ttk.Notebook(dlg)
        notebook.pack(fill="both")
        zoom_frame = tk.Frame(notebook)
        notebook.add(zoom_frame, text="Zoom")
        tk.Label(zoom_frame, text="From").pack()
        zoom_from_scale = tk.Scale(zoom_frame, from_=1.0, to=10.0, resolution=0.1, orient="horizontal")
        zoom_from_scale.pack(fill="x")
        tk.Label(zoom_frame, text="To").pack()
        zoom_to_scale = tk.Scale(zoom_frame, from_=1.0, to=10.0, resolution=0.1, orient="horizontal")
        zoom_to_scale.pack(fill="x")
        tk.Label(zoom_frame, text="Frames (1 frame = 0.1s)").pack()
        zoom_frames_scale = tk.Scale(zoom_frame, from_=2, to=100, orient="horizontal")
        zoom_frames_scale.pack(fill="x")
        if app_state["animation"] is not None and app_state["animation"]["name"] == "zoom":
            zoom_from_scale.set(app_state["animation"]["from"])
            zoom_to_scale.set(app_state["animation"]["to"])
            zoom_frames_scale.set(app_state["animation"]["frames"])
        ttk.Button(zoom_frame, text="Create",
                   command=lambda: create_zoom_anim(zoom_from_scale.get(), zoom_to_scale.get(), zoom_frames_scale.get()
                                                    )).pack()
        ttk.Button(dlg, text="Reset animation", command=reset_anim).pack()

        dlg.transient(root)
        dlg.grab_set()
        dlg.focus_set()
        dlg.wait_window(root)

    def play_animation():
        if not app_state.get("frames") or app_state.get("playing"):
            return
        app_state["playing"] = True

        def animate():
            while app_state["playing"]:
                frames = app_state.get("frames", [])
                if not frames:
                    break
                idx = (app_state.get("current_frame", 0) + 1) % len(frames)
                show_frame(idx)
                time.sleep(0.1)
        threading.Thread(target=animate, daemon=True).start()

    def stop_animation():
        app_state["playing"] = False

    def reset_animation():
        app_state["playing"] = False
        app_state["current_frame"] = 0
        update_ascii()

    def step_animation(step=1):
        app_state["playing"] = False
        app_state["current_frame"] = (app_state.get("current_frame", 0) + step) % len(app_state.get("frames", []))
        update_ascii(reset=False)

    def export_ascii():
        if not app_state.get("frames"):
            return
        path = filedialog.asksaveasfilename(defaultextension=".ascii",
                                            filetypes=[("ASCII art", "*.ascii"), ("Text Files", "*.txt")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            for i, frame in enumerate(app_state["frames"]):
                f.write(f"-FRAME-\n")
                f.write(frame + "\n\n")

    app_state = {"path": None, "original_frames": [], "frames": [], "current_frame": 0, "playing": False,
                 "animation": None}

    root = tk.Tk()
    root.title("Image to ASCII Converter")

    ttk.Button(root, text="Load Image", command=load_image).pack(pady=5)

    tk.Label(root, text="Width").pack()
    width_scale = tk.Scale(root, from_=40, to=200, orient="horizontal", command=update_ascii)
    width_scale.set(80)
    width_scale.pack(fill="x")

    tk.Label(root, text="Brightness").pack()
    brightness_scale = tk.Scale(root, from_=0.2, to=2.0, resolution=0.1, orient="horizontal", command=update_ascii)
    brightness_scale.set(1.0)
    brightness_scale.pack(fill="x")

    tk.Label(root, text="Contrast").pack()
    contrast_scale = tk.Scale(root, from_=0.2, to=2.0, resolution=0.1, orient="horizontal", command=update_ascii)
    contrast_scale.set(1.0)
    contrast_scale.pack(fill="x")

    tk.Label(root, text="Zoom").pack()
    zoom_scale = tk.Scale(root, from_=1.0, to=10.0, resolution=0.1, orient="horizontal", command=update_ascii)
    zoom_scale.set(1.0)
    zoom_scale.pack(fill="x")

    tk.Label(root, text="X").pack()
    x_scale = tk.Scale(root, from_=0, to=0, orient="horizontal", command=update_ascii)
    x_scale.set(1.0)
    x_scale.pack(fill="x")

    tk.Label(root, text="Y").pack()
    y_scale = tk.Scale(root, from_=0, to=0, orient="horizontal", command=update_ascii)
    y_scale.set(1.0)
    y_scale.pack(fill="x")

    # tk.Label(root, text="Font size").pack()
    # font_scale = tk.Scale(root, from_=6, to=24, orient="horizontal",
    #                       command=lambda e: text_box.config(font=("Courier", font_scale.get())))
    # font_scale.set(10)
    # font_scale.pack(fill="x")

    tk.Label(root, text="ASCII Characters (dark → light)").pack()
    chars_entry = ttk.Entry(root)
    chars_entry.insert(0, DEFAULT_ASCII_CHARS)
    chars_entry.bind("<KeyRelease>", update_ascii)
    chars_entry.pack(fill="x", pady=5)

    ttk.Button(root, text="Make animation...", command=make_anim).pack()

    control_frame = tk.Frame(root)
    control_frame.pack(pady=5)

    ttk.Button(control_frame, text="Play", command=play_animation).grid(row=0, column=0, padx=(3, 0))
    ttk.Button(control_frame, text="Stop", command=stop_animation).grid(row=0, column=1)
    ttk.Button(control_frame, text="<", command=lambda: step_animation(-1), width=2).grid(row=0, column=2)
    ttk.Button(control_frame, text=">", command=lambda: step_animation(1), width=2).grid(row=0, column=3)
    ttk.Button(control_frame, text="Reset", command=reset_animation).grid(row=0, column=4, padx=(0, 3))
    ttk.Button(root, text="Export", command=export_ascii).pack(pady=(0, 5))

    text_box = scrolledtext.ScrolledText(root, wrap=tk.NONE, font=("Courier", 6))
    # text_box.pack(fill="both", expand=True)

    root.mainloop()


def main():
    if len(sys.argv) == 1:
        launch_gui()
    else:
        if len(sys.argv) < 3:
            print("Usage: python gif_to_ascii.py <image_path> <output_file> [width] [ascii_chars] [brightness] ["
                  "contrast]")
            sys.exit(1)

        image_path = sys.argv[1]
        output_file = sys.argv[2]
        new_width = int(sys.argv[3]) if len(sys.argv) > 3 else 80
        ascii_chars = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_ASCII_CHARS
        brightness = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
        contrast = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0

        originals, err = extract_frames(image_path)
        if err:
            print(err)
            sys.exit(1)
        frames = process_frames(originals, new_width, ascii_chars, brightness, contrast)

        with open(output_file, "w", encoding="utf-8") as f:
            for i, frame in enumerate(frames):
                f.write(f"-FRAME-\n")
                f.write(frame + "\n\n")

        print(f"Saved ASCII art to {output_file}")


if __name__ == "__main__":
    main()
