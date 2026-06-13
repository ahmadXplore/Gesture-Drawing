"""
Hand Detection Module v3.0
"""

import cv2
import mediapipe as mp
from config.settings import DETECTION_CONFIDENCE, TRACKING_CONFIDENCE, MAX_HANDS


def _load_mediapipe_solutions():
    try:
        return mp.solutions
    except AttributeError:
        import mediapipe.python.solutions as solutions
        return solutions


class HandDetector:

    def __init__(self):
        mp_solutions = _load_mediapipe_solutions()
        self.mp_hands = mp_solutions.hands
        self.mp_drawing = mp_solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_HANDS,
            min_detection_confidence=DETECTION_CONFIDENCE,
            min_tracking_confidence=TRACKING_CONFIDENCE,
        )

        self._lm_spec = self.mp_drawing.DrawingSpec(
            color=(0, 255, 120), thickness=1, circle_radius=2)
        self._con_spec = self.mp_drawing.DrawingSpec(
            color=(80, 180, 255), thickness=1)

    def find_hands(self, frame, draw=True):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        if results.multi_hand_landmarks and draw:
            for hl in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hl,
                    self.mp_hands.HAND_CONNECTIONS,
                    self._lm_spec, self._con_spec,
                )
        return frame, results

    def get_landmarks(self, results, frame_shape):
        out = []
        if results.multi_hand_landmarks:
            h, w, _ = frame_shape
            for hl in results.multi_hand_landmarks:
                lm = {}
                for i, l in enumerate(hl.landmark):
                    lm[i] = {'x': int(l.x * w), 'y': int(l.y * h), 'z': l.z}
                out.append(lm)
        return out

    def close(self):
        self.hands.close()
