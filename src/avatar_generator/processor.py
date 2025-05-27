import cv2
import numpy as np
import face_alignment
import insightface
from insightface.app import FaceAnalysis
import torch
import mediapipe as mp
import streamlit as st

class ImageProcessor:
    """Class for processing input images before avatar generation"""
    
    def __init__(self):
        """Initialize the image processor with face detection and alignment tools"""
        
        # Initialize mediapipe face mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        
        # Try to initialize InsightFace for face analysis
        try:
            self.face_analyzer = FaceAnalysis(name='buffalo_l')
            self.face_analyzer.prepare(ctx_id=0 if torch.cuda.is_available() else -1)
        except Exception as e:
            st.warning(f"InsightFace initialization failed: {e}. Falling back to alternative methods.")
            self.face_analyzer = None
        
        # Initialize face alignment
        try:
            self.face_aligner = face_alignment.FaceAlignment(
                face_alignment.LandmarksType.THREE_D, 
                device='cuda' if torch.cuda.is_available() else 'cpu'
            )
        except Exception as e:
            st.warning(f"Face alignment initialization failed: {e}")
            self.face_aligner = None
    
    def process(self, image: np.ndarray) -> np.ndarray:
        """
        Process the input image for avatar generation
        
        Args:
            image: Input image as numpy array
            
        Returns:
            processed_image: Processed image ready for avatar generation
        """
        if image is None:
            raise ValueError("Input image is None")
        
        # Create a copy to avoid modifying the original
        processed_image = image.copy()
        
        # Step 1: Detect face
        face_bbox = self._detect_face(processed_image)
        if face_bbox is None:
            raise ValueError("No face detected in the image. Please try again with a clearer face image.")
        
        # Step 2: Crop and align face
        aligned_face = self._align_face(processed_image, face_bbox)
        
        # Step 3: Enhance image quality
        enhanced_image = self._enhance_image(aligned_face)
        
        # Step 4: Normalize lighting and colors
        normalized_image = self._normalize_image(enhanced_image)
        
        # Display processing steps for debugging (commented out in production)
        # self._display_processing_steps(image, face_bbox, aligned_face, enhanced_image, normalized_image)
        
        return normalized_image
    
    def _detect_face(self, image: np.ndarray):
        """Detect the primary face in the image"""
        # Try InsightFace first if available
        if self.face_analyzer is not None:
            try:
                faces = self.face_analyzer.get(image)
                if len(faces) > 0:
                    # Get the largest or most prominent face
                    face = max(faces, key=lambda x: x.bbox[2] * x.bbox[3])
                    x1, y1, x2, y2 = map(int, face.bbox)
                    return [x1, y1, x2 - x1, y2 - y1]
            except Exception as e:
                st.warning(f"InsightFace detection failed: {e}")
        
        # Fall back to mediapipe
        try:
            with self.mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                min_detection_confidence=0.5
            ) as face_mesh:
                # Convert to RGB if needed
                if image.shape[2] == 3 and image.dtype == np.uint8:
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if image.shape[2] == 3 else image
                else:
                    rgb_image = image
                
                results = face_mesh.process(rgb_image)
                
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    h, w = image.shape[:2]
                    
                    # Get face bounding box from landmarks
                    x_coords = [landmark.x * w for landmark in landmarks]
                    y_coords = [landmark.y * h for landmark in landmarks]
                    
                    x1, y1 = int(min(x_coords)), int(min(y_coords))
                    x2, y2 = int(max(x_coords)), int(max(y_coords))
                    
                    # Add a margin to the bounding box
                    margin_x = int((x2 - x1) * 0.2)
                    margin_y = int((y2 - y1) * 0.2)
                    
                    x1 = max(0, x1 - margin_x)
                    y1 = max(0, y1 - margin_y)
                    x2 = min(w, x2 + margin_x)
                    y2 = min(h, y2 + margin_y)
                    
                    return [x1, y1, x2 - x1, y2 - y1]
        except Exception as e:
            st.warning(f"Mediapipe face detection failed: {e}")
        
        # Last resort: OpenCV
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                # Get the largest face
                largest_idx = np.argmax([w*h for (x, y, w, h) in faces])
                return faces[largest_idx]
        except Exception as e:
            st.error(f"All face detection methods failed: {e}")
        
        return None
    
    def _align_face(self, image: np.ndarray, bbox):
        """Align the face for consistent processing"""
        try:
            if self.face_aligner is not None:
                landmarks = self.face_aligner.get_landmarks_from_image(image)
                if landmarks is not None and len(landmarks) > 0:
                    # Use detected landmarks to align the face
                    return self._perspective_transform(image, landmarks[0])
            
            # If face alignment fails, just crop the face
            x, y, w, h = bbox
            face_img = image[y:y+h, x:x+w]
            
            # Resize to a standard size
            return cv2.resize(face_img, (512, 512))
            
        except Exception as e:
            st.warning(f"Face alignment failed: {e}. Using simple crop instead.")
            # Simple crop if alignment fails
            x, y, w, h = bbox
            # Ensure the crop is within image bounds
            x = max(0, x)
            y = max(0, y)
            w = min(w, image.shape[1] - x)
            h = min(h, image.shape[0] - y)
            
            face_img = image[y:y+h, x:x+w]
            return cv2.resize(face_img, (512, 512))
    
    def _perspective_transform(self, image, landmarks):
        """Transform image based on facial landmarks for proper alignment"""
        # Get essential face landmarks (eyes, nose, mouth corners)
        h, w = image.shape[:2]
        
        # Extract key points (simplification of the full algorithm)
        # These indices are for a standard 68-point facial landmark model
        left_eye = np.mean(landmarks[36:42], axis=0)
        right_eye = np.mean(landmarks[42:48], axis=0)
        nose_tip = landmarks[30]
        left_mouth = landmarks[48]
        right_mouth = landmarks[54]
        
        # Define source points
        src_pts = np.array([
            left_eye[:2],
            right_eye[:2],
            nose_tip[:2],
            left_mouth[:2],
            right_mouth[:2]
        ], dtype=np.float32)
        
        # Define destination points for a 512x512 image
        # These are approximate positions for a well-aligned face
        dst_pts = np.array([
            [170, 200],  # left eye
            [342, 200],  # right eye
            [256, 280],  # nose tip
            [180, 360],  # left mouth corner
            [332, 360]   # right mouth corner
        ], dtype=np.float32)
        
        # Calculate transformation matrix
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        
        # Apply transformation
        aligned_image = cv2.warpPerspective(image, M, (512, 512))
        
        return aligned_image
    
    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better avatar generation"""
        # Apply a slight Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (3, 3), 0)
        
        # Apply contrast enhancement (CLAHE)
        lab = cv2.cvtColor(blurred, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        enhanced_lab = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
        
        return enhanced
    
    def _normalize_image(self, image: np.ndarray) -> np.ndarray:
        """Normalize lighting and colors for consistent processing"""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # Split channels
        l, a, b = cv2.split(lab)
        
        # Normalize luminance channel
        l_norm = cv2.normalize(l, None, 0, 255, cv2.NORM_MINMAX)
        
        # Merge channels
        normalized_lab = cv2.merge([l_norm, a, b])
        
        # Convert back to RGB
        normalized = cv2.cvtColor(normalized_lab, cv2.COLOR_LAB2RGB)
        
        return normalized
    
    def _display_processing_steps(self, original, bbox, aligned, enhanced, normalized):
        """Display the processing steps for debugging"""
        # Draw the bounding box on the original image
        debug_image = original.copy()
        x, y, w, h = bbox
        cv2.rectangle(debug_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Create a composite image with all steps
        st.subheader("Image Processing Steps (Debug)")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.image(debug_image, caption="Face Detection", width=200)
        with col2:
            st.image(aligned, caption="Aligned Face", width=200)
        with col3:
            st.image(enhanced, caption="Enhanced", width=200)
        with col4:
            st.image(normalized, caption="Normalized", width=200)