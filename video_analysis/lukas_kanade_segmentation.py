import cv2
import numpy as np

def video_segmentation_optical_flow(video_path):
    cap = cv2.VideoCapture(video_path)

    # Read the first frame
    ret, prev_frame = cap.read()

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    # Create a mask image for drawing segmented regions
    mask = np.zeros_like(prev_frame)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the current frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow using Lucas-Kanade algorithm
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        # Compute the magnitude and angle of the optical flow vectors
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # Set the hue value of the mask image based on the angle of the flow vectors
        mask[..., 0] = angle * 180 / np.pi / 2

        # Normalize the magnitude of the flow vectors for better visualization
        mask[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)

        # Convert the mask image from HSV to BGR color space
        mask_bgr = cv2.cvtColor(mask, cv2.COLOR_HSV2BGR)

        # Display the segmented regions in the original frame
        result = cv2.addWeighted(frame, 1, mask_bgr, 2, 0)

        cv2.imshow('Video Segmentation - Optical Flow', result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Update the previous frame and previous grayscale image
        prev_frame = frame
        prev_gray = gray

    cap.release()
    cv2.destroyAllWindows()


# Example usage
video_segmentation_optical_flow('stereo_video.mp4')
