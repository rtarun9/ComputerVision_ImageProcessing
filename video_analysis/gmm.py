import cv2
import numpy as np

def video_segmentation_motion(video_path):
    cap = cv2.VideoCapture(video_path)

    # Read the first frame
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Failed to read the video.")

    # Convert the first frame to grayscale
    prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Create a background subtractor object using Gaussian Mixture Model
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the current frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply background subtraction to obtain a foreground mask
        fg_mask = bg_subtractor.apply(gray)

        # Perform morphological operations to remove noise and improve the mask
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel=np.ones((3, 3), np.uint8))

        # Find contours of connected components in the mask
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw bounding rectangles around the detected motion regions
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

        cv2.imshow('Motion Segmentation', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if cv2.waitKey(70) & 0xFF == ord('q'):  # Delay of 50 milliseconds (20 frames per second)
            break
        
        # Update the previous frame
        prev_gray = gray

    cap.release()
    cv2.destroyAllWindows()


# Example usage
video_segmentation_motion('stereo_video.mp4')
