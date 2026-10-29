import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

from src.ui.camera_worker import CameraWorker

class VisionScrollApp:
    def __init__(self, root):
        self.root = root
        self.camera_worker = None
        self.camera_active = False
        self.current_image = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Window configuration
        self.root.title("VisionScroll")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        self.root.configure(bg="#101820")

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure(
            "TButton",
            font=("Segoe UI", 11),
            padding=10
        )

        self.style.configure(
            "Title.TLabel",
            background="#101820",
            foreground="#00D9A6",
            font=("Segoe UI", 26, "bold")
        )

        self.style.configure(
            "Subtitle.TLabel",
            background="#101820",
            foreground="#C7D1D9",
            font=("Segoe UI", 11)
        )

        # Build interface
        self.create_header()
        self.create_main_content()
        self.create_footer()

    def create_header(self):
        header = tk.Frame(self.root, bg="#101820")
        header.pack(fill="x", padx=30, pady=(25, 15))

        title = ttk.Label(
            header,
            text="VisionScroll",
            style="Title.TLabel"
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            header,
            text="Hands-free scrolling using hand gestures",
            style="Subtitle.TLabel"
        )
        subtitle.pack(anchor="w", pady=(5, 0))

    def create_main_content(self):
        content = tk.Frame(self.root, bg="#101820")
        content.pack(fill="both", expand=True, padx=30, pady=10)

        # Camera preview placeholder
        preview = tk.Frame(
            content,
            bg="#1B2836",
            highlightbackground="#34495E",
            highlightthickness=1
        )
        preview.pack(side="left", fill="both", expand=True, padx=(0, 15))

        self.preview_label = tk.Label(
            preview,
            text="Camera Preview\n\nCamera is currently stopped",
            bg="#1B2836",
            fg="#C7D1D9",
            font=("Segoe UI", 15),
            justify="center"
        )
        self.preview_label.pack(fill="both", expand=True, padx=15, pady=15)

        # Control panel
        controls = tk.Frame(
            content,
            bg="#1B2836",
            width=240,
            highlightbackground="#34495E",
            highlightthickness=1
        )
        controls.pack(side="right", fill="y")
        controls.pack_propagate(False)

        tk.Label(
            controls,
            text="CONTROLS",
            bg="#1B2836",
            fg="#00D9A6",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=20, pady=(25, 20))

        self.start_button = ttk.Button(
            controls,
            text="Start VisionScroll",
            command=self.start_app
        )
        self.start_button.pack(fill="x", padx=20, pady=8)

        self.stop_button = ttk.Button(
            controls,
            text="Stop VisionScroll",
            command=self.stop_app,
            state="disabled"
        )
        self.stop_button.pack(fill="x", padx=20, pady=8)

        tk.Label(
            controls,
            text="SYSTEM STATUS",
            bg="#1B2836",
            fg="#C7D1D9",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=20, pady=(30, 8))

        self.status_label = tk.Label(
            controls,
            text="● Stopped",
            bg="#1B2836",
            fg="#FF7070",
            font=("Segoe UI", 11)
        )
        self.status_label.pack(anchor="w", padx=20)

        tk.Label(
            controls,
            text="GESTURE",
            bg="#1B2836",
            fg="#C7D1D9",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=20, pady=(25, 8))

        self.gesture_label = tk.Label(
            controls,
            text="Inactive",
            bg="#1B2836",
            fg="#FFFFFF",
            font=("Segoe UI", 11)
        )
        self.gesture_label.pack(anchor="w", padx=20)

    def create_footer(self):
        footer = tk.Frame(self.root, bg="#101820")
        footer.pack(fill="x", padx=30, pady=(10, 20))

        tk.Label(
            footer,
            text="VisionScroll | Gesture-Controlled Scrolling",
            bg="#101820",
            fg="#8796A5",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

    def start_app(self):
        if self.camera_active:
            return

        self.start_button.config(state="disabled")
        self.status_label.config(
            text="● Starting camera...",
            fg="#FFC857"
        )

        try:
            self.camera_worker = CameraWorker()
            self.camera_worker.start()

            self.camera_active = True
            self.stop_button.config(state="normal")

            self.root.after(30, self.update_camera_frame)

        except Exception as exc:
            self.camera_active = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

            self.status_label.config(
                text="● Camera error",
                fg="#FF7070"
            )

            self.preview_label.config(
                text=f"Unable to start camera:\n{exc}"
            )

    def stop_app(self):
        self.camera_active = False

        if self.camera_worker is not None:
            self.camera_worker.stop()
            self.camera_worker = None

        self.current_image = None

        self.preview_label.config(
            image="",
            text="Camera Preview\n\nCamera is currently stopped"
        )

        self.status_label.config(
            text="● Stopped",
            fg="#FF7070"
        )

        self.gesture_label.config(text="Inactive")

        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def update_camera_frame(self):
        if not self.camera_active or self.camera_worker is None:
            return

        if self.camera_worker.error:
            self.status_label.config(
                text=f"Camera error: {self.camera_worker.error}"
            )
            self.stop_app()
            return

        frame = self.camera_worker.get_frame()

        if frame is not None:
            # Convert OpenCV BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the image for Tkinter
            image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(image=image)

            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo

        self.root.after(15, self.update_camera_frame)
    def on_close(self):
        self.stop_app()
        self.root.destroy()


def main():
    root = tk.Tk()
    VisionScrollApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
