import cv2
import mediapipe as mp
import time
import pyautogui
import numpy as np
import pyttsx3

# Voice setup (optional)
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Full keyboard layout
keys = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Back"],
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Enter"],
    ["Z", "X", "C", "V", "B", "N", "M", "Space"]
]

typed_text = ""  # Store typed characters

def draw_keyboard(img):
    key_pos = []
    start_x, start_y = 20, 80   # Start from top-left corner
    key_w, key_h = 60, 50       # Smaller keys for better fit

    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            x = start_x + j * (key_w + 5)
            y = start_y + i * (key_h + 5)
            cv2.rectangle(img, (x, y), (x + key_w, y + key_h), (255, 0, 0), 2)

            text = "Space" if key == "Space" else key
            font_scale = 0.7 if key != "Space" else 0.5
            text_x = x + 10
            text_y = y + int(key_h / 2) + 10
            cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)

            key_pos.append((key, x, y, key_w, key_h))

    return key_pos


def is_hover(x, y, key_x, key_y, key_w, key_h):
    return key_x < x < key_x + key_w and key_y < y < key_y + key_h

# Video start
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height
hover_start = 0
hover_key = None

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    key_positions = draw_keyboard(frame)

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            lm = hand.landmark[8]  # Index fingertip
            h, w, _ = frame.shape
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)

            for key, kx, ky, kw, kh in key_positions:
                if is_hover(x, y, kx, ky, kw, kh):
                    cv2.rectangle(frame, (kx, ky), (kx + kw, ky + kh), (0, 255, 0), -1)
                    cv2.putText(frame, key, (kx + 10, ky + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

                    if hover_key != key:
                        hover_start = time.time()
                        hover_key = key
                    else:
                        if time.time() - hover_start > 1:
                            if key == "Space":
                                pyautogui.write(' ')
                                typed_text += " "
                                speak("space")
                            elif key == "Back":
                                pyautogui.press('backspace')
                                typed_text = typed_text[:-1]
                                speak("backspace")
                            elif key == "Enter":
                                pyautogui.press('enter')
                                with open("output.txt", "a") as f:
                                    f.write(typed_text + "\n")
                                typed_text = ""
                                speak("enter")
                            else:
                                pyautogui.write(key.lower())
                                typed_text += key.lower()
                                speak(key.lower())

                            print("Pressed:", key)
                            hover_key = None
                    break
            else:
                hover_key = None
    cv2.putText(frame, "Typed: " + typed_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.imshow("Gesture Keyboard", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
