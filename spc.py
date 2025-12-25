import cv2
import mediapipe as mp
import random
import time
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
ROUND_TIME = 5
RESULT_TIME = 5
phase = "PLAY"
round_start = time.time()
current_detected_move = None
locked_move = None
computer_move = ""
result_text = ""

def count_fingers(hand_landmarks):
    lm = hand_landmarks.landmark
    fingers = 0
    if lm[4].x < lm[3].x:
        fingers += 1
    tips = [8, 12, 16, 20]
    for tip in tips:
        if lm[tip].y < lm[tip - 2].y:
            fingers += 1
    return fingers

def fingers_to_move(fingers):
    if fingers <= 1:
        return "Rock"
    elif fingers <= 3:
        return "Scissors"
    else:
        return "Paper"

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    elapsed = int(time.time() - round_start)
    if phase == "PLAY":
        remaining = ROUND_TIME - elapsed
        if remaining > 0:
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    fingers = count_fingers(hand_landmarks)
                    current_detected_move = fingers_to_move(fingers)
                    mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )
            cv2.putText(frame, f"Show Hand: {remaining}s",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 255), 2)
            if current_detected_move:
                cv2.putText(frame,
                            f"Detected: {current_detected_move}",
                            (10, 80),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)

        else:
            locked_move = current_detected_move
            if locked_move is None:
                locked_move = "Rock"  
            computer_move = random.choice(
                ["Rock", "Paper", "Scissors"])
            if locked_move == computer_move:
                result_text = "Draw"
            elif (locked_move == "Rock" and computer_move == "Scissors") or \
                 (locked_move == "Paper" and computer_move == "Rock") or \
                 (locked_move == "Scissors" and computer_move == "Paper"):
                result_text = "You Win!"
            else:
                result_text = "Computer Wins!"
            phase = "RESULT"
            round_start = time.time()
    else:
        cv2.putText(frame, f"Your Move: {locked_move}",
                    (10, 80), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)
        cv2.putText(frame, f"Computer: {computer_move}",
                    (10, 120), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 0, 0), 2)
        cv2.putText(frame, result_text,
                    (10, 160), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2)
        if elapsed >= RESULT_TIME:
            phase = "PLAY"
            round_start = time.time()
            current_detected_move = None
            locked_move = None
    cv2.imshow("Rock Paper Scissors - MediaPipe", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
