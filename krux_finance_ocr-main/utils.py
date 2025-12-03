import os
import numpy as np
from PIL import Image, ImageFont

def get_font(size, bold=False):
    """
    Returns a TrueType font object. 
    Attempts to load Arial (common on Windows) or falls back to default.
    """
    try:
        # Try common Windows fonts
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except IOError:
        try:
            # Fallback for Linux/Other
            font_name = "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"
            return ImageFont.truetype(font_name, size)
        except IOError:
            print(f"Warning: Could not load requested font. Using default.")
            return ImageFont.load_default()

def create_mock_qr(size=100):
    """Generates a random noise image resembling a QR code."""
    qr = np.random.randint(0, 2, (size, size)) * 255
    return Image.fromarray(qr.astype('uint8')).convert('RGB')

def ensure_dir(path):
    """Ensures a directory exists."""
    os.makedirs(path, exist_ok=True)
