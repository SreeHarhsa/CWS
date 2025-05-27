import cv2
import numpy as np
import time
import streamlit as st
from ultralytics import YOLO

class CameraCapture:
    """Class to handle camera capture functionality"""
    
    def __init__(self, model_path="data/models/yolov8n-face.pt"):
        """
        Initialize the camera capture module
        
        Args:
            model_path: Path to the YOLO model for face detection
        """
        self.camera = None
        self.face_detector = None
        
        try:
            # Try to load YOLO model if available
            self.face_detector = YOLO(model_path)
        except Exception:
            # If model not found, use OpenCV's face detector
            self.face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def capture_image(self, countdown=3):
        """
        Capture an image from the webcam with a countdown
        
        Args:
            countdown: Seconds to countdown before capturing
            
        Returns:
            numpy.ndarray: Captured image or None if failed
        """
        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                st.error("Error: Could not open camera.")
                return None
            
            # Create a placeholder for the camera feed
            camera_placeholder = st.empty()
            
            # Show countdown
            for i in range(countdown, 0, -1):
                ret, frame = self.camera.read()
                if not ret:
                    st.error("Failed to capture image")
                    return None
                
                # Flip the frame for a mirror effect
                frame = cv2.flip(frame, 1)
                
                # Draw countdown on frame
                h, w = frame.shape[:2]
                cv2.putText(frame, str(i), (int(w/2), int(h/2)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 5)
                
                # Convert to RGB for display
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Display in Streamlit
                camera_placeholder.image(rgb_frame, channels="RGB")
                
                # Wait for a second
                time.sleep(1)
            
            # Capture final image
            ret, frame = self.camera.read()
            frame = cv2.flip(frame, 1)  # Mirror effect
            
            if not ret:
                st.error("Failed to capture image")
                return None
            
            # Convert to RGB for processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Display the captured image
            camera_placeholder.image(rgb_frame, channels="RGB", caption="Captured Image")
            
            # Release the camera
            self.camera.release()
            
            # Return the captured frame
            return rgb_frame
        
        except Exception as e:
            st.error(f"Error capturing image: {str(e)}")
            
            # Make sure to release the camera if an error occurs
            if self.camera is not None:
                self.camera.release()
            
            return None
    
    def detect_face(self, image):
        """
        Detect faces in the image
        
        Args:
            image: Input image
            
        Returns:
            tuple: (face_detected, face_bbox) where face_bbox is [x, y, w, h]
        """
        try:
            if image is None:
                return False, None
            
            # If YOLO model is available
            if isinstance(self.face_detector, YOLO):
                results = self.face_detector(image)
                if len(results) > 0 and len(results[0].boxes) > 0:
                    # Get the first face box
                    box = results[0].boxes[0].xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = map(int, box)
                    return True, [x1, y1, x2-x1, y2-y1]
            
            # Fallback to OpenCV
            if hasattr(self.face_detector, 'detectMultiScale'):
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) > 0:
                    # Get the largest face by area
                    largest_face_idx = np.argmax([w*h for (x, y, w, h) in faces])
                    x, y, w, h = faces[largest_face_idx]
                    return True, [x, y, w, h]
            
            return False, None
            
        except Exception as e:
            st.error(f"Error detecting face: {str(e)}")
            return False, None