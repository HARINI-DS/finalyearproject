from __future__ import annotations

import sys
import threading
import webbrowser
from pathlib import Path

import pystray
from PIL import Image, ImageDraw
from tkinter import Tk, Label

from backend.core.config import settings


class DesktopAIONButton:
    """Real Windows desktop floating AION button."""

    def __init__(self):
        self.root = Tk()
        self.root.title("AION")
        self.root.withdraw()
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.96)
        self.root.configure(bg="#0b1020")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-transparentcolor", "#0b1020")

        self._drag_data = {"x": 0, "y": 0}
        self._build_ui()
        self._position_bottom_right()
        self.root.protocol("WM_DELETE_WINDOW", self.hide)

    def _build_ui(self):
        frame = Label(
            self.root,
            text="AION",
            bg="#0f172a",
            fg="#dff7ff",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=16,
            pady=8,
            bd=0,
            cursor="hand2",
        )
        frame.pack(fill="both", expand=True)

        # subtle neon border
        self.root.config(highlightbackground="#5cc8ff", highlightthickness=1)

        frame.bind("<Button-1>", lambda event: self.open_assistant())
        frame.bind("<ButtonPress-1>", self._start_drag)
        frame.bind("<B1-Motion>", self._on_drag)

    def _position_bottom_right(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"+{max(0, screen_width - 130)}+{max(0, screen_height - 90)}")

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag(self, event):
        x = self.root.winfo_x() + (event.x - self._drag_data["x"])
        y = self.root.winfo_y() + (event.y - self._drag_data["y"])
        self.root.geometry(f"+{x}+{y}")

    def show(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)

    def hide(self):
        self.root.withdraw()

    def open_assistant(self):
        webbrowser.open(settings.frontend_url)


def _create_icon() -> Image.Image:
    image = Image.new("RGB", (64, 64), color=(12, 14, 18))
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 8, 56, 56), fill=(77, 201, 255), outline=(180, 240, 255), width=2)
    draw.ellipse((24, 24, 40, 40), fill=(12, 14, 18))
    return image


def launch_ui(icon: pystray.Icon, item):
    if hasattr(icon, "desktop_button"):
        icon.desktop_button.show()
    webbrowser.open(settings.frontend_url)


def quit_app(icon: pystray.Icon, item):
    if hasattr(icon, "desktop_button"):
        icon.desktop_button.hide()
    icon.stop()
    try:
        sys.exit(0)
    except SystemExit:
        pass


def run_tray() -> None:
    desktop_button = DesktopAIONButton()

    icon = pystray.Icon(
        "AION",
        _create_icon(),
        "AION",
        menu=pystray.Menu(
            pystray.MenuItem("Open Assistant", launch_ui),
            pystray.MenuItem("Quit", quit_app),
        ),
    )
    icon.desktop_button = desktop_button

    tray_thread = threading.Thread(target=icon.run, daemon=True)
    tray_thread.start()

    desktop_button.show()
    desktop_button.root.mainloop()


if __name__ == "__main__":
    run_tray()
