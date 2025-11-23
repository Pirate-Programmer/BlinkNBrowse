import cv2 as cv
import mediapipe as mp
import pyautogui
import keyboard

# --- Global Settings ---
CAMERA_INPUT = 0
FRAME_WIDTH = 640  # Width of the camera frame
FRAME_HEIGHT = 480  # Height of the camera frame

# --- !! TUNE THIS VALUE !! ---
# Higher = more sensitive, faster cursor
# Lower = less sensitive, slower cursor
SENSITIVITY = 3000.0
# -----------------------------

# Get the size of your primary screen
SCREEN_W, SCREEN_H = pyautogui.size()
print(f"Screen Size: {SCREEN_W}x{SCREEN_H}")

# --- SAFETY FEATURE ---
pyautogui.FAILSAFE = True

# --- Initialize MediaPipe Hands ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# --- Initialize Video Capture ---
cap = cv.VideoCapture(CAMERA_INPUT)
cap.set(cv.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# --- Anchor Variables for Relative Mode ---
anchor_x, anchor_y = 0.5, 0.5  # Normalized hand anchor
cursor_anchor_x, cursor_anchor_y = 0, 0  # Pixel mouse anchor
anchor_is_set = False  # Flag to see if we've set the anchor

print("Starting Relative Hand Cursor...")
print("Hold 'Ctrl' to activate cursor movement.")
print("Press 'q' in the OpenCV window to quit.")

while True:
    isFrame, frame = cap.read()
    if not isFrame:
        print("Failed to grab frame.")
        break

    frame = cv.flip(frame, 1)

    # Check for 'Ctrl' key press
    is_active = False
    try:
        if keyboard.is_pressed('ctrl'):
            is_active = True
    except Exception as e:
        print(f"Warning: Could not read keyboard state. Error: {e}")
        is_active = False

    # Process the frame
    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    frame.flags.writeable = False
    result = hands.process(frame_rgb)
    frame.flags.writeable = True

    # --- Main Logic ---
    if result.multi_hand_landmarks:
        # Hand is detected
        hand_landmarks = result.multi_hand_landmarks[0]
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

        if is_active:
            # --- 'Ctrl' is PRESSED ---

            if not anchor_is_set:
                # --- This is the FIRST frame 'Ctrl' is pressed ---
                # 1. Set the hand anchor to the current tip position
                anchor_x, anchor_y = index_tip.x, index_tip.y

                # 2. Set the cursor anchor to the current mouse position
                cursor_anchor_x, cursor_anchor_y = pyautogui.position()

                # 3. Set the flag
                anchor_is_set = True
                print(
                    f"Anchor Set: Hand at ({anchor_x:.2f}, {anchor_y:.2f}), Cursor at ({cursor_anchor_x}, {cursor_anchor_y})")

            else:
                # --- 'Ctrl' is HELD, and anchor is already set ---
                # 1. Calculate the *difference* from the anchor
                delta_x = index_tip.x - anchor_x
                delta_y = index_tip.y - anchor_y

                # 2. Calculate new cursor position
                # (Start from the cursor's anchor position and add the scaled delta)
                new_x = cursor_anchor_x + (delta_x * SENSITIVITY)
                new_y = cursor_anchor_y + (delta_y * SENSITIVITY)

                # --- FIX: Clamp the coordinates to the screen boundaries ---
                # This prevents the mouse from ever hitting the corners
                # and triggering the failsafe.
                new_x = max(0, min(new_x, SCREEN_W - 1))
                new_y = max(0, min(new_y, SCREEN_H - 1))
                # ---------------------------------------------------------

                # 3. Move the mouse
                pyautogui.moveTo(new_x, new_y)

            # --- Visual Feedback (Drawing) ---
            h, w, _ = frame.shape
            # Draw a circle on the current tip
            cv.circle(frame, (int(index_tip.x * w), int(index_tip.y * h)), 10, (0, 255, 0), -1)
            # Draw a circle on the anchor position
            cv.circle(frame, (int(anchor_x * w), int(anchor_y * h)), 10, (0, 0, 255), -1)

        else:
            # --- 'Ctrl' is RELEASED ---
            # "Lift the mouse" - reset the anchor flag
            if anchor_is_set:
                print("Anchor Released")
                anchor_is_set = False

    else:
        # --- No hand is detected ---
        # Also reset the anchor
        if anchor_is_set:
            print("Anchor Released (Hand Lost)")
            anchor_is_set = False

    # --- UI Status Text ---
    if is_active:
        cv.putText(frame, "STATUS: ACTIVE (Relative)", (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv.putText(frame, "STATUS: IDLE (Hold Ctrl)", (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv.imshow("Relative Hand Cursor (Press 'q' to quit)", frame)

    if cv.waitKey(10) & 0xFF == ord('q'):
        print("Exiting...")
        break

# --- Cleanup ---
cap.release()
cv.destroyAllWindows()
hands.close()
print("Script finished.")