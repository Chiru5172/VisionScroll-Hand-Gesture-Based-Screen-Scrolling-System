import pyautogui


class ScrollController:
    def __init__(self, scroll_amount=40, cooldown=0.08):
        self.scroll_amount = scroll_amount
        self.cooldown = cooldown
        self.last_scroll_time = 0.0

    def scroll(self, direction):
        import time

        current_time = time.monotonic()

        if current_time - self.last_scroll_time < self.cooldown:
            return

        if direction == "UP":
            pyautogui.scroll(self.scroll_amount)
        elif direction == "DOWN":
            pyautogui.scroll(-self.scroll_amount)
        else:
            return

        self.last_scroll_time = current_time