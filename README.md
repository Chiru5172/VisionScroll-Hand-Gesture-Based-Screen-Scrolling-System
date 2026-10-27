# VisionScroll

**VisionScroll** is a Python-based, hands-free scrolling application that uses a webcam to track hand gestures and control scrolling on your computer.

The current version detects hand landmarks with MediaPipe, recognizes a pinch gesture between the thumb and index finger, tracks index-finger movement, and uses PyAutoGUI to scroll up or down.

## Current Features

- Webcam video capture using OpenCV.
- Hand landmark detection using MediaPipe Tasks.
- Pinch gesture detection using the thumb tip and index-finger tip.
- Index-finger movement recognition (`UP`, `DOWN`, and `IDLE`).
- Gesture-controlled scrolling using PyAutoGUI.
- Adjustable scroll amount, cooldown, and movement threshold.
- Safe camera and detector cleanup when the tracking script exits.

## Technology Stack

- **Python** — application logic
- **OpenCV** — webcam access and on-screen drawing
- **MediaPipe Tasks** — hand landmark detection
- **PyAutoGUI** — operating-system scroll events

## Project Structure

```text
VisionScroll/
├── assets/
│   └── models/
│       └── hand_landmarker.task
├── config/
├── logs/
├── src/
│   ├── __init__.py
│   ├── detection/
│   │   ├── __init__.py
│   │   └── hand_detector.py
│   └── gestures/
│       ├── __init__.py
│       ├── pinch_detector.py
│       ├── movement_tracker.py
│       └── scroll_controller.py
├── tests/
├── camera_test.py
├── hand_tracking.py
├── test_scroll.py
├── requirements.txt
└── README.md
```

Some folders, such as `config/`, `logs/`, and `tests/`, may not contain files yet. The project structure will expand as the application develops.

## Prerequisites

- Windows computer with a working webcam.
- Python version compatible with the installed MediaPipe release. Python 3.10 or 3.11 is a practical choice; check the MediaPipe package compatibility if using another version.
- Internet access to install Python dependencies.
- The MediaPipe Hand Landmarker model file at `assets/models/hand_landmarker.task`.

## Setup

### 1. Open the project folder

In PowerShell, navigate to your project directory:

```powershell
cd D:\VisionScroll
```

### 2. Create and activate a virtual environment

If you have not already created one:

```powershell
python -m venv venv
```

Activate it in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Check the model file

Confirm that this file exists:

```text
assets/models/hand_landmarker.task
```

The hand-tracking application needs this model to detect hand landmarks. If it is missing, obtain the official MediaPipe Hand Landmarker model and save it at that path.

## Running VisionScroll

Run the hand-tracking application:

```powershell
python hand_tracking.py
```

Place your hand in view of the webcam. The application should display the detected hand landmarks and gesture status. Pinch your thumb and index finger, then move your index finger up or down to control scrolling.

Press **Q** in the camera preview window to exit.

### Test the camera separately

```powershell
python camera_test.py
```

### Test scrolling separately

```powershell
python test_scroll.py
```

For the scroll test, place your cursor over a harmless, scrollable window before the test runs. PyAutoGUI sends scroll events to the window under the cursor.

## Gesture Controls

| Gesture | Expected behavior |
|---|---|
| Show a hand to the webcam | Hand landmarks are detected |
| Pinch thumb and index finger together | Activate gesture-controlled scrolling |
| Move index finger upward while pinching | Scroll up |
| Move index finger downward while pinching | Scroll down |
| Release the pinch | Stop gesture-controlled scrolling |
| Move the hand out of view | Reset gesture tracking |

Exact behavior can depend on lighting, camera position, hand visibility, and the active application.

## Tuning Settings

The settings are currently configured in Python code. You can change them and rerun the application.

### Scroll amount

Configured when creating `ScrollController` in `hand_tracking.py`, for example:

```python
scroll_controller = ScrollController(
    scroll_amount=12,
    cooldown=0.03
)
```

A larger absolute scroll amount usually moves the page farther per scroll event.

### Cooldown

`cooldown` is the minimum interval, in seconds, between scroll events. A smaller value allows more frequent events; a larger value limits how frequently they occur.

### Movement threshold

Configured when creating `MovementTracker`, for example:

```python
movement_tracker = MovementTracker(
    movement_threshold=0.04
)
```

The movement threshold is compared with the change in the index fingertip's normalized vertical coordinate between consecutive processed frames. A lower threshold is more sensitive to small movements; a higher threshold requires a larger change between frames.

### Pinch thresholds

The pinch detector uses:
- `threshold` to activate a pinch.
- `release_threshold` to deactivate it.

Using a larger release threshold than activation threshold provides hysteresis, helping reduce rapid switching around one boundary.

**Note:** These are initial tuning parameters, not universal values. Adjust them based on your camera position and comfort.

## Troubleshooting

### Camera does not open
- Close other applications that may be using the webcam.
- Check the camera index in the code (commonly `0` for the default camera).
- Verify camera permissions in Windows settings.

### Hand landmarks are not detected reliably
- Improve lighting.
- Keep the hand fully visible in the camera frame.
- Check that `assets/models/hand_landmarker.task` exists.

### Scrolling is too slow or too fast
- Adjust `scroll_amount` and `cooldown` in `ScrollController`.
- Adjust `movement_threshold` in `MovementTracker`.
- Change one setting at a time so you can tell which change helped.

### The application exits with an error
- Confirm that the virtual environment is activated.
- Install dependencies with `pip install -r requirements.txt`.
- Read the error message printed in the terminal.

## Safety and Privacy

- The current application uses the local webcam for hand tracking.
- Keep your cursor over a safe, scrollable area when testing; scroll events go to the window under the cursor.
- Stop the application when you no longer need gesture control.
- Avoid exposing the camera to sensitive surroundings while testing.

## Current Status and Future Improvements

### Implemented
- Webcam capture and hand landmark tracking.
- Pinch detection.
- Index-finger movement detection.
- PyAutoGUI scroll controller.
- Separate camera and scroll test scripts.

### Planned
- Tkinter desktop dashboard with Start/Stop controls and live status.
- Background camera processing so the interface remains responsive.
- GUI controls for sensitivity and scrolling speed.
- Save settings in `config/settings.json`.
- Automated tests for gesture detection and configuration.
- Windows executable packaging with PyInstaller.

## License

No license has been selected for this project yet. Add a `LICENSE` file before distributing the project if you want to specify permissions for reuse and modification.

Gujjula Chirudeep Reddy