import cv2
import mediapipe as mp


class HandDetector:
    def __init__(self, model_path, max_hands=1):
        self.model_path = model_path

        self.mp_hands = mp.tasks.vision.HandLandmarker
        self.mp_running_mode = mp.tasks.vision.RunningMode

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=self.model_path
            ),
            running_mode=self.mp_running_mode.VIDEO,
            num_hands=max_hands
        )

        self.detector = self.mp_hands.create_from_options(options)

    def detect(self, frame, timestamp_ms):
        # Convert OpenCV's BGR frame into RGB.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create a MediaPipe image.
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Process the frame.
        result = self.detector.detect_for_video(
            mp_image,
            timestamp_ms
        )

        return result

    def close(self):
        self.detector.close()