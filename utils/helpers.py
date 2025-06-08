import pandas as pd
import sys
import os

def get_theme_colors(theme):
    return {
        "dark": {
            "bg": "#1e1f29",
            "fg": "white",
            "card": "#2c2f3a",
            "card_hover": "#3b3e4c",
            "success": "#2ecc71",
            "error": "#e74c3c",
            "button": "#3498db",
            "shadow": "#15161e",
            "accent": "#2980b9",
            "question_bg": "#1a1b25",
            "timer_bg": "#1c2c1c",
            "timer_fg": "#2ecc71"
        }
    }

def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1+radius, y1, x2-radius, y1, x2, y1,
        x2, y1+radius, x2, y2-radius, x2, y2,
        x2-radius, y2, x1+radius, y2, x1, y2,
        x1, y2-radius, x1, y1+radius, x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

def resource_path(rel_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    # Determine base path: if running under PyInstaller, use _MEIPASS;
    # otherwise, use project root (parent of utils directory)
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # file is in <project_root>/utils/helpers.py
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    return os.path.join(base_path, rel_path)   