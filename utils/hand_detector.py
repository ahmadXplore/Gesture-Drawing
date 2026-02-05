"""
Hand Detection Module
Handles hand tracking using MediaPipe
"""

import cv2
import mediapipe as mp
from config.settings import DETECTION_CONFIDENCE, TRACKING_CONFIDENCE, MAX_HANDS


class HandDetector:
    """Detects and tracks hands using MediaPipe"""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_HANDS,
            min_detection_confidence=DETECTION_CONFIDENCE,
            min_tracking_confidence=TRACKING_CONFIDENCE
        )
        
    def find_hands(self, frame, draw=True):
        """
        Detect hands in the frame
        
        Args:
            frame: BGR image from webcam
            draw: Whether to draw landmarks on the frame
            
        Returns:
            frame: Frame with landmarks drawn (if draw=True)
            results: MediaPipe results object
        """
        # Convert BGR to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb)
        
        # Draw landmarks if hands detected
        if results.multi_hand_landmarks and draw:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
        
        return frame, results
    
    def get_landmarks(self, results, frame_shape):
        """
        Extract landmark positions from results
        
        Args:
            results: MediaPipe results object
            frame_shape: Shape of the frame (height, width, channels)
            
        Returns:
            List of landmark dictionaries with x, y pixel coordinates
        """
        landmarks_list = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = {}
                h, w, _ = frame_shape
                
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    # Convert normalized coordinates to pixel coordinates
                    landmarks[idx] = {
                        'x': int(landmark.x * w),
                        'y': int(landmark.y * h),
                        'z': landmark.z
                    }
                
                landmarks_list.append(landmarks)
        
        return landmarks_list
    
    def close(self):
        """Release resources"""
        self.hands.close()
