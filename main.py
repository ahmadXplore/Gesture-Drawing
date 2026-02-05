"""
Main Application File
Gesture-Based Drawing Application
"""

from ui.manager import UIManager
from gestures.recognizer import GestureRecognizer
from utils.canvas import Canvas
from utils.hand_detector import HandDetector
from config.settings import (
    CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_INDEX,
    SHOW_FPS, FPS_POSITION, FPS_COLOR,
    CANVAS_WIDTH, CANVAS_HEIGHT
)
import cv2
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class GestureDrawingApp:
    """Main application class"""

    def __init__(self):
        print("🚀 Initializing Gesture Drawing Application...")

        # Initialize components
        self.hand_detector = HandDetector()
        self.canvas = Canvas()
        self.gesture_recognizer = GestureRecognizer()
        self.ui_manager = UIManager()

        # Camera setup
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

        # Application state
        self.running = True
        self.current_mode = 'NONE'
        self.current_gesture = 'NONE'
        self.previous_gesture = 'NONE'

        # FPS calculation
        self.prev_time = 0

        # Debouncing for button clicks
        self.last_click_time = 0
        self.click_cooldown = 0.5  # seconds

        print("✅ Application initialized successfully!")
        print("\n" + "="*60)
        print("GESTURE CONTROLS:")
        print("="*60)
        print("👆 ONE FINGER (Index)     → DRAW/ERASE MODE")
        print("✌️  TWO FINGERS (Index+Middle) → SELECT MODE")
        print("   - Hover over colors to change color")
        print("   - Hover over ERASER to toggle eraser")
        print("   - Hover over BRUSH+/- to adjust size")
        print("🖐️  OPEN PALM (All fingers)    → CLEAR CANVAS")
        print("="*60)
        print("Press 'q' to quit | Press 's' to save | Press 'c' to clear\n")

    def run(self):
        """Main application loop"""

        while self.running:
            # Read frame
            success, frame = self.cap.read()
            if not success:
                print("❌ Failed to read frame from camera")
                break

            # Flip for mirror effect
            frame = cv2.flip(frame, 1)

            # Detect hands
            frame, results = self.hand_detector.find_hands(frame, draw=True)

            # Get landmarks
            landmarks_list = self.hand_detector.get_landmarks(
                results, frame.shape)

            # Process gestures if hand detected
            if landmarks_list:
                landmarks = landmarks_list[0]  # Use first hand

                # Recognize gesture
                self.current_gesture = self.gesture_recognizer.recognize(
                    landmarks)

                # Handle gesture
                self._handle_gesture(landmarks)
            else:
                self.current_gesture = 'NONE'
                self.current_mode = 'NONE'
                self.canvas.reset_previous_point()

            # Combine canvas with frame
            canvas_view = self.canvas.get_canvas()

            # Blend canvas with frame (make frame semi-transparent)
            frame_with_canvas = cv2.addWeighted(
                frame, 0.5, canvas_view, 0.8, 0)

            # Draw UI
            frame_with_canvas = self.ui_manager.draw_ui(
                frame_with_canvas,
                self.canvas.current_color,
                self.canvas.brush_size,
                self.current_mode,
                self.current_gesture,
                self.canvas.eraser_mode
            )

            # Calculate and display FPS
            if SHOW_FPS:
                current_time = time.time()
                fps = 1 / (current_time -
                           self.prev_time) if self.prev_time else 0
                self.prev_time = current_time

                cv2.putText(
                    frame_with_canvas,
                    f'FPS: {int(fps)}',
                    FPS_POSITION,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    FPS_COLOR,
                    2
                )

            # Show frame
            cv2.imshow("Gesture Drawing Application", frame_with_canvas)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
            elif key == ord('s'):
                self._save_drawing()
            elif key == ord('c'):
                self.canvas.clear()
                print("🗑️  Canvas cleared")

            self.previous_gesture = self.current_gesture

        # Cleanup
        self.cleanup()

    def _handle_gesture(self, landmarks):
        """
        Handle the recognized gesture
        
        Args:
            landmarks: Hand landmarks dictionary
        """
        current_time = time.time()

        if self.current_gesture == 'DRAW':
            self.current_mode = 'DRAWING'
            point = self.gesture_recognizer.get_drawing_point(landmarks)
            self.canvas.draw(point)

        elif self.current_gesture == 'SELECT':
            self.current_mode = 'SELECTION'
            self.canvas.reset_previous_point()

            # Check if hovering over a UI button
            point = self.gesture_recognizer.get_selection_point(landmarks)

            # Use hover activation (no cooldown needed, it's built into UI manager)
            button_action = self.ui_manager.check_hover_activation(point)

            if button_action:
                self._handle_button_action(button_action)

        elif self.current_gesture == 'CLEAR':
            # Only clear once per gesture (not continuously)
            if self.previous_gesture != 'CLEAR':
                self.canvas.clear()
                self.current_mode = 'CLEAR'
                print("🗑️  Canvas cleared by gesture!")

        else:
            self.current_mode = 'NONE'
            self.canvas.reset_previous_point()

    def _handle_button_action(self, action):
        """
        Handle button clicks from UI
        
        Args:
            action: Dictionary with 'type' and 'value'
        """
        if action['type'] == 'color':
            self.canvas.set_color(action['value'])
            # Turn off eraser when selecting color
            self.canvas.set_eraser_mode(False)
            print(f"🎨 Color changed to: {action['value']}")

        elif action['type'] == 'tool':
            if action['value'] == 'eraser':
                self.canvas.toggle_eraser()
                status = "ON" if self.canvas.eraser_mode else "OFF"
                print(f"🧹 Eraser: {status}")

        elif action['type'] == 'action':
            if action['value'] == 'clear':
                self.canvas.clear()
                print("🗑️  Canvas cleared")
            elif action['value'] == 'save':
                self._save_drawing()

        elif action['type'] == 'brush':
            if action['value'] == 'increase':
                self.canvas.increase_brush_size()
                print(f"🖌️  Brush size: {self.canvas.brush_size}")
            elif action['value'] == 'decrease':
                self.canvas.decrease_brush_size()
                print(f"🖌️  Brush size: {self.canvas.brush_size}")

    def _save_drawing(self):
        """Save the current drawing"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"drawing_{timestamp}.png"
        self.canvas.save_canvas(filename)
        print(f"💾 Drawing saved as: {filename}")

    def cleanup(self):
        """Clean up resources"""
        print("\n🛑 Shutting down application...")
        self.cap.release()
        cv2.destroyAllWindows()
        self.hand_detector.close()
        print("✅ Application closed successfully!")


def main():
    """Entry point"""
    try:
        app = GestureDrawingApp()
        app.run()
    except KeyboardInterrupt:
        print("\n⚠️  Application interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
