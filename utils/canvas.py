"""
Canvas Module
Manages the drawing canvas and drawing operations
"""

import cv2
import numpy as np
from config.settings import (
    CANVAS_WIDTH, CANVAS_HEIGHT, COLORS, DEFAULT_COLOR,
    DEFAULT_BRUSH_SIZE, MIN_BRUSH_SIZE, MAX_BRUSH_SIZE,
    SMOOTHING_FACTOR
)


class Canvas:
    """Manages the drawing canvas"""

    def __init__(self):
        # Create blank canvas
        self.canvas = np.zeros(
            (CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8)

        # Drawing state
        self.current_color = COLORS[DEFAULT_COLOR]
        self.brush_size = DEFAULT_BRUSH_SIZE
        self.is_drawing = False
        self.previous_point = None
        self.eraser_mode = False  # Track if eraser is active

        # History for undo functionality (optional)
        self.canvas_history = []

    def clear(self):
        """Clear the canvas"""
        self.canvas = np.zeros(
            (CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8)
        self.previous_point = None
        self.canvas_history.append(self.canvas.copy())

    def draw(self, point):
        """
        Draw on the canvas (or erase if in eraser mode)
        
        Args:
            point: Tuple (x, y) of the drawing point
        """
        if point is None:
            self.previous_point = None
            return

        x, y = point

        # Choose color based on mode
        draw_color = (0, 0, 0) if self.eraser_mode else self.current_color

        # Draw line from previous point to current point for smooth lines
        if self.previous_point is not None:
            cv2.line(
                self.canvas,
                self.previous_point,
                (x, y),
                draw_color,
                self.brush_size if not self.eraser_mode else self.brush_size * 2
            )
        else:
            # Draw circle if no previous point
            cv2.circle(
                self.canvas,
                (x, y),
                self.brush_size if not self.eraser_mode else self.brush_size * 2,
                draw_color,
                -1
            )

        self.previous_point = (x, y)

    def toggle_eraser(self):
        """Toggle eraser mode on/off"""
        self.eraser_mode = not self.eraser_mode
        return self.eraser_mode

    def set_eraser_mode(self, enabled):
        """Set eraser mode explicitly"""
        self.eraser_mode = enabled

    def set_color(self, color_name):
        """
        Set the drawing color
        
        Args:
            color_name: String name of the color from COLORS dict
        """
        if color_name in COLORS:
            self.current_color = COLORS[color_name]

    def set_brush_size(self, size):
        """
        Set the brush size
        
        Args:
            size: Integer brush size
        """
        self.brush_size = max(MIN_BRUSH_SIZE, min(MAX_BRUSH_SIZE, size))

    def increase_brush_size(self):
        """Increase brush size by 1"""
        self.brush_size = min(MAX_BRUSH_SIZE, self.brush_size + 1)

    def decrease_brush_size(self):
        """Decrease brush size by 1"""
        self.brush_size = max(MIN_BRUSH_SIZE, self.brush_size - 1)

    def get_canvas(self):
        """Get the current canvas"""
        return self.canvas

    def reset_previous_point(self):
        """Reset the previous point (call when switching modes)"""
        self.previous_point = None

    def save_canvas(self, filename='drawing.png'):
        """
        Save the canvas to a file
        
        Args:
            filename: Name of the file to save
        """
        cv2.imwrite(filename, self.canvas)
        return filename
