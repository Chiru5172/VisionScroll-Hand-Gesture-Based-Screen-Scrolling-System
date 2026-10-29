import cv2
import time
import threading
from pathlib import Path
from queue import Queue, Empty
from src.gestures.pinch_detector import PinchDetector
from src.detection.hand_detector import HandDetector
from src.gestures.movement_tracker import MovementTracker
from src.gestures.scroll_controller import ScrollController

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "assets" / "models" / "hand_landmarker.task"


class CameraWorker:
    def __init__(self):
        self.camera = None
        self.detector = None
        self.thread = None
        self.gesture_status = "Inactive"
        self.pinch_active = False
        self.scroll_direction = "IDLE"

        self.running = False
        self.stop_event = threading.Event()

        # Store only the latest frame to avoid building up a backlog.
        self.frame_queue = Queue(maxsize=1)

        self.error = None

    def start(self):
        if self.running:
            return

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"MediaPipe model not found: {MODEL_PATH}"
            )

        self.stop_event.clear()
        self.error = None
        self.running = True

        self.thread = threading.Thread(
            target=self._process_camera,
            daemon=True
        )
        self.thread.start()

    def _publish_frame(self, frame):
        if self.frame_queue.full():
            try:
                self.frame_queue.get_nowait()
            except Empty:
                pass

        try:
            self.frame_queue.put_nowait(frame)
        except Exception:
            pass

    def _process_camera(self):
        try:
            self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

            if not self.camera.isOpened():
                self.camera.release()
                self.camera = cv2.VideoCapture(0)

            if not self.camera.isOpened():
                raise RuntimeError("Unable to open webcam.")

            # Configure camera resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            # Reduce buffering so the preview uses recent frames
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            self.detector = HandDetector(
                model_path=str(MODEL_PATH),
                max_hands=1
            )
            pinch_detector = PinchDetector(
                threshold=0.05,
                release_threshold=0.07
            )

            previous_timestamp_ms = -1

            while not self.stop_event.is_set():
                success, frame = self.camera.read()

                if not success:
                    raise RuntimeError("Unable to read from webcam.")

                timestamp_ms = int(time.monotonic() * 1000)
                timestamp_ms = max(
                    timestamp_ms,
                    previous_timestamp_ms + 1
                )
                previous_timestamp_ms = timestamp_ms

                result = self.detector.detect(frame, timestamp_ms)

                if result.hand_landmarks:
                    landmarks = result.hand_landmarks[0]

                    # Draw hand landmarks
                    self._draw_landmarks(frame, landmarks)

                    # Detect pinch gesture
                    pinch_distance, pinch_active = pinch_detector.detect(
                        landmarks
                    )

                    if pinch_active:
                        status_text = "PINCH ACTIVE"
                        status_color = (0, 255, 0)
                    else:
                        status_text = "PINCH INACTIVE"
                        status_color = (0, 200, 255)

                    # Display pinch status
                    cv2.putText(
                        frame,
                        status_text,
                        (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        status_color,
                        2
                    )

                    # Display distance between thumb and index finger
                    cv2.putText(
                        frame,
                        f"Pinch distance: {pinch_distance:.3f}",
                        (20, 105),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2
                    )

                else:
                    pinch_detector.reset()

                    cv2.putText(
                        frame,
                        "Show your hand",
                        (20, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 200, 255),
                        2
                    )

                self._publish_frame(frame)

        except Exception as exc:
            self.error = str(exc)

        finally:
            if self.detector is not None:
                try:
                    self.detector.close()
                except Exception:
                    pass
                self.detector = None

            if self.camera is not None:
                try:
                    self.camera.release()
                except Exception:
                    pass
                self.camera = None

            self.running = False

    @staticmethod
    def _draw_landmarks(frame, landmarks):
        height, width, _ = frame.shape

        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17), (5, 9)
        ]

        points = [
            (int(point.x * width), int(point.y * height))
            for point in landmarks
        ]

        for start, end in connections:
            cv2.line(
                frame,
                points[start],
                points[end],
                (0, 255, 0),
                2
            )

        for x, y in points:
            cv2.circle(frame, (x, y), 4, (255, 255, 255), -1)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), 1)

    def get_frame(self):
        try:
            return self.frame_queue.get_nowait()
        except Empty:
            return None

    def stop(self):
        self.stop_event.set()

        if self.thread is not None:
            self.thread.join(timeout=3)

        if self.thread is None or not self.thread.is_alive():
            self.running = False
