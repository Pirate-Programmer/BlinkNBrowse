import mediapipe as mp
import cv2
import time
import math
from hid import *

class HandGesture:
    def __init__(self, keyboard: hid_keyboard, action_cooldown=1.0):
        """
        keyboard: instance of your hid_keyboard class
        action_cooldown: minimum seconds between sending repeated gestures
        """
        self.keyboard = keyboard
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.last_action_time = 0
        self.ACTION_COOLDOWN = action_cooldown

    def process(self, frame):
        """
        Call this each loop with your current frame (BGR from OpenCV)
        Returns: gesture name ("THUMBS_UP", "THUMBS_DOWN", or "NONE")
        """
        current_time = time.time()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(frame_rgb)

        if result.multi_hand_landmarks:
            lm = result.multi_hand_landmarks[0].landmark
            gesture = self.get_gesture(lm)

            if gesture != "NONE" and current_time - self.last_action_time > self.ACTION_COOLDOWN:
                if gesture == "THUMBS_UP":
                    print("Gesture: Thumbs Up -> Ctrl+C")
                    self.keyboard.send_key(KEYS['c'], MODIFIER['ctrl'])
                    self.last_action_time = current_time
                elif gesture == "THUMBS_DOWN":
                    print("Gesture: Thumbs Down -> Ctrl+V")
                    self.keyboard.send_key(KEYS['v'], MODIFIER['ctrl'])
                    self.last_action_time = current_time

            return gesture

        return "NONE"

    def get_gesture(self, lm):
        """Analyzes landmarks to detect thumbs up or down"""
        # Fingers curled check
        fingers_curled = all([
            self._is_finger_curled(lm, 8, 6),
            self._is_finger_curled(lm, 12, 10),
            self._is_finger_curled(lm, 16, 14),
            self._is_finger_curled(lm, 20, 18)
        ])

        if fingers_curled:
            # THUMBS UP: thumb tip above index MCP
            if lm[4].y < lm[5].y - 0.05:
                return "THUMBS_UP"
            # THUMBS DOWN: thumb tip below wrist or pinky MCP
            if lm[4].y > lm[17].y + 0.05 or lm[4].y > lm[0].y + 0.05:
                return "THUMBS_DOWN"

        return "NONE"

    def _is_finger_curled(self, landmarks, tip_idx, pip_idx, wrist_idx=0):
        """Helper to check if a finger is curled based on distance to wrist."""
        wrist = landmarks[wrist_idx]
        tip = landmarks[tip_idx]
        pip = landmarks[pip_idx]
        dist_tip = math.dist((wrist.x, wrist.y), (tip.x, tip.y))
        dist_pip = math.dist((wrist.x, wrist.y), (pip.x, pip.y))
        return dist_tip < dist_pip
