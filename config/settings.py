"""
Configuration file for Gesture Drawing Application
Contains all constants, colors, and settings
"""

# Camera Settings
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_INDEX = 0

# MediaPipe Hand Detection Settings
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.7
MAX_HANDS = 1

# Canvas Settings
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 720

# Drawing Settings
DEFAULT_BRUSH_SIZE = 5
MIN_BRUSH_SIZE = 1
MAX_BRUSH_SIZE = 50
BRUSH_SIZE_STEP = 1  # Increment/decrement by 1

# Colors (BGR format for OpenCV)
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'RED': (0, 0, 255),
    'GREEN': (0, 255, 0),
    'BLUE': (255, 0, 0),
    'YELLOW': (0, 255, 255),
    'CYAN': (255, 255, 0),
    'MAGENTA': (255, 0, 255),
    'ORANGE': (0, 165, 255),
    'PURPLE': (128, 0, 128),
}

DEFAULT_COLOR = 'BLUE'

# UI Settings
UI_HEIGHT = 100
UI_POSITION = 'top'  # 'top' or 'bottom'
UI_BACKGROUND_COLOR = (50, 50, 50)
UI_TEXT_COLOR = (255, 255, 255)
UI_BUTTON_SIZE = 60
UI_BUTTON_MARGIN = 10
HOVER_TIME = 0.8  # Seconds to hover over button to activate

# Gesture Thresholds
FINGER_TIP_THRESHOLD = 0.1  # Distance threshold for finger tip detection
PINCH_THRESHOLD = 40  # Pixel distance for pinch gesture
SMOOTHING_FACTOR = 0.5  # For smoothing drawing lines

# FPS Display
SHOW_FPS = True
FPS_POSITION = (10, 30)
FPS_COLOR = (0, 255, 0)

# Landmark indices (MediaPipe hand landmarks)
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20

THUMB_IP = 3
INDEX_PIP = 6
MIDDLE_PIP = 10
RING_PIP = 14
PINKY_PIP = 18

WRIST = 0
