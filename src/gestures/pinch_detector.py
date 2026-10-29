import math


class PinchDetector:
    def __init__(self, threshold=0.05, release_threshold=0.07):
        self.threshold = threshold
        self.release_threshold = release_threshold
        self.is_pinching = False

    def calculate_distance(self, thumb_tip, index_tip):
        dx = thumb_tip.x - index_tip.x
        dy = thumb_tip.y - index_tip.y

        return math.sqrt(dx * dx + dy * dy)

    def detect(self, landmarks):
        if landmarks is None or len(landmarks) < 21:
            self.reset()
            return None, False

        thumb_tip = landmarks[4]
        index_tip = landmarks[8]

        distance = self.calculate_distance(thumb_tip, index_tip)

        # Activate pinch when the fingers are close
        if not self.is_pinching:
            if distance <= self.threshold:
                self.is_pinching = True

        # Release pinch when the fingers separate
        elif distance >= self.release_threshold:
            self.is_pinching = False

        return distance, self.is_pinching

    def reset(self):
        self.is_pinching = False