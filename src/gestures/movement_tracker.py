class MovementTracker:
    def __init__(self, movement_threshold=0.006):
        self.movement_threshold = movement_threshold
        self.previous_y = None
        self.previous_time = None

    def update(self, index_tip, timestamp):
        current_y = index_tip.y

        if self.previous_y is None or self.previous_time is None:
            self.previous_y = current_y
            self.previous_time = timestamp

            return {
                "direction": "IDLE",
                "displacement": 0.0,
                "velocity": 0.0
            }

        delta_y = current_y - self.previous_y
        delta_time = timestamp - self.previous_time

        self.previous_y = current_y
        self.previous_time = timestamp

        if delta_time <= 0:
            return {
                "direction": "IDLE",
                "displacement": delta_y,
                "velocity": 0.0
            }

        velocity = delta_y / delta_time

        if delta_y < -self.movement_threshold:
            direction = "UP"
        elif delta_y > self.movement_threshold:
            direction = "DOWN"
        else:
            direction = "IDLE"

        return {
            "direction": direction,
            "displacement": delta_y,
            "velocity": velocity
        }

    def reset(self):
        self.previous_y = None
        self.previous_time = None