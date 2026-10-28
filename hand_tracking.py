import time
from pathlib import Path

import cv2
import mediapipe as mp
import time

from src.gestures.pinch_detector import PinchDetector
from src.gestures.movement_tracker import MovementTracker
from src.gestures.scroll_controller import ScrollController
from src.detection.hand_detector import HandDetector


# Project paths
BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "assets"
    / "models"
    / "hand_landmarker.task"
)

def draw_hand_landmarks(frame, landmarks):
    height, width, _ = frame.shape

    # Connections between the 21 hand landmarks.
    connections = [
        # Thumb
        (0, 1), (1, 2), (2, 3), (3, 4),

        # Index finger
        (0, 5), (5, 6), (6, 7), (7, 8),

        # Middle finger
        (5, 9), (9, 10), (10, 11), (11, 12),

        # Ring finger
        (9, 13), (13, 14), (14, 15), (15, 16),

        # Little finger
        (13, 17), (17, 18), (18, 19), (19, 20),

        # Palm connections
        (0, 17), (5, 9)
    ]

    # Convert normalized coordinates to pixel coordinates.
    points = []

    for landmark in landmarks:
        x = int(landmark.x * width)
        y = int(landmark.y * height)

        points.append((x, y))

    # Draw connections between landmarks.
    for start, end in connections:
        cv2.line(
            frame,
            points[start],
            points[end],
            (0, 255, 0),
            2
        )

    # Draw all 21 landmarks.
    for x, y in points:
        cv2.circle(
            frame,
            (x, y),
            4,
            (255, 255, 255),
            -1
        )

        cv2.circle(
            frame,
            (x, y),
            5,
            (0, 255, 0),
            1
        )
    
def main():
    if not MODEL_PATH.exists():
        print("ERROR: Hand landmark model was not found.")
        print(f"Expected location: {MODEL_PATH}")
        return

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Unable to open webcam.")
        return

    detector = None

    try:
        detector = HandDetector(
            model_path=str(MODEL_PATH),
            max_hands=1
        )
        pinch_detector = PinchDetector(
            threshold=0.05,
            release_threshold=0.07
        )

        movement_tracker = MovementTracker(
            movement_threshold=0.004
        )

        scroll_controller = ScrollController(
            scroll_amount=12,
            cooldown=0.03
        )
        print("VisionScroll hand tracking started.")
        print("Press Q to exit.")

        previous_timestamp_ms = -1
        previous_time = time.perf_counter()

        while True:
            success, frame = camera.read()

            if not success:
                print("ERROR: Unable to read webcam frame.")
                break

            # Mirror the frame for a natural preview.
            frame = cv2.flip(frame, 1)

            # Generate monotonically increasing timestamps.
            timestamp_ms = int(time.monotonic() * 1000)

            timestamp_ms = max(
                timestamp_ms,
                previous_timestamp_ms + 1
            )

            previous_timestamp_ms = timestamp_ms

            # Detect hand landmarks.
            result = detector.detect(
                frame,
                timestamp_ms
            )

            height, width, _ = frame.shape

            hand_count = len(result.hand_landmarks)

            cv2.putText(
                frame,
                f"Hands detected: {hand_count}",
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            if result.hand_landmarks:
                landmarks = result.hand_landmarks[0]

                # Draw hand landmarks.
                draw_hand_landmarks(frame, landmarks)

                # Get current fingertip positions.
                thumb_tip = landmarks[4]
                index_tip = landmarks[8]
                # Detect the pinch gesture
                pinch_distance, pinch_active = pinch_detector.detect(landmarks)

                if pinch_active:
                    # Track index finger movement
                    movement = movement_tracker.update(
                        index_tip,
                        time.monotonic()
                    )

                    direction = movement["direction"]

                    # Perform scrolling
                    if direction in ("UP", "DOWN"):
                        scroll_controller.scroll(direction)

                    status = f"PINCH ACTIVE | Direction: {direction}"

                else:
                    movement_tracker.reset()
                    status = "PINCH INACTIVE"

                # Display gesture status
                cv2.putText(
                    frame,
                    status,
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                thumb_x = int(thumb_tip.x * width)
                thumb_y = int(thumb_tip.y * height)

                index_x = int(index_tip.x * width)
                index_y = int(index_tip.y * height)

                # Highlight the thumb and index fingertips.
                cv2.circle(
                    frame,
                    (thumb_x, thumb_y),
                    10,
                    (0, 0, 255),
                    -1
                )

                cv2.circle(
                    frame,
                    (index_x, index_y),
                    10,
                    (255, 0, 0),
                    -1
                )

                # Detect pinch activation.
                pinch_distance, pinch_active = pinch_detector.detect(
                    landmarks
                )

                # Track movement only while the pinch is active.
                if pinch_active:
                    movement = movement_tracker.update(
                        index_tip,
                        time.monotonic()
                    )
                else:
                    movement_tracker.reset()

                    movement = {
                        "direction": "INACTIVE",
                        "displacement": 0.0,
                        "velocity": 0.0
                    }

                # Display fingertip coordinates.
                cv2.putText(
                    frame,
                    f"Index X: {index_tip.x:.3f}",
                    (15, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Index Y: {index_tip.y:.3f}",
                    (15, 95),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2
                )

                # Display pinch status.
                pinch_status = (
                    "ACTIVE" if pinch_active else "INACTIVE"
                )

                cv2.putText(
                    frame,
                    f"Pinch: {pinch_status}",
                    (15, 130),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0) if pinch_active else (0, 0, 255),
                    2
                )

                if pinch_distance is not None:
                    cv2.putText(
                        frame,
                        f"Pinch Distance: {pinch_distance:.3f}",
                        (15, 160),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2
                    )

                # Display movement direction.
                cv2.putText(
                    frame,
                    f"Movement: {movement['direction']}",
                    (15, 195),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

            else:
                # Reset the detectors if the hand disappears.
                pinch_detector.reset()
                movement_tracker.reset()

                cv2.putText(
                    frame,
                    "Show your hand to the camera",
                    (15, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )

            # Calculate approximate processing FPS.
            current_time = time.perf_counter()
            elapsed = current_time - previous_time
            previous_time = current_time

            if elapsed > 0:
                fps = 1.0 / elapsed

                cv2.putText(
                    frame,
                    f"FPS: {fps:.1f}",
                    (15, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

            cv2.imshow(
                "VisionScroll - Hand Tracking",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nApplication interrupted.")

    except Exception as error:
        print(f"Application error: {error}")

    finally:
        camera.release()
        cv2.destroyAllWindows()

        if detector is not None:
            detector.close()

        print("VisionScroll stopped safely.")


if __name__ == "__main__":
    main()
