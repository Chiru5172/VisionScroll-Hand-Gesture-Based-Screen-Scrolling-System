import cv2


def main():
    # Initialize the default webcam
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Unable to access the webcam.")
        print("Check whether your webcam is connected or being used by another application.")
        return

    # Request a suitable resolution
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("VisionScroll webcam test started.")
    print("Press Q to close the camera window.")

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("ERROR: Unable to read a frame from the webcam.")
                break

            # Mirror the image for a natural webcam preview
            frame = cv2.flip(frame, 1)

            # Display the application name
            cv2.putText(
                frame,
                "VisionScroll - Camera Test",
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            # Display the live webcam feed
            cv2.imshow("VisionScroll", frame)

            # Exit when the user presses Q
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        # Always release the webcam and close OpenCV windows
        camera.release()
        cv2.destroyAllWindows()

        print("Webcam closed successfully.")


if __name__ == "__main__":
    main()