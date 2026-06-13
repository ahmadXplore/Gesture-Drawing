"""
Gesture Drawing Application v4.0
=================================
Changes from v2:
  ✅ Pinch gesture REMOVED (was unstable)
  ✅ Black color fixed (white canvas background)
  ✅ Catmull-Rom spline smoothing — visibly silkier strokes
  ✅ 18 colors (was 10)
  ✅ 8 shape modes: FREE LINE RECT CIRCLE ELLIPSE TRIANGLE ARROW STAR
  ✅ Cleaner HUD layout (2-row color palette)
"""

from ui.manager import UIManager
from gestures.recognizer import GestureRecognizer
from utils.canvas import Canvas
from utils.hand_detector import HandDetector
from config.settings import (
    CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_INDEX,
    SHOW_FPS, FPS_POSITION, FPS_COLOR,
    CANVAS_WIDTH, CANVAS_HEIGHT, PARTICLE_TRAIL,
)
import cv2
import time
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PY = None
venv_dir = os.path.join(ROOT_DIR, 'venv')
if os.path.isdir(venv_dir):
    candidate = os.path.join(venv_dir, 'Scripts', 'python.exe')
    if os.path.isfile(candidate):
        VENV_PY = candidate
    else:
        candidate = os.path.join(venv_dir, 'bin', 'python')
        if os.path.isfile(candidate):
            VENV_PY = candidate

if VENV_PY is not None:
    current_python = os.path.abspath(sys.executable)
    expected_python = os.path.abspath(VENV_PY)
    if os.path.normcase(current_python) != os.path.normcase(expected_python):
        print('⚠️  Detected local virtual environment for this project:')
        print(f'    {expected_python}')
        print('    Re-launching with the local venv so MediaPipe imports work reliably.')
        os.execv(expected_python, [expected_python] + sys.argv)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class GestureDrawingApp:

    def __init__(self):
        print("🚀  Gesture Drawing v4.0 — starting …")

        self.hand_detector = HandDetector()
        self.canvas = Canvas()
        self.gesture_recognizer = GestureRecognizer()
        self.ui_manager = UIManager()

        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)   # low-latency capture

        self.running = True
        self.current_mode = 'NONE'
        self.current_gesture = 'NONE'
        self.previous_gesture = 'NONE'

        self.prev_time = 0.0
        self._fps_smooth = 30.0

        self._print_controls()

    # ── main loop ─────────────────────────────────────────────────────────────

    def run(self):
        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                print("❌  Camera read failed")
                break

            frame = cv2.flip(frame, 1)
            frame, results = self.hand_detector.find_hands(frame, draw=True)
            lm_list = self.hand_detector.get_landmarks(results, frame.shape)

            if lm_list:
                lm = lm_list[0]
                self.current_gesture = self.gesture_recognizer.recognize(lm)
                self._handle_gesture(lm)
            else:
                self.current_gesture = 'NONE'
                self.current_mode = 'NONE'
                self.canvas.reset_previous_point()

            # Blend canvas onto camera frame
            canvas_view = self.canvas.get_canvas()
            composite = cv2.addWeighted(frame, 0.30, canvas_view, 0.92, 0)

            # Draw HUD
            composite = self.ui_manager.draw_ui(
                composite,
                self.canvas.current_color,
                self.canvas.brush_size,
                self.current_mode,
                self.current_gesture,
                eraser_mode=self.canvas.eraser_mode,
                draw_mode=self.canvas.draw_mode,
                opacity=self.canvas.opacity,
                trail=self.canvas.trail if PARTICLE_TRAIL else None,
            )

            # FPS counter
            if SHOW_FPS:
                now = time.time()
                fps = 1.0 / (now - self.prev_time) if self.prev_time else 30.0
                self._fps_smooth = 0.88 * self._fps_smooth + 0.12 * fps
                self.prev_time = now
                cv2.putText(composite, f'FPS {int(self._fps_smooth)}',
                            FPS_POSITION, cv2.FONT_HERSHEY_SIMPLEX,
                            0.65, FPS_COLOR, 2, cv2.LINE_AA)

            cv2.imshow("✋  Gesture Drawing v4.0", composite)

            # Keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
            elif key == ord('s'):
                self._save()
            elif key == ord('c'):
                self.canvas.clear()
                print("🗑️  Cleared")
            elif key in (ord('z'), 26):
                if self.canvas.undo():
                    print("↩️  Undo")
            elif key in (ord('y'), 25):
                if self.canvas.redo():
                    print("↪️  Redo")
            elif key == ord('1'):
                self.canvas.set_draw_mode('FREE')
            elif key == ord('2'):
                self.canvas.set_draw_mode('LINE')
            elif key == ord('3'):
                self.canvas.set_draw_mode('RECT')
            elif key == ord('4'):
                self.canvas.set_draw_mode('CIRCLE')
            elif key == ord('5'):
                self.canvas.set_draw_mode('ELLIPSE')
            elif key == ord('6'):
                self.canvas.set_draw_mode('TRIANGLE')
            elif key == ord('7'):
                self.canvas.set_draw_mode('ARROW')
            elif key == ord('8'):
                self.canvas.set_draw_mode('STAR')

            self.previous_gesture = self.current_gesture

        self.cleanup()

    # ── gesture handling ──────────────────────────────────────────────────────

    def _handle_gesture(self, lm: dict):
        g = self.current_gesture

        if g == 'DRAW':
            self.current_mode = 'ERASING' if self.canvas.eraser_mode else 'DRAWING'
            self.canvas.draw(self.gesture_recognizer.get_drawing_point(lm))

        elif g == 'SELECT':
            self.current_mode = 'SELECT'
            if self.previous_gesture == 'DRAW':
                self.canvas.reset_previous_point()
            pt = self.gesture_recognizer.get_selection_point(lm)
            action = self.ui_manager.check_hover_activation(pt)
            if action:
                self._handle_action(action)

        elif g == 'CLEAR':
            if self.previous_gesture != 'CLEAR':
                self.canvas.clear()
                self.current_mode = 'CLEAR'
                print("🗑️  Cleared by gesture")

        else:
            self.current_mode = 'NONE'
            if self.previous_gesture == 'DRAW':
                self.canvas.reset_previous_point()

    def _handle_action(self, action: dict):
        t, v = action['type'], action['value']

        if t == 'color':
            self.canvas.set_color(v)
            print(f"🎨  {v}")
        elif t == 'tool' and v == 'eraser':
            on = self.canvas.toggle_eraser()
            print(f"🧹  Eraser {'ON' if on else 'OFF'}")
        elif t == 'brush' and v == 'increase':
            self.canvas.increase_brush_size()
            print(f"🖌️  {self.canvas.brush_size}")
        elif t == 'brush' and v == 'decrease':
            self.canvas.decrease_brush_size()
            print(f"🖌️  {self.canvas.brush_size}")
        elif t == 'opacity' and v == 'increase':
            self.canvas.increase_opacity()
        elif t == 'opacity' and v == 'decrease':
            self.canvas.decrease_opacity()
        elif t == 'mode':
            self.canvas.set_draw_mode(v)
            print(f"✏️  {v}")
        elif t == 'action':
            if v == 'clear':
                self.canvas.clear()
                print("🗑️  Cleared")
            elif v == 'save':
                self._save()
            elif v == 'undo':
                if self.canvas.undo():
                    print("↩️  Undo")
            elif v == 'redo':
                if self.canvas.redo():
                    print("↪️  Redo")

    # ── helpers ───────────────────────────────────────────────────────────────

    def _save(self):
        fn = f"drawing_{time.strftime('%Y%m%d_%H%M%S')}.png"
        self.canvas.save_canvas(fn)
        print(f"💾  Saved → {fn}")

    def cleanup(self):
        print("\n🛑  Shutting down …")
        self.cap.release()
        cv2.destroyAllWindows()
        self.hand_detector.close()
        print("✅  Done")

    def _print_controls(self):
        print("\n" + "═"*64)
        print("  GESTURE DRAWING v4.0")
        print("═"*64)
        print("  👆  1 finger   → DRAW / ERASE")
        print("  ✌️   2 fingers  → SELECT  (hover a button for 0.65 s)")
        print("  🖐️   Open palm  → CLEAR canvas")
        print("─"*64)
        print("  z=Undo   y=Redo   s=Save   c=Clear   q=Quit")
        print("  1=Free  2=Line  3=Rect  4=Circle  5=Ellipse")
        print("  6=Triangle  7=Arrow  8=Star")
        print("═"*64 + "\n")


def main():
    try:
        GestureDrawingApp().run()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")
    except Exception as e:
        print(f"❌  {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
