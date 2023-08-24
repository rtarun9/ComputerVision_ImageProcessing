import cv2
import numpy as np

def video_segmentation_motion(video_path, debug_show_mask=False):
    cap = cv2.VideoCapture(video_path)

    # Read the first frame
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Failed to read the video.")

    # Convert the first frame to grayscale
    prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the current frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Compute the absolute difference between the current frame and the previous frame
        frame_diff = cv2.absdiff(prev_gray, gray)

        # Apply a threshold to obtain a binary mask of moving regions
        _, mask = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)

        # Perform morphological operations to remove noise and improve the mask
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=np.ones((3, 3), np.uint8))

        if (debug_show_mask == True):
            cv2.imshow('mask', mask)
            
            prev_gray = gray
            
            if cv2.waitKey(80) & 0xFF == ord('q'):  # Delay of 50 milliseconds (20 frames per second)
                break
            
            continue

            
        # Find contours of connected components in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw bounding rectangles around the detected motion regions
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow('Motion Segmentation', frame)
        if cv2.waitKey(80) & 0xFF == ord('q'):  # Delay of 50 milliseconds (20 frames per second)
            break

        # Update the previous frame
        prev_gray = gray

    cap.release()
    cv2.destroyAllWindows()


# Example usage
video_segmentation_motion('stereo_video.mp4', True)
