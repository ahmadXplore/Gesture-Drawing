"""
Gesture Recognition Module
Recognizes different hand gestures for drawing actions
"""

import math
from config.settings import (
    INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP, THUMB_TIP,
    INDEX_PIP, MIDDLE_PIP, RING_PIP, PINKY_PIP, THUMB_IP,
    PINCH_THRESHOLD
)


class GestureRecognizer:
    """Recognizes hand gestures from landmarks"""

    def __init__(self):
        self.previous_gesture = None

    def recognize(self, landmarks):
        """
        Recognize gesture from hand landmarks
        
        Args:
            landmarks: Dictionary of landmark positions
            
        Returns:
            String representing the gesture:
            - 'DRAW': One finger up (index)
            - 'SELECT': Two fingers up (index + middle)
            - 'CLEAR': Open palm (all fingers up)
            - 'NONE': No recognized gesture
        """
        if not landmarks:
            return 'NONE'

        fingers_up = self._count_fingers_up(landmarks)

        # Check finger count gestures
        if fingers_up == [0, 1, 0, 0, 0]:  # Only index finger up
            return 'DRAW'

        elif fingers_up == [0, 1, 1, 0, 0]:  # Index and middle fingers up
            return 'SELECT'

        elif fingers_up == [1, 1, 1, 1, 1]:  # All fingers up (open palm)
            return 'CLEAR'

        return 'NONE'

    def _count_fingers_up(self, landmarks):
        """
        Count which fingers are extended
        
        Returns:
            List of 5 binary values [thumb, index, middle, ring, pinky]
            1 = finger up, 0 = finger down
        """
        fingers = []

        # Thumb (special case - check horizontal distance)
        if landmarks[THUMB_TIP]['x'] < landmarks[THUMB_IP]['x']:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other fingers (check if tip is above PIP joint)
        tip_ids = [INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]
        pip_ids = [INDEX_PIP, MIDDLE_PIP, RING_PIP, PINKY_PIP]

        for tip_id, pip_id in zip(tip_ids, pip_ids):
            if landmarks[tip_id]['y'] < landmarks[pip_id]['y']:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def _is_pinching(self, landmarks):
        """
        Check if thumb and index finger are pinching
        
        Args:
            landmarks: Dictionary of landmark positions
            
        Returns:
            Boolean indicating pinch gesture
        """
        thumb_tip = landmarks[THUMB_TIP]
        index_tip = landmarks[INDEX_TIP]

        # Calculate distance between thumb and index finger tips
        distance = math.sqrt(
            (thumb_tip['x'] - index_tip['x']) ** 2 +
            (thumb_tip['y'] - index_tip['y']) ** 2
        )

        return distance < PINCH_THRESHOLD

    def get_drawing_point(self, landmarks):
        """
        Get the point for drawing (index finger tip)
        
        Args:
            landmarks: Dictionary of landmark positions
            
        Returns:
            Tuple (x, y) of the drawing point
        """
        if landmarks and INDEX_TIP in landmarks:
            return (landmarks[INDEX_TIP]['x'], landmarks[INDEX_TIP]['y'])
        return None

    def get_selection_point(self, landmarks):
        """
        Get the point for selection (middle point between index and middle finger)
        
        Args:
            landmarks: Dictionary of landmark positions
            
        Returns:
            Tuple (x, y) of the selection point
        """
        if landmarks and INDEX_TIP in landmarks and MIDDLE_TIP in landmarks:
            x = (landmarks[INDEX_TIP]['x'] + landmarks[MIDDLE_TIP]['x']) // 2
            y = (landmarks[INDEX_TIP]['y'] + landmarks[MIDDLE_TIP]['y']) // 2
            return (x, y)
        return None

    def get_pinch_distance(self, landmarks):
        """
        Get the distance between thumb and index for dynamic brush sizing
        
        Args:
            landmarks: Dictionary of landmark positions
            
        Returns:
            Float distance value
        """
        if landmarks and THUMB_TIP in landmarks and INDEX_TIP in landmarks:
            thumb_tip = landmarks[THUMB_TIP]
            index_tip = landmarks[INDEX_TIP]

            distance = math.sqrt(
                (thumb_tip['x'] - index_tip['x']) ** 2 +
                (thumb_tip['y'] - index_tip['y']) ** 2
            )
            return distance
        return None
