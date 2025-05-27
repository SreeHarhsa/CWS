import os
import cv2
import numpy as np
import mediapipe as mp
import streamlit as st

class VirtualFitter:
    """Class for fitting accessories onto the avatar"""
    
    def __init__(self):
        """Initialize the virtual fitting module"""
        # Initialize MediaPipe Pose for body keypoints
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize MediaPipe Face Mesh for face keypoints
        self.mp_face_mesh = mp.solutions.face_mesh
    
    def fit_accessory(self, avatar_image, accessory):
        """
        Fit an accessory onto the avatar
        
        Args:
            avatar_image: Avatar image
            accessory: Accessory data
            
        Returns:
            numpy.ndarray: Avatar image with accessory fitted
        """
        if avatar_image is None or accessory is None:
            return avatar_image
        
        # Get accessory image and mask
        accessory_img = accessory.get('image')
        accessory_mask = accessory.get('mask')
        
        if accessory_img is None:
            return avatar_image
        
        # If mask is not provided, create one from the alpha channel if available
        if accessory_mask is None and accessory_img.shape[-1] == 4:
            accessory_mask = accessory_img[:, :, 3]
        
        # If no mask can be created, skip fitting
        if accessory_mask is None:
            return avatar_image
        
        # Determine the position to place the accessory based on category
        category = accessory.get('category', '')
        position = accessory.get('position', '')
        
        # Calculate keypoints for positioning
        keypoints = self._get_keypoints(avatar_image)
        
        # Place the accessory based on category and position
        if category == 'clothing' or position == 'body':
            return self._fit_clothing(avatar_image, accessory_img, accessory_mask, keypoints)
        elif category == 'jewelry' or position == 'neck':
            return self._fit_jewelry(avatar_image, accessory_img, accessory_mask, keypoints)
        elif category == 'shoes' or position == 'feet':
            return self._fit_shoes(avatar_image, accessory_img, accessory_mask, keypoints)
        elif category == 'watches' or position == 'wrist':
            return self._fit_watch(avatar_image, accessory_img, accessory_mask, keypoints)
        else:
            # If unknown category, place in the center (fallback)
            return self._place_accessory_center(avatar_image, accessory_img, accessory_mask)
    
    def _get_keypoints(self, image):
        """
        Get body and face keypoints from the avatar image
        
        Args:
            image: Avatar image
            
        Returns:
            dict: Keypoints for different body parts
        """
        keypoints = {
            'face': None,
            'body': None,
            'hands': None
        }
        
        # Detect body keypoints
        try:
            with self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5
            ) as pose:
                # Process the image
                results = pose.process(image)
                
                if results.pose_landmarks:
                    keypoints['body'] = {}
                    
                    # Extract relevant keypoints
                    h, w = image.shape[:2]
                    landmarks = results.pose_landmarks.landmark
                    
                    # Neck (approximated as midpoint between shoulders)
                    l_shoulder = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w,
                                          landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h])
                    r_shoulder = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * w,
                                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * h])
                    neck = (l_shoulder + r_shoulder) / 2
                    keypoints['body']['neck'] = neck
                    
                    # Shoulders
                    keypoints['body']['left_shoulder'] = l_shoulder
                    keypoints['body']['right_shoulder'] = r_shoulder
                    
                    # Chest (approximated as midpoint between shoulders and hips)
                    l_hip = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x * w,
                                     landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y * h])
                    r_hip = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x * w,
                                     landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y * h])
                    chest = (neck + (l_hip + r_hip) / 2) / 2
                    keypoints['body']['chest'] = chest
                    
                    # Wrists
                    l_wrist = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x * w,
                                       landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y * h])
                    r_wrist = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x * w,
                                       landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y * h])
                    keypoints['body']['left_wrist'] = l_wrist
                    keypoints['body']['right_wrist'] = r_wrist
                    
                    # Feet
                    l_ankle = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x * w,
                                       landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y * h])
                    r_ankle = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x * w,
                                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y * h])
                    keypoints['body']['left_foot'] = l_ankle
                    keypoints['body']['right_foot'] = r_ankle
        except Exception as e:
            st.warning(f"Body keypoint detection failed: {e}")
        
        # Detect face landmarks
        try:
            with self.mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                min_detection_confidence=0.5
            ) as face_mesh:
                # Process the image
                results = face_mesh.process(image)
                
                if results.multi_face_landmarks:
                    keypoints['face'] = {}
                    
                    # Extract face landmarks
                    h, w = image.shape[:2]
                    landmarks = results.multi_face_landmarks[0].landmark
                    
                    # Top of the head (approximated)
                    top_head_indices = [10, 152, 8]  # Points near the top of the head
                    top_head_points = []
                    for idx in top_head_indices:
                        top_head_points.append(np.array([landmarks[idx].x * w, landmarks[idx].y * h]))
                    top_head = np.mean(top_head_points, axis=0)
                    keypoints['face']['top'] = top_head
                    
                    # Chin (approximated)
                    chin_indices = [152, 175, 199]  # Points near the chin
                    chin_points = []
                    for idx in chin_indices:
                        chin_points.append(np.array([landmarks[idx].x * w, landmarks[idx].y * h]))
                    chin = np.mean(chin_points, axis=0)
                    keypoints['face']['chin'] = chin
                    
                    # Face center
                    face_center = (top_head + chin) / 2
                    keypoints['face']['center'] = face_center
                    
                    # Ears
                    left_ear = np.array([landmarks[234].x * w, landmarks[234].y * h])
                    right_ear = np.array([landmarks[454].x * w, landmarks[454].y * h])
                    keypoints['face']['left_ear'] = left_ear
                    keypoints['face']['right_ear'] = right_ear
                    
                    # Neck (if not already set from pose)
                    if keypoints['body'] is None or 'neck' not in keypoints['body']:
                        # Estimate neck position below the chin
                        neck_y_offset = (chin[1] - top_head[1]) * 0.3  # 30% of face height
                        neck = np.array([chin[0], chin[1] + neck_y_offset])
                        if keypoints['body'] is None:
                            keypoints['body'] = {}
                        keypoints['body']['neck'] = neck
        except Exception as e:
            st.warning(f"Face keypoint detection failed: {e}")
        
        return keypoints
    
    def _fit_clothing(self, avatar_image, clothing_img, clothing_mask, keypoints):
        """
        Fit clothing onto the avatar
        
        Args:
            avatar_image: Avatar image
            clothing_img: Clothing image
            clothing_mask: Clothing mask
            keypoints: Body keypoints
            
        Returns:
            numpy.ndarray: Avatar with clothing
        """
        # Create a copy of the avatar image
        result = avatar_image.copy()
        h, w = result.shape[:2]
        
        # If no body keypoints available, place at the center
        if keypoints.get('body') is None:
            return self._place_accessory_center(avatar_image, clothing_img, clothing_mask)
        
        # Get relevant keypoints for clothing placement
        body = keypoints['body']
        
        # Check if we have the shoulder points
        if 'left_shoulder' not in body or 'right_shoulder' not in body:
            # Fallback to center placement
            return self._place_accessory_center(avatar_image, clothing_img, clothing_mask)
        
        # Calculate the size and position of the clothing
        shoulder_width = np.linalg.norm(body['left_shoulder'] - body['right_shoulder'])
        
        # Scale the clothing based on shoulder width
        scale_factor = min(max(shoulder_width / clothing_img.shape[1] * 2.0, 0.5), 3.0)
        
        # Resize the clothing and its mask
        new_width = int(clothing_img.shape[1] * scale_factor)
        new_height = int(clothing_img.shape[0] * scale_factor)
        
        # Ensure minimum size
        new_width = max(new_width, 50)
        new_height = max(new_height, 50)
        
        # Resize both the image and mask
        try:
            clothing_resized = cv2.resize(clothing_img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            mask_resized = cv2.resize(clothing_mask, (new_width, new_height), interpolation=cv2.INTER_AREA)
        except Exception as e:
            st.warning(f"Error resizing clothing: {e}")
            return avatar_image
        
        # Calculate position (centered horizontally, with top near neck/chest)
        if 'neck' in body:
            center_x = int(body['neck'][0])
            center_y = int(body['neck'][1]) + int(new_height * 0.3)  # Place a bit below the neck
        else:
            # Fallback to using shoulders
            center_x = int((body['left_shoulder'][0] + body['right_shoulder'][0]) / 2)
            center_y = int((body['left_shoulder'][1] + body['right_shoulder'][1]) / 2) + int(new_height * 0.2)
        
        # Calculate the top-left corner for placement
        x1 = center_x - new_width // 2
        y1 = center_y - new_height // 2
        
        # Ensure the clothing stays within the image boundaries
        x1 = max(0, min(x1, w - new_width))
        y1 = max(0, min(y1, h - new_height))
        
        # Create region of interest (ROI) in the result image
        roi = result[y1:y1 + new_height, x1:x1 + new_width]
        
        # Check if ROI is valid
        if roi.shape[0] == 0 or roi.shape[1] == 0:
            return avatar_image
        
        # Create clothing with alpha channel if necessary
        if clothing_resized.shape[2] == 3:
            # Add alpha channel
            clothing_with_alpha = np.zeros((new_height, new_width, 4), dtype=np.uint8)
            clothing_with_alpha[:, :, :3] = clothing_resized
            clothing_with_alpha[:, :, 3] = mask_resized
            clothing_resized = clothing_with_alpha
        
        # Use the mask for blending
        alpha = mask_resized.astype(float) / 255
        alpha = np.expand_dims(alpha, axis=2)
        
        # For RGB channels
        for c in range(3):
            roi[:, :, c] = (1 - alpha[:, :, 0]) * roi[:, :, c] + alpha[:, :, 0] * clothing_resized[:, :, c]
        
        return result
    
    def _fit_jewelry(self, avatar_image, jewelry_img, jewelry_mask, keypoints):
        """
        Fit jewelry onto the avatar
        
        Args:
            avatar_image: Avatar image
            jewelry_img: Jewelry image
            jewelry_mask: Jewelry mask
            keypoints: Body keypoints
            
        Returns:
            numpy.ndarray: Avatar with jewelry
        """
        # Create a copy of the avatar image
        result = avatar_image.copy()
        h, w = result.shape[:2]
        
        # Try to get neck position from body keypoints
        neck_pos = None
        if keypoints.get('body') is not None and 'neck' in keypoints['body']:
            neck_pos = keypoints['body']['neck']
        # If no neck from body, try to get from face keypoints
        elif keypoints.get('face') is not None and 'chin' in keypoints['face']:
            # Approximate neck position below the chin
            chin = keypoints['face']['chin']
            if keypoints.get('face', {}).get('top') is not None:
                face_height = np.linalg.norm(keypoints['face']['chin'] - keypoints['face']['top'])
                neck_y_offset = face_height * 0.3
            else:
                neck_y_offset = 30  # Default offset
            neck_pos = np.array([chin[0], chin[1] + neck_y_offset])
        
        # If no neck position found, place jewelry at the center
        if neck_pos is None:
            return self._place_accessory_center(avatar_image, jewelry_img, jewelry_mask)
        
        # Scale the jewelry based on the face/body size
        scale_factor = 1.0
        if keypoints.get('face') is not None and 'left_ear' in keypoints['face'] and 'right_ear' in keypoints['face']:
            face_width = np.linalg.norm(keypoints['face']['left_ear'] - keypoints['face']['right_ear'])
            scale_factor = min(max(face_width / jewelry_img.shape[1] * 0.8, 0.5), 2.0)
        
        # Resize the jewelry and its mask
        new_width = int(jewelry_img.shape[1] * scale_factor)
        new_height = int(jewelry_img.shape[0] * scale_factor)
        
        # Ensure minimum size
        new_width = max(new_width, 30)
        new_height = max(new_height, 30)
        
        try:
            jewelry_resized = cv2.resize(jewelry_img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            mask_resized = cv2.resize(jewelry_mask, (new_width, new_height), interpolation=cv2.INTER_AREA)
        except Exception as e:
            st.warning(f"Error resizing jewelry: {e}")
            return avatar_image
        
        # Calculate position (centered horizontally at neck)
        center_x = int(neck_pos[0])
        center_y = int(neck_pos[1])
        
        # Calculate the top-left corner for placement
        x1 = center_x - new_width // 2
        y1 = center_y - new_height // 3  # Place the top 1/3 at the neck position
        
        # Ensure the jewelry stays within the image boundaries
        x1 = max(0, min(x1, w - new_width))
        y1 = max(0, min(y1, h - new_height))
        
        # Create region of interest (ROI) in the result image
        roi = result[y1:y1 + new_height, x1:x1 + new_width]
        
        # Check if ROI is valid
        if roi.shape[0] == 0 or roi.shape[1] == 0:
            return avatar_image
        
        # Create jewelry with alpha channel if necessary
        if jewelry_resized.shape[2] == 3:
            # Add alpha channel
            jewelry_with_alpha = np.zeros((new_height, new_width, 4), dtype=np.uint8)
            jewelry_with_alpha[:, :, :3] = jewelry_resized
            jewelry_with_alpha[:, :, 3] = mask_resized
            jewelry_resized = jewelry_with_alpha
        
        # Use the mask for blending
        alpha = mask_resized.astype(float) / 255
        alpha = np.expand_dims(alpha, axis=2)
        
        # For RGB channels
        for c in range(3):
            roi[:, :, c] = (1 - alpha[:, :, 0]) * roi[:, :, c] + alpha[:, :, 0] * jewelry_resized[:, :, c]
        
        return result
    
    def _fit_shoes(self, avatar_image, shoes_img, shoes_mask, keypoints):
        """
        Fit shoes onto the avatar
        
        Args:
            avatar_image: Avatar image
            shoes_img: Shoes image
            shoes_mask: Shoes mask
            keypoints: Body keypoints
            
        Returns:
            numpy.ndarray: Avatar with shoes
        """
        # Create a copy of the avatar image
        result = avatar_image.copy()
        h, w = result.shape[:2]
        
        # If no body keypoints available, place at the bottom center
        if keypoints.get('body') is None or 'left_foot' not in keypoints['body'] or 'right_foot' not in keypoints['body']:
            # Place at bottom center
            return self._place_accessory_bottom(avatar_image, shoes_img, shoes_mask)
        
        # Get foot positions
        left_foot = keypoints['body']['left_foot']
        right_foot = keypoints['body']['right_foot']
        
        # Calculate the distance between feet
        feet_distance = np.linalg.norm(left_foot - right_foot)
        
        # Scale the shoes based on the feet distance
        scale_factor = min(max(feet_distance / shoes_img.shape[1] * 1.5, 0.5), 3.0)
        
        # Resize the shoes and mask
        new_width = int(shoes_img.shape[1] * scale_factor)
        new_height = int(shoes_img.shape[0] * scale_factor)
        
        # Ensure minimum size
        new_width = max(new_width, 50)
        new_height = max(new_height, 30)
        
        try:
            shoes_resized = cv2.resize(shoes_img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            mask_resized = cv2.resize(shoes_mask, (new_width, new_height), interpolation=cv2.INTER_AREA)
        except Exception as e:
            st.warning(f"Error resizing shoes: {e}")
            return avatar_image
        
        # Calculate the position (center between feet)
        center_x = int((left_foot[0] + right_foot[0]) / 2)
        center_y = int((left_foot[1] + right_foot[1]) / 2) + int(0.1 * new_height)  # Slightly below feet points
        
        # Calculate the top-left corner for placement
        x1 = center_x - new_width // 2
        y1 = center_y - new_height // 2
        
        # Ensure the shoes stay within the image boundaries
        x1 = max(0, min(x1, w - new_width))
        y1 = max(0, min(y1, h - new_height))
        
        # Create region of interest (ROI) in the result image
        roi = result[y1:y1 + new_height, x1:x1 + new_width]
        
        # Check if ROI is valid
        if roi.shape[0] == 0 or roi.shape[1] == 0:
            return avatar_image
        
        # Create shoes with alpha channel if necessary
        if shoes_resized.shape[2] == 3:
            # Add alpha channel
            shoes_with_alpha = np.zeros((new_height, new_width, 4), dtype=np.uint8)
            shoes_with_alpha[:, :, :3] = shoes_resized
            shoes_with_alpha[:, :, 3] = mask_resized
            shoes_resized = shoes_with_alpha
        
        # Use the mask for blending
        alpha = mask_resized.astype(float) / 255
        alpha = np.expand_dims(alpha, axis=2)
        
        # For RGB channels
        for c in range(3):
            roi[:, :, c] = (1 - alpha[:, :, 0]) * roi[:, :, c] + alpha[:, :, 0] * shoes_resized[:, :, c]
        
        return result
    
    def _fit_watch(self, avatar_image, watch_img, watch_mask, keypoints):
        """
        Fit a watch onto the avatar
        
        Args:
            avatar_image: Avatar image
            watch_img: Watch image
            watch_mask: Watch mask
            keypoints: Body keypoints
            
        Returns:
            numpy.ndarray: Avatar with watch
        """
        # Create a copy of the avatar image
        result = avatar_image.copy()
        h, w = result.shape[:2]
        
        # If no body keypoints available, place at the left wrist area
        if keypoints.get('body') is None or 'left_wrist' not in keypoints['body']:
            # Place on the left side of the image
            return self._place_accessory_left_wrist(avatar_image, watch_img, watch_mask)
        
        # Get wrist position (default to left wrist)
        wrist_pos = keypoints['body']['left_wrist']
        
        # Scale the watch based on the body size
        scale_factor = 1.0
        if 'left_shoulder' in keypoints.get('body', {}) and 'right_shoulder' in keypoints.get('body', {}):
            shoulder_width = np.linalg.norm(keypoints['body']['left_shoulder'] - keypoints['body']['right_shoulder'])
            scale_factor = min(max(shoulder_width / watch_img.shape[1] * 0.25, 0.5), 2.0)
        
        # Resize the watch and mask
        new_width = int(watch_img.shape[1] * scale_factor)
        new_height = int(watch_img.shape[0] * scale_factor)
        
        # Ensure minimum size
        new_width = max(new_width, 30)
        new_height = max(new_height, 30)
        
        try:
            watch_resized = cv2.resize(watch_img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            mask_resized = cv2.resize(watch_mask, (new_width, new_height), interpolation=cv2.INTER_AREA)
        except Exception as e:
            st.warning(f"Error resizing watch: {e}")
            return avatar_image
        
        # Calculate position
        center_x = int(wrist_pos[0])
        center_y = int(wrist_pos[1])
        
        # Calculate the top-left corner for placement
        x1 = center_x - new_width // 2
        y1 = center_y - new_height // 2
        
        # Ensure the watch stays within the image boundaries
        x1 = max(0, min(x1, w - new_width))
        y1 = max(0, min(y1, h - new_height))
        
        # Create region of interest (ROI) in the result image
        roi = result[y1:y1 + new_height, x1:x1 + new_width]
        
        # Check if ROI is valid
        if roi.shape[0] == 0 or roi.shape[1] == 0:
            return avatar_image
        
        # Create watch with alpha channel if necessary
        if watch_resized.shape[2] == 3:
            # Add alpha channel
            watch_with_alpha = np.zeros((new_height, new_width, 4), dtype=np.uint8)
            watch_with_alpha[:, :, :3] = watch_resized
            watch_with_alpha[:, :, 3] = mask_resized
            watch_resized = watch_with_alpha
        
        # Use the mask for blending
        alpha = mask_resized.astype(float) / 255
        alpha = np.expand_dims(alpha, axis=2)
        
        # For RGB channels
        for c in range(3):
            roi[:, :, c] = (1 - alpha[:, :, 0]) * roi[:, :, c] + alpha[:, :, 0] * watch_resized[:, :, c]
        
        return result
    
    def _place_accessory_center(self, avatar_image, accessory_img, accessory_mask):
        """Place the accessory in the center of the avatar image"""
        # Create a copy of the avatar image
        result = avatar_image.copy()
        h, w = result.shape[:2]
        
        # Resize accessory to a reasonable size
        scale_factor = min(w / accessory_img.shape[1], h / accessory_img.shape[0]) * 0.5
        new_width = int(accessory_img.shape[1] * scale_factor)
        new_height = int(accessory_img.shape[0] * scale_factor)
        
        try:
            accessory_resized = cv2.resize(accessory_img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            mask_resized = cv2.resize(accessory_mask, (new_width, new_height), interpolation=cv2.INTER_AREA)
        except Exception as e:
            st.warning(f"Error resizing accessory: {e}")
            return avatar_image
        
        # Calculate center position
        x1 = (w - new_width) // 2
        y1 = (h - new_height) // 2
        
        # Create region of interest (ROI) in the result image
        roi = result[y1:y1 + new_height, x1:x1 + new_width]
        
        # Create accessory with alpha channel if necessary
        if accessory_resized.shape[2] == 3:
            # Add alpha channel
            accessory_with_alpha = np.zeros((new_height, new_width, 4), dtype=np.uint8)
            accessory_with_alpha[:, :, :3] = accessory_resized
            accessory_with_alpha[:, :, 3] = mask_resized
            accessory_resized = accessory_with_alpha
        
        # Use the mask for blending
        alpha = mask_resized.astype(float) / 255
        alpha = np.expand_dims(alpha, axis=2)
        
        # For RGB channels
        for c in range(3):
            roi[:, :, c] = (1 - alpha[:, :, 0]) * roi[:, :, c] + alpha[:, :, 0] * accessory_resized[:, :, c]
        
        return result
    
    def _place_accessory_bottom(self, avatar_image, accessory_img, accessory_mask):
        """Place the accessory at the bottom of the avatar image"""
        # Create a copy of the avatar image
        result = avatar_image.copy()
        h, w = result.shape[:2]
        
        # Resize accessory to a reasonable size
        scale_factor = min(w / accessory_img.shape[1], h / 4 / accessory_img.shape[0])
        new_width = int(accessory_img.shape[1] * scale_factor)
        new_height = int(accessory_img.shape[0] * scale_factor)
        
        try:
            accessory_resized = cv2.resize(accessory_img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            mask_resized = cv2.resize(accessory_mask, (new_width, new_height), interpolation=cv2.INTER_AREA)
        except Exception as e:
            st.warning(f"Error resizing accessory: {e}")
            return avatar_image
        
        # Calculate bottom-center position
        x1 = (w - new_width) // 2
        y1 = h - new_height - 10  # 10 pixels from bottom
        
        # Ensure the accessory stays within the image boundaries
        x1 = max(0, min(x1, w - new_width))
        y1 = max(0, min(y1, h - new_height))
        
        # Create region of interest (ROI) in the result image
        roi = result[y1:y1 + new_height, x1:x1 + new_width]
        
        # Create accessory with alpha channel if necessary
        if accessory_resized.shape[2] == 3:
            # Add alpha channel
            accessory_with_alpha = np.zeros((new_height, new_width, 4), dtype=np.uint8)
            accessory_with_alpha[:, :, :3] = accessory_resized
            accessory_with_alpha[:, :, 3] = mask_resized
            accessory_resized = accessory_with_alpha
        
        # Use the mask for blending
        alpha = mask_resized.astype(float) / 255
        alpha = np.expand_dims(alpha, axis=2)
        
        # For RGB channels
        for c in range(3):
            roi[:, :, c] = (1 - alpha[:, :, 0]) * roi[:, :, c] + alpha[:, :, 0] * accessory_resized[:, :, c]
        
        return result
    
    def _place_accessory_left_wrist(self, avatar_image, accessory_img, accessory_mask):
        """Place the accessory at the left wrist area"""
        # Create a copy of the avatar image
        result = avatar_image.copy()
        h, w = result.shape[:2]
        
        # Resize accessory to a reasonable size
        scale_factor = min(w / 6 / accessory_img.shape[1], h / 6 / accessory_img.shape[0])
        new_width = int(accessory_img.shape[1] * scale_factor)
        new_height = int(accessory_img.shape[0] * scale_factor)
        
        try:
            accessory_resized = cv2.resize(accessory_img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            mask_resized = cv2.resize(accessory_mask, (new_width, new_height), interpolation=cv2.INTER_AREA)
        except Exception as e:
            st.warning(f"Error resizing accessory: {e}")
            return avatar_image
        
        # Calculate left wrist position (approximated)
        x1 = w // 4 - new_width // 2  # Left quarter of the image
        y1 = 2 * h // 3  # Two thirds down the image
        
        # Ensure the accessory stays within the image boundaries
        x1 = max(0, min(x1, w - new_width))
        y1 = max(0, min(y1, h - new_height))
        
        # Create region of interest (ROI) in the result image
        roi = result[y1:y1 + new_height, x1:x1 + new_width]
        
        # Create accessory with alpha channel if necessary
        if accessory_resized.shape[2] == 3:
            # Add alpha channel
            accessory_with_alpha = np.zeros((new_height, new_width, 4), dtype=np.uint8)
            accessory_with_alpha[:, :, :3] = accessory_resized
            accessory_with_alpha[:, :, 3] = mask_resized
            accessory_resized = accessory_with_alpha
        
        # Use the mask for blending
        alpha = mask_resized.astype(float) / 255
        alpha = np.expand_dims(alpha, axis=2)
        
        # For RGB channels
        for c in range(3):
            roi[:, :, c] = (1 - alpha[:, :, 0]) * roi[:, :, c] + alpha[:, :, 0] * accessory_resized[:, :, c]
        
        return result