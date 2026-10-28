import time
from src.gestures.scroll_controller import ScrollController

controller = ScrollController(scroll_amount=3)

print("Place your cursor over a scrollable window.")
print("Scrolling UP in 3 seconds...")

time.sleep(3)
controller.scroll("UP")

print("Scrolling DOWN in 2 seconds...")
time.sleep(2)
controller.scroll("DOWN")

print("Test completed!")
