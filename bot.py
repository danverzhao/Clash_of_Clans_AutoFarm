import cv2
import mss
import numpy as np
import pyautogui
import easyocr
import time
import os
import random

_reader = easyocr.Reader(["en"], gpu=True)

pyautogui.FAILSAFE = True  # Move mouse to top-left corner to stop the bot

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")

# How long to wait between actions (seconds)
DELAYS = {
    "after_click": 0.5,
    "find_match_wait": 10,   # seconds to wait for matchmaking
    "battle_check": 3,        # how often to check if battle ended
    "battle_timeout": 240,    # max battle duration (4 minutes)
}

# Where to deploy troops on screen — adjust these to your emulator window position
# These are percentage-based positions across the battlefield area
# You can tune these after watching the bot run once
DEPLOY_AREA = {
    "top":    (0.3, 0.15),
    "bottom": (0.3, 0.85),
    "left":   (0.05, 0.5),
    "right":  (0.95, 0.5),
}


# ─── OCR ─────────────────────────────────────────────────────────────────────

def read_number(top_left: tuple[int, int], bottom_right: tuple[int, int], frame: np.ndarray) -> int | None:
    """
    Crops the region defined by top_left and bottom_right from frame,
    reads the number inside it, and returns it as an int. Returns None if no number found.
    """
    x1, y1 = top_left
    x2, y2 = bottom_right
    region = frame[y1:y2, x1:x2]

    results = _reader.readtext(region, allowlist="0123456789")
    digits = "".join(text for _, text, _ in results)

    return int(digits) if digits else None


# ─── Image Matching ───────────────────────────────────────────────────────────

def find_in_image(template_path: str, haystack_path: str, threshold: float = 0.75) -> tuple[int, int] | None:
    """
    Check if the image at template_path exists inside the image at haystack_path.
    Returns the (x, y) midpoint of the match in haystack coordinates, or None if not found.
    """
    template = cv2.imread(template_path)
    haystack = cv2.imread(haystack_path)

    if template is None:
        raise FileNotFoundError(f"Template image not found: {template_path}")
    if haystack is None:
        raise FileNotFoundError(f"Haystack image not found: {haystack_path}")

    result = cv2.matchTemplate(haystack, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2
        return cx, cy

    return None


def screenshot() -> np.ndarray:
    with mss.mss() as sct:
        frame = np.array(sct.grab(sct.monitors[1]))
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)


def find_image(name: str, frame: np.ndarray = None, threshold: float = 0.75) -> tuple[int, int] | None:
    """Returns (x, y) center of the found image, or None.
    If frame is provided, searches within it. Otherwise takes a fresh screenshot."""
    path = os.path.join(IMAGES_DIR, f"{name}.png")
    if not os.path.exists(path):
        print(f"  [!] Missing image: {path}  — run capture_tool.py first")
        return None

    screen = frame if frame is not None else screenshot()
    template = cv2.imread(path)
    if template is None:
        print(f"  [!] Could not load image: {path}")
        return None

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2
        return cx, cy

    return None


def wait_for_image(name: str, timeout: float = 15, interval: float = 1) -> tuple[int, int] | None:
    """Wait until an image appears on screen, then return its position."""
    start = time.time()
    while time.time() - start < timeout:
        pos = find_image(name)
        if pos:
            return pos
        time.sleep(interval)
    print(f"  [!] Timed out waiting for '{name}'")
    return None


def click_image(name: str, timeout: float = 15) -> bool:
    """Find an image and click it. Returns True if successful."""
    print(f"  Looking for '{name}'...")
    pos = wait_for_image(name, timeout=timeout)
    if pos:
        pyautogui.click(pos[0], pos[1])
        print(f"  Clicked '{name}' at {pos}")
        time.sleep(DELAYS["after_click"])
        return True
    return False


# ─── Screen Dimensions ────────────────────────────────────────────────────────

def screen_size() -> tuple[int, int]:
    w, h = pyautogui.size()
    return w, h


def to_pixel(px: float, py: float) -> tuple[int, int]:
    """Convert 0.0–1.0 percentage to pixel coordinate."""
    w, h = screen_size()
    return int(w * px), int(h * py)


