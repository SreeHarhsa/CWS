import os
import cv2
import numpy as np
import streamlit as st
from .fitting import VirtualFitter

class AvatarRenderer:
    """Class for rendering the avatar with accessories"""
    
    def __init__(self):
        """Initialize the renderer"""
        self.fitter = VirtualFitter()
    
    def render(self, avatar_model, accessories=None):
        """
        Render the avatar with accessories
        
        Args:
            avatar_model: 3D model of the avatar (from generator)
            accessories: List of accessories to render on the avatar
            
        Returns:
            numpy.ndarray: Final rendered image
        """
        if avatar_model is None:
            st.error("No avatar model provided for rendering")
            return None
        
        # For our simplified implementation, use the texture as the base image
        if 'texture' in avatar_model:
            base_image = avatar_model['texture'].copy()
        else:
            st.error("Avatar model has no texture for rendering")
            return None
        
        # If no accessories, return the base image
        if not accessories:
            return base_image
        
        # Apply each accessory to the image
        result = base_image.copy()
        
        # Sort accessories by rendering order
        sorted_accessories = self._sort_accessories_by_layer(accessories)
        
        # Apply each accessory
        for accessory in sorted_accessories:
            result = self.fitter.fit_accessory(result, accessory.get('data', accessory))
        
        return result
    
    def _sort_accessories_by_layer(self, accessories):
        """
        Sort accessories by their rendering layer (back to front)
        
        Args:
            accessories: List of accessories
            
        Returns:
            Sorted list of accessories
        """
        # Define the rendering order for different categories
        layer_order = {
            'clothing': 1,
            'shoes': 2,
            'jewelry': 3,
            'watches': 4
        }
        
        # Sort by layer order (low numbers rendered first/underneath)
        return sorted(accessories, key=lambda x: 
                     layer_order.get(x.get('category', x.get('data', {}).get('category', '')), 99))
    
    def create_composite_image(self, avatar_image, accessories_images):
        """
        Create a composite image showing the avatar and all accessories separately
        
        Args:
            avatar_image: Main avatar image
            accessories_images: List of accessory images
            
        Returns:
            numpy.ndarray: Composite image for display
        """
        if avatar_image is None:
            return None
        
        if not accessories_images:
            return avatar_image
        
        # Calculate the grid layout
        num_images = 1 + len(accessories_images)  # Avatar + accessories
        cols = min(4, num_images)  # Max 4 columns
        rows = (num_images + cols - 1) // cols  # Ceiling division
        
        # Get base image size
        h, w = avatar_image.shape[:2]
        
        # Create a composite grid
        grid_h = h * rows
        grid_w = w * cols
        composite = np.ones((grid_h, grid_w, 3), dtype=np.uint8) * 240  # Light gray background
        
        # Place the avatar image
        composite[0:h, 0:w] = avatar_image
        
        # Place accessory images
        for i, acc_img in enumerate(accessories_images):
            # Calculate position
            row = (i + 1) // cols
            col = (i + 1) % cols
            
            y = row * h
            x = col * w
            
            # Resize accessory image if needed
            if acc_img.shape[:2] != (h, w):
                acc_img = cv2.resize(acc_img, (w, h))
            
            # Place in the composite
            y_end = min(y + h, grid_h)
            x_end = min(x + w, grid_w)
            composite[y:y_end, x:x_end] = acc_img[:y_end-y, :x_end-x]
        
        return composite