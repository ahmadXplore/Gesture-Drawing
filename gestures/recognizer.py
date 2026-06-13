"""
Gesture Recognition Module v3.0
Pinch gesture removed (was unstable).
Gestures: DRAW | SELECT | CLEAR | NONE
"""

import math
from config.settings import (
    INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP, THUMB_TIP,
    INDEX_PIP, MIDDLE_PIP, RING_PIP, PINKY_PIP, THUMB_IP,
)


class GestureRecognizer:

    def __init__(self):
        self.previous_gesture = 'NONE'

    def recognize(self, landmarks: dict) -> str:
        """
        DRAW   — index finger only (1 finger up)
        SELECT — index + middle fingers (2 fingers up)
        CLEAR  — open palm (all 5 fingers up)
        NONE   — anything else
        """
        if not landmarks:
            return 'NONE'

        f = self._fingers_up(landmarks)

        if f == [0, 1, 0, 0, 0]:
            return 'DRAW'
        if f == [0, 1, 1, 0, 0]:
            return 'SELECT'
        if f == [1, 1, 1, 1, 1]:
            return 'CLEAR'
        return 'NONE'

    def get_drawing_point(self, landmarks: dict):
        if INDEX_TIP in landmarks:
            return (landmarks[INDEX_TIP]['x'], landmarks[INDEX_TIP]['y'])
        return None

    def get_selection_point(self, landmarks: dict):
        if INDEX_TIP in landmarks and MIDDLE_TIP in landmarks:
            x = (landmarks[INDEX_TIP]['x'] + landmarks[MIDDLE_TIP]['x']) // 2
            y = (landmarks[INDEX_TIP]['y'] + landmarks[MIDDLE_TIP]['y']) // 2
            return (x, y)
        return None

    def _fingers_up(self, lm: dict) -> list:
        fingers = []
        # Thumb (horizontal check for mirrored feed)
        fingers.append(1 if lm[THUMB_TIP]['x'] < lm[THUMB_IP]['x'] else 0)
        # Four fingers (vertical check)
        for tip, pip in zip(
            [INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP],
            [INDEX_PIP, MIDDLE_PIP, RING_PIP, PINKY_PIP]
        ):
            fingers.append(1 if lm[tip]['y'] < lm[pip]['y'] else 0)
        return fingers
