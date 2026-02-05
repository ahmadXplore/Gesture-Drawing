"""
UI Module
Manages the user interface (color palette, controls, info display)
"""

import cv2
import numpy as np
import time
from config.settings import (
    COLORS, UI_HEIGHT, UI_BACKGROUND_COLOR, UI_TEXT_COLOR,
    UI_BUTTON_SIZE, UI_BUTTON_MARGIN, CANVAS_WIDTH, CANVAS_HEIGHT,
    HOVER_TIME
)


class UIManager:
    """Manages the user interface"""

    def __init__(self):
        self.ui_height = UI_HEIGHT
        self.button_size = UI_BUTTON_SIZE
        self.button_margin = UI_BUTTON_MARGIN

        # UI at the top
        self.ui_y_start = 10

        # Create color buttons (top row)
        self.color_buttons = self._create_color_buttons()

        # Eraser button (right after colors)
        num_colors = len(COLORS)
        self.eraser_button = {
            'name': 'ERASER',
            'x': 20 + num_colors * (self.button_size + self.button_margin),
            'y': self.ui_y_start,
            'width': self.button_size + 20,
            'height': self.button_size,
            'color': (60, 60, 60)
        }

        # Brush size buttons (below colors)
        self.brush_up_button = {
            'name': 'BRUSH+',
            'x': 20,
            'y': self.ui_y_start + self.button_size + 10,
            'width': 100,
            'height': 35,
            'color': (50, 200, 50)
        }

        self.brush_down_button = {
            'name': 'BRUSH-',
            'x': 130,
            'y': self.ui_y_start + self.button_size + 10,
            'width': 100,
            'height': 35,
            'color': (200, 50, 50)
        }

        # Action buttons
        self.clear_button = {
            'name': 'CLEAR',
            'x': CANVAS_WIDTH - 280,
            'y': self.ui_y_start + self.button_size + 10,
            'width': 120,
            'height': 35,
            'color': (100, 100, 100)
        }

        self.save_button = {
            'name': 'SAVE',
            'x': CANVAS_WIDTH - 150,
            'y': self.ui_y_start + self.button_size + 10,
            'width': 120,
            'height': 35,
            'color': (50, 150, 50)
        }

        # Hover tracking
        self.hover_start_time = None
        self.current_hover_button = None
        self.last_activated_button = None
        self.activation_cooldown = 0.3  # Prevent rapid activation
        self.last_activation_time = 0

        self.selected_color = None

    def _create_color_buttons(self):
        """Create color palette buttons"""
        buttons = []
        x_start = 20
        y_start = self.ui_y_start

        for idx, (color_name, color_bgr) in enumerate(COLORS.items()):
            button = {
                'name': color_name,
                'x': x_start + idx * (self.button_size + self.button_margin),
                'y': y_start,
                'width': self.button_size,
                'height': self.button_size,
                'color': color_bgr
            }
            buttons.append(button)

        return buttons

    def draw_ui(self, frame, current_color, brush_size, current_mode, gesture, eraser_mode=False):
        """
        Draw the UI on the frame
        
        Args:
            frame: The frame to draw UI on
            current_color: Current drawing color (BGR tuple)
            brush_size: Current brush size
            current_mode: Current mode string ('DRAW', 'SELECT', etc.)
            gesture: Current gesture being performed
            eraser_mode: Whether eraser is active
        """
        # Create semi-transparent UI panel at top
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (0, 0),
            (CANVAS_WIDTH, UI_HEIGHT),
            UI_BACKGROUND_COLOR,
            -1
        )
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Draw color buttons
        for button in self.color_buttons:
            cv2.rectangle(
                frame,
                (button['x'], button['y']),
                (button['x'] + button['width'],
                 button['y'] + button['height']),
                button['color'],
                -1
            )

            # Add border
            border_color = (200, 200, 200)
            # Dim colors if eraser is active
            if eraser_mode:
                border_color = (100, 100, 100)

            cv2.rectangle(
                frame,
                (button['x'], button['y']),
                (button['x'] + button['width'],
                 button['y'] + button['height']),
                border_color,
                2
            )

            # Highlight selected color (only if not in eraser mode)
            if button['color'] == current_color and not eraser_mode:
                cv2.rectangle(
                    frame,
                    (button['x'] - 4, button['y'] - 4),
                    (button['x'] + button['width'] + 4,
                     button['y'] + button['height'] + 4),
                    (255, 255, 255),
                    4
                )

        # Draw eraser button
        cv2.rectangle(
            frame,
            (self.eraser_button['x'], self.eraser_button['y']),
            (self.eraser_button['x'] + self.eraser_button['width'],
             self.eraser_button['y'] + self.eraser_button['height']),
            self.eraser_button['color'],
            -1
        )

        # Eraser icon (simple crossed lines)
        icon_x = self.eraser_button['x'] + self.eraser_button['width'] // 2
        icon_y = self.eraser_button['y'] + self.eraser_button['height'] // 2
        icon_size = 15
        cv2.line(frame,
                 (icon_x - icon_size, icon_y - icon_size),
                 (icon_x + icon_size, icon_y + icon_size),
                 (200, 200, 200), 3)
        cv2.line(frame,
                 (icon_x + icon_size, icon_y - icon_size),
                 (icon_x - icon_size, icon_y + icon_size),
                 (200, 200, 200), 3)

        # Highlight if eraser is active
        if eraser_mode:
            cv2.rectangle(
                frame,
                (self.eraser_button['x'] - 4, self.eraser_button['y'] - 4),
                (self.eraser_button['x'] + self.eraser_button['width'] + 4,
                 self.eraser_button['y'] + self.eraser_button['height'] + 4),
                (0, 255, 255),  # Cyan highlight for eraser
                4
            )
        else:
            cv2.rectangle(
                frame,
                (self.eraser_button['x'], self.eraser_button['y']),
                (self.eraser_button['x'] + self.eraser_button['width'],
                 self.eraser_button['y'] + self.eraser_button['height']),
                (200, 200, 200),
                2
            )

        # Draw brush size buttons with hover effect
        self._draw_button_with_hover(frame, self.brush_up_button)
        cv2.putText(
            frame,
            'BRUSH +',
            (self.brush_up_button['x'] + 10, self.brush_up_button['y'] + 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            UI_TEXT_COLOR,
            2
        )

        self._draw_button_with_hover(frame, self.brush_down_button)
        cv2.putText(
            frame,
            'BRUSH -',
            (self.brush_down_button['x'] + 10,
             self.brush_down_button['y'] + 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            UI_TEXT_COLOR,
            2
        )

        # Display current brush size
        cv2.putText(
            frame,
            f'Size: {brush_size}',
            (250, self.ui_y_start + self.button_size + 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            UI_TEXT_COLOR,
            2
        )

        # Draw brush size preview circle
        preview_x = 370
        preview_y = self.ui_y_start + self.button_size + 27
        preview_color = (255, 255, 255) if eraser_mode else current_color
        preview_size = brush_size * 2 if eraser_mode else brush_size

        cv2.circle(frame, (preview_x, preview_y),
                   preview_size, preview_color, -1)
        cv2.circle(frame, (preview_x, preview_y),
                   preview_size, (150, 150, 150), 1)

        # Show "ERASER" text next to preview if active
        if eraser_mode:
            cv2.putText(
                frame,
                'ERASER',
                (preview_x + 30, preview_y + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )

        # Draw action buttons
        self._draw_button_with_hover(frame, self.clear_button)
        cv2.putText(
            frame,
            'CLEAR',
            (self.clear_button['x'] + 25, self.clear_button['y'] + 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            UI_TEXT_COLOR,
            2
        )

        self._draw_button_with_hover(frame, self.save_button)
        cv2.putText(
            frame,
            'SAVE',
            (self.save_button['x'] + 30, self.save_button['y'] + 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            UI_TEXT_COLOR,
            2
        )

        # Display current mode and gesture at bottom
        mode_y = CANVAS_HEIGHT - 60
        cv2.putText(
            frame,
            f'Mode: {current_mode}',
            (20, mode_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f'Gesture: {gesture}',
            (20, mode_y + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        # Instructions at bottom
        instructions = "1 finger = DRAW/ERASE | 2 fingers = SELECT (hover: colors, eraser, +/-) | Open palm = CLEAR"
        cv2.putText(
            frame,
            instructions,
            (CANVAS_WIDTH // 2 - 400, CANVAS_HEIGHT - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1
        )

        return frame

    def _draw_button_with_hover(self, frame, button):
        """Draw button with hover progress indicator"""
        # Base button
        cv2.rectangle(
            frame,
            (button['x'], button['y']),
            (button['x'] + button['width'], button['y'] + button['height']),
            button['color'],
            -1
        )

        # Border
        cv2.rectangle(
            frame,
            (button['x'], button['y']),
            (button['x'] + button['width'], button['y'] + button['height']),
            (200, 200, 200),
            2
        )

        # Draw hover progress bar if this button is being hovered
        if self.current_hover_button == button['name'] and self.hover_start_time:
            hover_duration = time.time() - self.hover_start_time
            progress = min(hover_duration / HOVER_TIME, 1.0)

            # Progress bar at bottom of button
            bar_width = int(button['width'] * progress)
            cv2.rectangle(
                frame,
                (button['x'], button['y'] + button['height'] - 5),
                (button['x'] + bar_width, button['y'] + button['height']),
                (0, 255, 0),
                -1
            )

    def check_hover_activation(self, point):
        """
        Check if a point is hovering over a button and track hover time
        
        Args:
            point: Tuple (x, y) of the selection point
            
        Returns:
            Dictionary with 'type' and 'value' if activated, else None
        """
        if point is None:
            self.hover_start_time = None
            self.current_hover_button = None
            return None

        x, y = point
        current_time = time.time()

        # Check if enough time has passed since last activation
        if current_time - self.last_activation_time < self.activation_cooldown:
            return None

        # Find which button is being hovered
        hovered_button = None
        hovered_action = None

        # Check color buttons
        for button in self.color_buttons:
            if self._is_point_in_button(point, button):
                hovered_button = button['name']
                hovered_action = {'type': 'color', 'value': button['name']}
                break

        # Check eraser button
        if not hovered_button:
            if self._is_point_in_button(point, self.eraser_button):
                hovered_button = 'ERASER'
                hovered_action = {'type': 'tool', 'value': 'eraser'}

        # Check brush size buttons
        if not hovered_button:
            if self._is_point_in_button(point, self.brush_up_button):
                hovered_button = 'BRUSH+'
                hovered_action = {'type': 'brush', 'value': 'increase'}
            elif self._is_point_in_button(point, self.brush_down_button):
                hovered_button = 'BRUSH-'
                hovered_action = {'type': 'brush', 'value': 'decrease'}
            elif self._is_point_in_button(point, self.clear_button):
                hovered_button = 'CLEAR'
                hovered_action = {'type': 'action', 'value': 'clear'}
            elif self._is_point_in_button(point, self.save_button):
                hovered_button = 'SAVE'
                hovered_action = {'type': 'action', 'value': 'save'}

        # Track hover time
        if hovered_button:
            if self.current_hover_button != hovered_button:
                # Started hovering over a new button
                self.hover_start_time = current_time
                self.current_hover_button = hovered_button
            else:
                # Still hovering over same button
                hover_duration = current_time - self.hover_start_time

                # Check if hover time exceeded threshold
                if hover_duration >= HOVER_TIME:
                    # Activate the button
                    self.hover_start_time = None
                    self.current_hover_button = None
                    self.last_activated_button = hovered_button
                    self.last_activation_time = current_time
                    return hovered_action
        else:
            # Not hovering over any button
            self.hover_start_time = None
            self.current_hover_button = None

        return None

    def _is_point_in_button(self, point, button):
        """Check if point is inside button bounds"""
        x, y = point
        return (button['x'] <= x <= button['x'] + button['width'] and
                button['y'] <= y <= button['y'] + button['height'])

    def check_button_click(self, point):
        """
        Legacy method - now uses hover activation instead
        Use check_hover_activation() for better UX
        """
        return self.check_hover_activation(point)
